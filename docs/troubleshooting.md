# Troubleshooting and cleanup

Use the virtual environment executable shown in [README](../README.md). Commands below use `python` as shorthand for it. Run from the extracted repository root.

| Symptom | Likely cause | Action |
|---|---|---|
| `No module named purplelab` | Wrong working directory or incomplete extraction | Change to the folder containing `purplelab/` and this README; extract the complete ZIP |
| `python3` or `py` not found | Python is absent or not on PATH | Install an approved Python 3.11+ runtime and reopen the terminal |
| `venv` unavailable on a managed Linux image | Its venv component is not installed | Ask your system/package administrator for that interpreter's venv support; the scripts also run directly under an approved Python 3.11+ interpreter |
| PowerShell blocks activation | Local execution policy | Use `.\.venv\Scripts\python.exe` directly; activation is unnecessary |
| Subprocess timeout | Slow or blocked process launch, or a child exception | Check the working directory and interpreter; run `python -m unittest discover -s tests -v`; a timeout is not proof of attack prevention |
| Integrity verification reports changes | Edited, corrupted, or normalized release files | Compare with a fresh extraction; after intentional development, compare Git changes instead of expecting the release manifest to pass |
| Field-server address already in use | Another listener owns 127.0.0.1:8766 | Stop the field server you started; do not terminate an unidentified process |
| `/config` returns 403 in hardened mode | Expected role restriction | Send synthetic operator role for the authorized control; do not relabel the anonymous denial a service error |
| `ollama` connection refused | Optional service is stopped | Follow the [model guide](model-study.md); the core suite does not need Ollama |
| Model identity preflight fails | Missing exact local tag or digest | Inspect `ollama list`; use its exact installed model name |
| Model row is `error` or `invalid` | Transport, timeout, parsing or unexpected structure | Keep these rows separate; warm the model and inspect the local runtime before repeating |
| Counts differ after adding a fixture | The evaluation population changed | Record the new denominator and update the expected fixture matrix deliberately |

## Inspect a failure without changing its meaning

Keep the failed output directory. Identify scenario, case and mode in `summary.json`; use the same identifiers to find events in `evidence.jsonl`. Check the first unexpected proposal, the enforcement decision and the resulting effect. Confirm that the matching benign control still completes. A transcript that looks alarming is not itself a committed effect.

A failure in the validator returns a nonzero exit code. Read the step that failed; do not bypass it by removing its assertion. The field routing tests do not launch a socket server, and mocked adapter tests do not require a model.

## Cleanup

1. Stop a field server started in your terminal with Ctrl-C.
2. Complete outstanding optional model requests, then stop a manually started `ollama serve` process with Ctrl-C if you no longer need it.
3. Archive the campaign and its evidence before removing unwanted run folders through your file manager.
4. Remove the repository's `.venv` if you no longer need that environment. No system-wide Python packages were installed by the quick start.

Core S05 memory lives in temporary per-case directories and is cleaned up by the runner. Report files persist until you remove them. Field-service events append to the selected JSONL file, while its mutable record state resets at restart. Reusing a core output path replaces its three report files; choose fresh paths for retained comparisons.
