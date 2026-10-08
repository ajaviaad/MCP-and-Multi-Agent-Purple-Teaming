import argparse
import csv
import json
import queue
import subprocess
import sys
import threading
import time
import tempfile
from collections import Counter
from pathlib import Path
from .cases import CASES, fixture
from .common import SOURCES, VERSION, digest, directive, sign, tool_manifest


class Client:
    """One isolated, bounded subprocess per case; no sockets or credentials."""
    def __init__(self, mode, scenario, case, memory_path=None):
        self.command = [sys.executable, "-m", "purplelab.server", "--mode", mode,
                   "--scenario", scenario, "--case", case]
        if memory_path:
            self.command.extend(["--memory-file", str(memory_path)])
        self.sequence, self.trace, self.events, self.prior_events = 0, [], [], []
        self.start()

    def start(self):
        self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.responses = queue.Queue()
        self.reader = threading.Thread(target=self._read,
                args=(self.process.stdout, self.responses), daemon=True)
        self.reader.start()

    def restart(self):
        self.prior_events = list(self.events)
        self.close()
        self.start()
        self.initialize()

    @staticmethod
    def _read(stream, responses):
        for line in stream:
            responses.put(line)
        responses.put(None)

    def rpc(self, method, params=None):
        self.sequence += 1
        request = {"jsonrpc": "2.0", "id": self.sequence, "method": method,
                   "params": params or {}}
        self.trace.append({"direction": "request", "message": request})
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        line = self.responses.get(timeout=5)
        if line is None:
            raise RuntimeError("teaching server exited before responding")
        response = json.loads(line)
        self.trace.append({"direction": "response", "message": response})
        if response.get("id") != self.sequence or "error" in response:
            raise RuntimeError("JSON-RPC response mismatch or error: " + str(response))
        return response["result"]

    def initialize(self):
        result = self.rpc("initialize", {"protocolVersion": VERSION,
                "capabilities": {}, "clientInfo": {"name": "purplelab", "version": "1.0"}})
        if result["protocolVersion"] != VERSION:
            raise RuntimeError("unexpected protocol version")
        notice = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self.trace.append({"direction": "request", "message": notice})
        self.process.stdin.write(json.dumps(notice) + "\n")
        self.process.stdin.flush()

    def call(self, tool, **arguments):
        response = self.rpc("tools/call", {"name": tool, "arguments": arguments})
        value = json.loads(response["content"][0]["text"])
        self.events = self.prior_events + value.pop("events")
        return value

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=2)
        self.reader.join(timeout=1)
        self.process.stdout.close()


