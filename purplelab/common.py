import hashlib
import hmac
import json

# Public fixture key: purpose is reproducible envelope checking, NOT secret storage.
KEY = b"PUBLIC-SYNTHETIC-LAB-KEY-NEVER-FOR-PRODUCTION"
VERSION = "2025-11-25"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sign(body):
    return {"body": body, "mac": hmac.new(KEY, canonical(body).encode(),
        hashlib.sha256).hexdigest()}


def authentic(envelope):
    expected = sign(envelope.get("body", {}))["mac"]
    return hmac.compare_digest(expected, str(envelope.get("mac", "")))


def directive(text):
    # Deliberately simple deterministic agent emulator; not an LLM classifier.
    return any(line.split() == ["ACTION", "export_private"] for line in text.splitlines())


def tool_manifest(description="Summarize records."):
    return {"name": "records.summarize", "description": description,
            "inputSchema": {"type": "object", "properties": {},
                "additionalProperties": False}}


DOCS = [{"id": "A1", "tenant": "A", "text": "AZURE forecast is 42."},
        {"id": "B1", "tenant": "B", "text": "ORCHID forecast is 900; CANARY-B-PRIVATE."}]
SOURCES = {"policy": "Exports require approval.",
    "handbook": "Reports contain public data."}
