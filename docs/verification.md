# Release verification record

Release **1.0.0**, prepared **8 October 2026**, was checked locally with **Python 3.12.14** on **macOS 26.5.2, ARM64**. The book's research cutoff remains **4 October 2026**. This record describes teaching-code validation, not a production security certification.

## Checks completed

| Check | Observed result | Scope |
|---|---|---|
| Original listing comparison | 10 of 10 files byte-identical | Seven `purplelab` files, original test module, field fixture service and statistics utility; digests in [release metadata](../release.json) |
| Unit-test discovery | 45 methods passed | 15 original book tests, 15 field-route tests and 15 statistical utility tests |
| Field fixture self-test | Passed | Direct route and role-policy behavior; no bound network listener |
| Statistics demonstration | Passed | Constructed 100-pair example; expected rates, paired reduction, exact test and interval properties |
| Statistical example CSV | Output equals `--demo` | [Paired example](../examples/paired-outcomes.csv) is constructed data |
| Complete core CLI matrix | 96 executions passed | 12 scenarios × four fixtures × two configurations |
| Report reconciliation | Passed | 24 summary groups; JSON and CSV agree; 302 application events and 790 protocol records cover all executions |
| Packaged example reconciliation | Passed | Same assertions applied to the independently generated [example evidence](../examples/baseline/provenance.json) |
| Validator from another working directory | Passed | Absolute script path resolves the repository correctly; default output is temporary |
| Retained evidence protection | Passed | A nonempty `--output` directory is rejected without overwriting its contents |
| Integrity-checker negative cases | 16 expected outcomes passed | Valid, changed, missing, malformed, duplicate, traversal, absolute-path and symlink fixture cases |

The original reference files are intentionally unchanged. Additional tests and the validator are companion-repository additions. The optional model adapter's transport checks use mocks; no live model was downloaded or queried during release validation.

## Observed scenario totals

Each configuration contains 24 malicious and 24 benign executions. Attack success means that the scenario's prohibited synthetic effect occurred; benign success uses its positive-effect and no-violation predicate.

| Configuration | Malicious executions reaching the effect | Benign executions completing |
|---|---:|---:|
| Vulnerable | 24 / 24 | 24 / 24 |
| Hardened | 0 / 24 | 24 / 24 |

The matrix intentionally supplies known attacks and known policy branches. Its 100% and 0% endpoints demonstrate the regression expectations for those fixtures. They do not estimate a real model's susceptibility, attacker population success, or production residual risk. The [measurement guide](measurement.md) defines the distinctions.

## Reproduce the record

From the extracted repository root, use the selected virtual-environment interpreter. These examples use `python` as shorthand; see the operating-system-specific commands in [README](../README.md).

```sh
python scripts/verify_integrity.py
python scripts/validate.py
```

The integrity checker reads `SHA256SUMS`; it checks listed files and does not reject unrelated additional files. Its manifest is unsigned. Integrity passes before development and intentionally fails after listed files are modified.

To retain a new validation run instead of deleting temporary artifacts:

```sh
python scripts/validate.py --output results/release-check
```

Use a new or empty directory. The retained folder contains `validation.json`, stdout/stderr logs for every stage, `statistics_demo.json`, and `matrix/` with all three report files. The JSON record includes Python and operating-system details, stage exit statuses, test counts, reconciled totals and output-file digests. It also includes local executable and output paths; review it before sharing outside your team.

The validator exits nonzero on a stage or evidence-consistency failure. Timings are machine-dependent and are not a stable performance baseline. Read [troubleshooting](troubleshooting.md) before changing assertions.

## What remains unverified

- Hosted GitHub Actions jobs. The nine-job [CI matrix](ci.md) is configured but was not executed while preparing this ZIP.
- Linux and Windows execution. Their instructions are supplied and the code avoids platform-specific runtime dependencies, but the local record above is macOS only.
- Live Ollama interoperability, trained-model outcomes or end-to-end application susceptibility. Follow [model study](model-study.md) or [field exercises](field-exercises.md) to create separate observations.
- Full conformance to any MCP specification, OAuth verification, production tenant isolation, distributed idempotency, or transaction recovery.
- Changes to ATLAS, MCP, referenced research or model availability after the book's research cutoff.

An adaptation should record its own source revision, environment, conditions, observations and limitations. A successful teaching release is the beginning of an application-specific assessment, not its acceptance decision.
