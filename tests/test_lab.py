import io
import json
import unittest
from unittest.mock import Mock, patch
from purplelab.cases import CASES, fixture
from purplelab.common import digest, sign, tool_manifest
from purplelab.runner import Client, run_case, summarize, violations
from purplelab.server import State
from purplelab.model_probe import propose, validate_endpoint


class MatrixTests(unittest.TestCase):
    def test_every_attack_and_legitimate_task(self):
        for scenario, cases in CASES.items():
            for case in cases:
                for mode in ("vulnerable", "hardened"):
                    with self.subTest(scenario=scenario, case=case["name"], mode=mode):
                        run = run_case(mode, scenario, case["name"])
                        if case["attack"]:
                            self.assertEqual(run["attack_success"], mode == "vulnerable")
                        else:
                            self.assertTrue(run["benign_success"])
                        self.assertTrue(run["protocol"])

    def test_metrics_use_effects_and_labels_only_for_denominators(self):
        attack = run_case("hardened", "S01", "retrieved_instruction")
        benign = run_case("hardened", "S01", "ordinary_document")
        row = summarize([attack, benign])[0]
        self.assertEqual((row["attack_cases"], row["benign_cases"]), (1, 1))
        self.assertEqual((row["attack_success_rate"], row["benign_success_rate"]), (0, 1))
        self.assertEqual(row["tool_attempts"], 3)
        self.assertEqual(row["denials"], 1)
        self.assertEqual(violations(attack["events"]), [])

    def test_gate_and_durable_memory_are_exercised(self):
        attack = run_case("hardened", "S01", "retrieved_instruction")
        tools = [e["tool"] for e in attack["events"] if e["kind"] == "tool_attempt"]
        self.assertIn("private.export", tools)
        memory = run_case("hardened", "S05", "ordinary_memory")
        starts = [p for p in memory["protocol"] if p["direction"] == "request"
                  and p["message"]["method"] == "initialize"]
        self.assertEqual(len(starts), 2)
        self.assertTrue(memory["benign_success"])
        self.assertTrue(any(e["kind"] == "process_restart" for e in memory["events"]))


