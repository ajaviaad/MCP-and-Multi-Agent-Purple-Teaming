"""Local JSON-RPC teaching server; historical MCP 2025-11-25 subset.

Only stdin/stdout are used. Artifact stores, payments and exports are in-memory.
This is intentionally not a complete MCP implementation or production server.
"""
import argparse
import json
import posixpath
import sys
from pathlib import Path
from .cases import fixture
from .common import DOCS, SOURCES, VERSION, authentic, digest, tool_manifest

TOOL_NAMES = ("records.summarize", "private.export", "ledger.update", "documents.search",
              "memory.store", "memory.recall", "delegation.accept", "payment.commit",
              "artifact.write", "report.export", "flaky.run", "evidence.accept",
                  "change.commit")


class State:
    def __init__(self, mode, scenario, data, memory_path=None):
        self.hardened = mode == "hardened"
        self.scenario, self.data = scenario, data
        self.events, self.memories, self.payments = [], [], {}
        self.memory_path = Path(memory_path) if memory_path else None
        if self.memory_path and self.memory_path.exists():
            self.memories = json.loads(self.memory_path.read_text(encoding="utf-8"))
        self.calls, self.units = 0, 0
        self.files = {}
        self.version = 2 if data.get("mutate") == "version" else 1
        self.resource = {"destination": "vendor-A", "amount": 0}

    def event(self, kind, **fields):
        self.events.append({"seq": len(self.events) + 1, "kind": kind, **fields})

    def deny(self, reason):
        self.event("denied", reason=reason)
        return {"ok": False, "reason": reason}

    def call(self, name, args):
        self.event("tool_attempt", tool=name)
        if name == "records.summarize":
            self.event("summary_data", fact="Revenue is 42.")
            return {"ok": True, "text": self.data.get("text", "Revenue is 42.")}
        if name == "private.export":
            if self.hardened:
                return self.deny("export is outside the user-approved summary capability")
            self.event("export", destination="synthetic-sink", classification="secret",
                       payload="CANARY-A-PRIVATE", origin=self.scenario)
            return {"ok": True, "receipt": "IN-MEMORY-ONLY"}
        if name == "ledger.update":
            token = args["token"]
            if not authentic(token):
                return self.deny("bad signature")
            grant = token["body"]
            if self.hardened and (grant["audience"] != "ledger" or
                    grant["scope"] != "ledger:write" or grant["tenant"] != args["tenant"]):
                return self.deny("audience, scope or tenant does not authorize this write")
            self.event("ledger_write", grant=grant, tenant=args["tenant"])
            return {"ok": True}
        if name == "documents.search":
            # Tenant comes from a server-side principal fixture, never the query.
            principal_tenant = self.data["tenant"]
            docs = [d for d in DOCS if args["query"].casefold() in d["text"].casefold()]
            if self.hardened:
                docs = [d for d in docs if d["tenant"] == principal_tenant]
            self.event("retrieval", principal_tenant=principal_tenant, documents=docs)
            return {"ok": True, "documents": docs}
        if name == "memory.store":
            self.memories.append({"text": args["text"], "kind": args["kind"],
                                  "source": "retrieval", "tenant": "A", "expires_turn": 3,
                                  "lineage": ["retrieved-fragment-1"]})
            if self.memory_path:
                self.memory_path.write_text(json.dumps(self.memories), encoding="utf-8")
            self.event("memory_saved", source="retrieval", created_turn=1, expires_turn=3)
            return {"ok": True}
        if name == "memory.recall":
            memories = [m for m in self.memories if m["expires_turn"] >= args["turn"]]
            self.event("memory_read", turn=args["turn"], count=len(memories),
                       lineage=[m["lineage"] for m in memories])
            return {"ok": True, "memories": [{**m, "can_control":
                    not self.hardened or (m["source"] == "user" and m[
                        "kind"] == "preference")}
                    for m in memories if m["tenant"] == "A"]}
        if name == "delegation.accept":
            envelope = args["envelope"]
            body = envelope["body"]
            parent_scopes = set(body["parent_scopes"])
            valid = (authentic(envelope) and body["parent"] == "planner-1" and
                     body["tenant"] == "A" and body["task"] == "task-1" and
                     parent_scopes <= {"read", "summarize"} and
                     {body["scope"]} <= parent_scopes and 0 <= body["depth"] <= 1)
            if self.hardened and not valid:
                return self.deny("delegation signature, parent, scope or depth invalid")
            self.event("delegation_accepted", valid_chain=valid, scope=body["scope"])
            return {"ok": True}
        if name == "payment.commit":
            ticket, operation = args["ticket"], args["operation"]
            if not authentic(ticket):
                return self.deny("invalid payment ticket")
            nonce = ticket["body"]["nonce"]
            if self.hardened:
                if ticket["body"]["operation_hash"] != digest(operation):
                    return self.deny("operation differs from ticket")
                if nonce in self.payments:
                    previous = self.payments[nonce]
                    if previous["operation_hash"] != digest(operation):
                        return self.deny("nonce was already bound to a different operation")
                    self.event("idempotent_replay", nonce=nonce)
                    return {"ok": True, "receipt": previous["receipt"], "replayed": True}
            receipt = "receipt-" + str(len([e for e in self.events if e[
                "kind"] == "payment"]) + 1)
            self.payments[nonce] = {"receipt": receipt, "operation_hash": digest(operation)}
            self.event("payment", nonce=nonce, operation_hash=digest(operation))
            return {"ok": True, "receipt": receipt, "replayed": False}
        if name == "artifact.write":
            lexical = posixpath.normpath(posixpath.join("/workspace", args["path"]))
            resolved = lexical.replace("/workspace/reports/link/", "/private/")
            if self.hardened and (not resolved.startswith("/workspace/reports/") or
                                  resolved == "/workspace/reports"):
                return self.deny("artifact escapes approved report root")
            self.files[resolved] = "SYNTHETIC REPORT"
            self.event("artifact_write", path=resolved)
            return {"ok": True, "path": resolved}
        if name == "report.export":
            # Labels arrive from the trusted data service in this teaching model.
            # A real implementation must preserve taint through transformations.
            fields = self.data["fields"]
            permitted = all(f["classification"] in ("public", "aggregate") for f in fields)
            if self.hardened and not permitted:
                return self.deny("export schema forbids secret-derived fields")
            self.event("export", destination="allowlisted-analytics", fields=fields,
                       classification="public" if permitted else "secret",
                           origin=self.scenario)
            return {"ok": True, "receipt": "IN-MEMORY-ONLY"}
        if name == "flaky.run":
            if self.hardened and self.calls >= 3:
                return self.deny("task tool budget exhausted")
            self.calls += 1
            self.units += 2
            success = self.calls > self.data["failures"]
            self.event("work", call=self.calls, units=2, success=success)
            return {"ok": success, "retry_hint": self.data["retry_hint"]}
        if name == "evidence.accept":
            known = SOURCES.get(args["source"])
            verified = known is not None and args["claim"] == known and args[
                "digest"] == digest(known)
            if self.hardened and not verified:
                return self.deny(
                    "claim does not match the retrieved source and content hash")
            self.event("answer", verified=verified, claim=args["claim"], source=args[
                "source"])
            return {"ok": True}
        if name == "change.commit":
            approval, operation = args["approval"], args["operation"]
            if not authentic(approval):
                return self.deny("invalid approval signature")
            body = approval["body"]
            matching = body["operation_hash"] == digest(operation)
            current = body["resource_version"] == self.version
            if self.hardened and not (matching and current):
                return self.deny(
                    "approval is bound to another operation or resource version")
            self.resource = dict(operation)
            self.version += 1
            self.event("change", approved_operation=matching, fresh_resource=current,
                       resource=self.resource, new_version=self.version)
            return {"ok": True}
        raise ValueError("unknown tool")

    def dispatch(self, request):
        method = request["method"]
        if method == "initialize":
            return {"protocolVersion": VERSION, "capabilities": {"tools": {}},
                    "serverInfo": {"name": "purplelab-teaching-subset", "version": "1.0"}}
        if method == "tools/list":
            manifest = tool_manifest(self.data.get("metadata", "Summarize records."))
            if self.data.get("reorder"):
                manifest = dict(reversed(list(manifest.items())))
            rest = [{"name": name, "description": "Synthetic local exercise tool.",
                     "inputSchema": {"type": "object"}} for name in TOOL_NAMES[1:]]
            return {"tools": [manifest, *rest]}
        if method == "tools/call":
            params = request["params"]
            value = self.call(params["name"], params.get("arguments", {}))
            # Every result carries a trace snapshot for the independent evaluator.
            value["events"] = list(self.events)
            return {"content": [{"type": "text", "text": json.dumps(value)}],
                    "isError": not value.get("ok", True)}
        raise ValueError("unsupported JSON-RPC method")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("vulnerable", "hardened"), required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--memory-file")
    options = parser.parse_args()
    data = fixture(options.scenario, options.case)["input"]
    state = State(options.mode, options.scenario, data, options.memory_file)
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            if "id" not in request:  # initialized notification has no response
                continue
            result = state.dispatch(request)
            response = {"jsonrpc": "2.0", "id": request["id"], "result": result}
        except (ValueError, KeyError, TypeError) as error:
            response = {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request,
                dict) else None,
                        "error": {"code": -32602, "message": str(error)}}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