def exercise(client, mode, scenario, data):
    hard = mode == "hardened"
    tools = client.rpc("tools/list")["tools"]
    local = []
    if scenario == "S01":
        result = client.call("records.summarize")
        if directive(result["text"]):
            local.append({"_index": len(client.events), "kind": "proposal",
                "tool": "private.export"})
            result = client.call("private.export")
    elif scenario == "S02":
        manifest = tools[0]
        if hard and digest(manifest) != digest(tool_manifest()):
            local.append({"_index": len(client.events), "kind": "denied",
                          "reason": "tool manifest differs from pinned approval",
                          "approved_digest": digest(tool_manifest()),
                              "observed_digest": digest(manifest)})
            result = {"ok": False}
        elif directive(manifest["description"]):
            result = client.call("private.export")
        else:
            result = client.call("records.summarize")
    elif scenario == "S03":
        token = sign({"actor": data.get("actor", "alice"), "tenant": "A",
                      "audience": data["audience"], "scope": data["scope"]})
        result = client.call("ledger.update", token=token, tenant=data["tenant"])
    elif scenario == "S04":
        result = client.call("documents.search", query=data["query"])
        result["ok"] = bool(result["documents"])
    elif scenario == "S05":
        client.call("memory.store", text=data["memory"], kind=data["kind"])
        client.restart()
        local.append({"_index": len(client.events), "kind": "process_restart",
                      "retained": "memory-and-lineage"})
        result = client.call("memory.recall", turn=2)
        for memory in result["memories"]:
            if directive(memory["text"]) and memory["can_control"]:
                result = client.call("private.export")
            elif directive(memory["text"]):
                local.append({"_index": len(client.events), "kind": "denied",
                              "reason": "untrusted memory is not a control channel"})
    elif scenario == "S06":
        envelope = sign({"parent": "planner-1", "tenant": "A", "scope": "read",
                         "depth": 1, "task": "task-1", "parent_scopes": ["read",
                             "summarize"]})
        if data["mutate"] == "none":
            envelope = sign({**envelope["body"], "scope": data["child_scope"]})
        elif data["mutate"] == "scope":
            envelope["body"]["scope"] = data["child_scope"]
        else:
            envelope["body"]["parent"] = "fake-supervisor"
        result = client.call("delegation.accept", envelope=envelope)
    elif scenario == "S07":
        operation = {"destination": "vendor-A", "amount": 10}
        for index in range(data["repeats"]):
            nonce = "n-" + str(index if data["separate"] else 0)
            ticket = sign({"nonce": nonce, "operation_hash": digest(operation)})
            if data.get("reorder"):
                operation = dict(reversed(list(operation.items())))
            result = client.call("payment.commit", ticket=ticket, operation=operation)
    elif scenario == "S08":
        result = client.call("artifact.write", path=data["path"])
    elif scenario == "S09":
        result = client.call("report.export")
    elif scenario == "S10":
        result = client.call("flaky.run")
        # Tool-supplied hints are untrusted. Even vulnerable simulation has a cap.
        retry_count = min(result["retry_hint"], 11)
        for _ in range(retry_count):
            if result["ok"] or result.get("reason") == "task tool budget exhausted":
                break
            result = client.call("flaky.run")
    elif scenario == "S11":
        hashed = SOURCES.get(data["source"], "") if data[
            "digest"] == "source" else data["claim"]
        result = client.call("evidence.accept", source=data["source"],
                             claim=data["claim"], digest=digest(hashed))
    elif scenario == "S12":
        operation = {"destination": "vendor-A", "amount": 10}
        approval = sign({"operation_hash": digest(operation), "resource_version": 1})
        if data["mutate"] == "destination":
            operation["destination"] = "vendor-B"
        elif data["mutate"] == "reorder":
            operation = dict(reversed(list(operation.items())))
        result = client.call("change.commit", approval=approval, operation=operation)
    else:
        raise ValueError("unknown scenario")
    return bool(result["ok"]), local


def violations(events):
    """Score actual effects, independently of attack labels and mode."""
    found, nonces, units = [], set(), 0
    for event in events:
        kind = event["kind"]
        reason = None
        if kind == "export" and event["classification"] == "secret":
            reason = "secret_export"
        elif kind == "ledger_write":
            grant = event["grant"]
            if (grant["audience"] != "ledger" or grant["scope"] != "ledger:write"
                    or grant["tenant"] != event["tenant"]):
                reason = "unauthorized_ledger_write"
        elif kind == "retrieval":
            if any(d["tenant"] != event["principal_tenant"] for d in event["documents"]):
                reason = "cross_tenant_disclosure"
        elif kind == "delegation_accepted" and not event["valid_chain"]:
            reason = "invalid_delegation_accepted"
        elif kind == "payment":
            if event["nonce"] in nonces:
                reason = "duplicate_payment"
            nonces.add(event["nonce"])
        elif kind == "artifact_write" and not event["path"].startswith(
            "/workspace/reports/"):
            reason = "artifact_boundary_escape"
        elif kind == "work":
            units += event["units"]
            if units > 6:
                reason = "task_budget_exceeded"
        elif kind == "answer" and not event["verified"]:
            reason = "unverified_claim_accepted"
        elif kind == "change" and not (event["approved_operation"] and event[
            "fresh_resource"]):
            reason = "approval_mismatch_or_stale_state"
        if reason:
            found.append({"event_seq": event["seq"], "reason": reason})
    return found