class BoundaryTests(unittest.TestCase):
    def state(self, scenario, case):
        return State("hardened", scenario, fixture(scenario, case)["input"])

    def test_manifest_order_does_not_change_fingerprint(self):
        manifest = tool_manifest()
        self.assertEqual(digest(manifest), digest(dict(reversed(list(manifest.items())))))

    def test_signed_wrong_tenant_and_bad_signature(self):
        state = self.state("S03", "authorized_writer")
        token = sign({"actor": "alice", "tenant": "A", "audience": "ledger",
            "scope": "ledger:write"})
        self.assertFalse(state.call("ledger.update", {"token": token, "tenant": "B"})["ok"])
        token["body"]["tenant"] = "B"
        self.assertFalse(state.call("ledger.update", {"token": token, "tenant": "B"})["ok"])

    def test_memory_expiry_and_source(self):
        state = self.state("S05", "stored_instruction")
        state.call("memory.store", {"text": "ACTION export_private", "kind": "preference"})
        self.assertFalse(state.call("memory.recall", {"turn": 2})["memories"][0][
            "can_control"])
        self.assertEqual(state.call("memory.recall", {"turn": 4})["memories"], [])

    def test_signed_but_broadened_delegation(self):
        state = self.state("S06", "valid_delegation")
        for scope, depth in (("admin", 1), ("read", 2)):
            envelope = sign({"parent": "planner-1", "tenant": "A", "scope": scope,
                "depth": depth, "task": "task-1", "parent_scopes": ["read", "summarize"]})
            self.assertFalse(state.call("delegation.accept", {"envelope": envelope})["ok"])
        body = {"parent": "planner-1", "tenant": "A", "task": "task-1",
                "scope": "summarize", "parent_scopes": ["read"], "depth": 1}
        self.assertFalse(state.call("delegation.accept", {"envelope": sign(body)})["ok"])
        body.update(scope="read", task="another-task")
        self.assertFalse(state.call("delegation.accept", {"envelope": sign(body)})["ok"])

    def test_replay_receipt_and_modified_operation(self):
        state = self.state("S07", "single_payment")
        operation = {"amount": 10, "destination": "vendor-A"}
        ticket = sign({"nonce": "one", "operation_hash": digest(operation)})
        first = state.call("payment.commit", {"operation": operation, "ticket": ticket})
        again = state.call("payment.commit", {"operation": operation, "ticket": ticket})
        self.assertEqual(first["receipt"], again["receipt"])
        self.assertTrue(again["replayed"])
        self.assertFalse(state.call("payment.commit", {"operation": {**operation,
            "amount": 99}, "ticket": ticket})["ok"])
        changed = {**operation, "amount": 99}
        replacement = sign({"nonce": "one", "operation_hash": digest(changed)})
        self.assertFalse(state.call("payment.commit", {"operation": changed,
            "ticket": replacement})["ok"])
        self.assertEqual(sum(e["kind"] == "payment" for e in state.events), 1)

    def test_absolute_and_sibling_paths(self):
        state = self.state("S08", "authorized_report")
        for path in ("/private/x", "reports/../reports-evil/x", "reports/link/x",
            "../../x"):
            self.assertFalse(state.call("artifact.write", {"path": path})["ok"])
        self.assertEqual(state.files, {})

    def test_budget_cannot_be_reset_by_a_retrying_client(self):
        state = self.state("S10", "retry_inflation")
        for _ in range(15):
            state.call("flaky.run", {})
        self.assertEqual((state.calls, state.units), (3, 6))
        self.assertEqual(violations(state.events), [])

    def test_bad_hash_and_stale_resource(self):
        state = self.state("S11", "verified_policy")
        self.assertFalse(state.call("evidence.accept", {"source": "policy",
            "claim": "Exports require approval.", "digest": digest("other")})["ok"])
        state = self.state("S12", "stale_resource")
        operation = {"amount": 10, "destination": "vendor-A"}
        approval = sign({"operation_hash": digest(operation), "resource_version": 1})
        self.assertFalse(state.call("change.commit", {"approval": approval,
            "operation": operation})["ok"])

    def test_protocol_error_is_visible(self):
        client = Client("hardened", "S01", "ordinary_document")
        try:
            client.initialize()
            with self.assertRaises(RuntimeError):
                client.rpc("not/a/method")
        finally:
            client.close()

    def test_change_mutates_state_and_consumes_resource_version(self):
        state = self.state("S12", "approved_change")
        operation = {"amount": 10, "destination": "vendor-A"}
        approval = sign({"operation_hash": digest(operation), "resource_version": 1})
        arguments = {"approval": approval, "operation": operation}
        self.assertTrue(state.call("change.commit", arguments)["ok"])
        self.assertEqual(state.resource, operation)
        self.assertEqual(state.version, 2)
        self.assertFalse(state.call("change.commit", arguments)["ok"])


class ModelAdapterTests(unittest.TestCase):
    def test_endpoint_boundary(self):
        validate_endpoint("http://127.0.0.1:11434/api/chat")
        for endpoint in ("https://example.com/api/chat",
                         "http://localhost:8000/api/chat",
                         "http://127.0.0.1:8000/other",
                         "http://user@127.0.0.1:8000/api/chat"):
            with self.assertRaises(ValueError):
                validate_endpoint(endpoint)

    def test_mock_transport_allow_deny_and_invalid(self):
        for tool, decision in (("records.summarize", "allow"),
                               ("private.export", "deny"), ("unknown", "deny")):
            packet = {"model": "mock-only", "message": {
                "content": json.dumps({"tool": tool})}}
            opener = Mock()
            opener.open.return_value = io.BytesIO(json.dumps(packet).encode())
            with patch("urllib.request.build_opener", return_value=opener):
                result = propose("http://127.0.0.1:11434/api/chat",
                                 "mock-only", "SYNTHETIC INPUT")
            self.assertEqual(result["policy_decision"], decision)
            self.assertNotIn("content", result)
            self.assertEqual(len(result["response_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