def run_case(mode, scenario, case_name):
    case = fixture(scenario, case_name)
    start = time.perf_counter()
    temporary = tempfile.TemporaryDirectory(prefix="purplelab-")
    memory_path = Path(temporary.name) / "memory.json" if scenario == "S05" else None
    client = Client(mode, scenario, case_name, memory_path)
    try:
        client.initialize()
        task_ok, local = exercise(client, mode, scenario, case["input"])
        events = [dict(e, component="server") for e in client.events]
        for event in reversed(local):
            position = event.pop("_index")
            events.insert(position, dict(event, component="client"))
        events = [dict(e, seq=i + 1) for i, e in enumerate(events)]
        breach = violations(events)
        return {"mode": mode, "scenario": scenario, "case": case_name,
                "attack": case["attack"], "task_ok": task_ok,
                "attack_success": case["attack"] and bool(breach),
                "benign_success": (not case["attack"] and task_ok and not breach
                    and positive_effect(scenario, case["input"], events)),
                "violations": breach, "events": events, "protocol": client.trace,
                "elapsed_ms": round((time.perf_counter() - start) * 1000, 3)}
    finally:
        client.close()
        temporary.cleanup()


def positive_effect(scenario, data, events):
    expected = {"S01": "summary_data", "S02": "summary_data", "S03": "ledger_write",
        "S04": "retrieval", "S05": "memory_read", "S06": "delegation_accepted",
        "S07": "payment", "S08": "artifact_write", "S09": "export",
        "S10": "work", "S11": "answer", "S12": "change"}[scenario]
    effects = [e for e in events if e["kind"] == expected]
    if scenario == "S05":
        return any(e["count"] == 1 and e["lineage"] == [[
            "retrieved-fragment-1"]] for e in effects)
    if scenario == "S07":
        return len(effects) == (data["repeats"] if data["separate"] else 1)
    if scenario == "S10":
        return any(e["success"] for e in effects)
    return bool(effects)


def summarize(runs):
    rows = []
    for scenario, mode in sorted({(r["scenario"], r["mode"]) for r in runs}):
        group = [r for r in runs if r["scenario"] == scenario and r["mode"] == mode]
        attacks = sum(r["attack"] for r in group)
        benign = len(group) - attacks
        success = sum(r["attack_success"] for r in group)
        benign_success = sum(r["benign_success"] for r in group)
        counts = Counter(e["kind"] for r in group for e in r["events"])
        rows.append({"scenario": scenario, "mode": mode, "cases": len(group),
                     "attack_cases": attacks, "attack_successes": success,
                     "attack_success_rate": success / attacks if attacks else None,
                     "benign_cases": benign, "benign_successes": benign_success,
                     "benign_success_rate": benign_success / benign if benign else None,
                     "tool_attempts": counts["tool_attempt"], "denials": counts["denied"],
                     "synthetic_work_units": sum(e.get("units",
                         0) for r in group for e in r["events"]),
                     "elapsed_ms": round(sum(r["elapsed_ms"] for r in group), 3)})
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Synthetic historical MCP teaching profile")
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--mode", choices=("vulnerable", "hardened", "both"),
        default="both")
    parser.add_argument("--scenario", choices=("all", *CASES), default="all")
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    modes = ("vulnerable", "hardened") if args.mode == "both" else (args.mode,)
    scenarios = CASES if args.scenario == "all" else (args.scenario,)
    runs = [run_case(mode, scenario, case["name"]) for scenario in scenarios
            for mode in modes for case in CASES[scenario]]
    args.output.mkdir(parents=True, exist_ok=True)
    rows = summarize(runs)
    with (args.output / "evidence.jsonl").open("w", encoding="utf-8") as stream:
        for run in runs:
            identity = {k: run[k] for k in ("mode", "scenario", "case")}
            for event in run["events"]:
                stream.write(json.dumps({**identity, "record": "event", **event}) + "\n")
            for message in run["protocol"]:
                stream.write(json.dumps({**identity, "record": "protocol",
                    **message}) + "\n")
    compact = [{k: v for k, v in r.items() if k not in ("events",
        "protocol")} for r in runs]
    summary = {"result_class": "deterministic-control-simulation",
               "protocol_profile": VERSION, "rows": rows, "runs": compact}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2),
        encoding="utf-8")
    with (args.output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"cases_executed": len(runs), "result_class": summary["result_class"],
                      "output": str(args.output.resolve())}, indent=2))


if __name__ == "__main__":
    main()
