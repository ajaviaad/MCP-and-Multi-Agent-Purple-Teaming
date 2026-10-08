# MCP and Multi-Agent Purple Teaming — Companion Repository

A runnable companion to *MCP and Multi Agent Purple Teaming: Generative AI attack simulation and defense using MITRE ATLAS and PASTA*.

**Release 1.0.0 · Python 3.11+ · Standard-library runtime · Learner to experienced practitioner**

Reproduce a control failure, inspect its observable effect, apply the supplied hardened mode, and compare the same cases. The repository contains the book's complete reference listings, operating guides, tests, measurement utilities, and editable campaign templates. No API key, paid service, GPU, or Python package installation is required for the core exercises.

## Start here

1. Extract the ZIP completely; do not run files from inside an archive viewer.
2. Open a terminal in the extracted `purple-teaming-companion` folder, where this README is located.
3. Follow the quick start for your operating system.
4. Read [learning paths](docs/learning-paths.md), then work through [S01](docs/scenarios.md).

The book's research baseline is **4 October 2026**, using ATLAS content release **2026.09**. This repository was packaged on **8 October 2026**. Its ten original Python files match the book listings; repository documentation and additional validation are new. Packaging does not constitute a new threat-intelligence update.

## Quick start

Install a maintained Python 3.11 or newer interpreter from [python.org](https://www.python.org/downloads/) or your organization's managed runtime. Python 3.12.14 on macOS is the locally verified release environment. Linux and Windows instructions are provided, with a CI matrix ready to check those environments when you upload the repository.

### macOS and Linux

Run these commands from the repository root:

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python scripts/verify_integrity.py
.venv/bin/python scripts/validate.py
.venv/bin/python -m purplelab run --mode both --scenario all --output results/first-run
```

### Windows PowerShell

This example selects an installed Python 3.12. Substitute another installed supported version if needed.

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe scripts/verify_integrity.py
.\.venv\Scripts\python.exe scripts/validate.py
.\.venv\Scripts\python.exe -m purplelab run --mode both --scenario all --output results/first-run
```

Using the virtual environment's executable directly avoids activation and execution-policy changes. No `pip install` command is needed. The validator uses temporary directories and does not call a model or start a public server. Its final status must be successful before you interpret exercise results.

**Expected baseline:** the complete matrix executes 96 deterministic cases: 12 scenarios × 4 fixtures × 2 modes. Vulnerable mode reaches 24 of 24 attack effects; hardened mode reaches 0 of 24. Both complete 24 of 24 benign fixtures. These are deliberately constructed regression cases, not a measured attack rate for a trained model. See the [verification record](docs/verification.md).

## Run your first purple-team exercise

Use the same interpreter as above. The following shorter examples use `python` to mean that selected virtual environment interpreter; substitute `.venv/bin/python` or `.\.venv\Scripts\python.exe` if you have not activated it.

```sh
python -m purplelab run --mode both --scenario S01 --output results/S01-baseline
```

Open `results/S01-baseline/summary.json`, then inspect `evidence.jsonl`. Follow the retrieved article through the proposed `private.export` call, the enforcement decision, and the synthetic export effect. In hardened mode the unsafe proposal still crosses the local JSON-RPC boundary and the server denies it. Confirm the benign summary case still works. Use the [scenario guide](docs/scenarios.md) for the exact control, evidence predicate, correction, and advanced retest for every scenario.

| Command option | Accepted values | Meaning |
|---|---|---|
| `--scenario` | `all`, `S01` through `S12` | Select the cases to execute |
| `--mode` | `vulnerable`, `hardened`, `both` | Select the policy configuration |
| `--output` | A directory path | Save the three report files |

A repeated run into the same output directory replaces its report files. Use a new directory for each recorded campaign. The process prints the number of cases and the resolved output path.

## What is included

| Area | Entry point | Purpose |
|---|---|---|
| Twelve core scenarios | [Scenario guide](docs/scenarios.md) | Injection, metadata drift, identity, tenancy, memory, delegation, replay, paths, exfiltration, budgets, evidence, approvals |
| Six field exercises | [Field guide](docs/field-exercises.md) | Response biasing, crafted links, multimodal triggers, cloaking, exposed services, capability discovery |
| Optional local model | [Model study](docs/model-study.md) | Observe tool proposals through Ollama; proposals are never executed |
| PASTA and scoring | [Measurement guide](docs/measurement.md) | Business invariants, denominators, evidence, corrective action, retest, statistical assumptions |
| Architecture | [Architecture and boundaries](docs/architecture.md) | Component responsibilities and the limits of the teaching implementation |
| Editable records | [Campaign template](templates/campaign.json), [finding template](templates/finding.md) | Plan an experiment and document remediation evidence |
| Operations | [Troubleshooting](docs/troubleshooting.md), [verification](docs/verification.md) | Diagnose setup problems and understand the recorded test scope |

## Results and evidence

Each core run writes:

- `summary.json`: result class, protocol profile, grouped metrics, and individual case outcomes.
- `summary.csv`: the grouped rows for review in a spreadsheet.
- `evidence.jsonl`: ordered application events and recorded JSON-RPC traffic, keyed by scenario, case, and mode.

[Packaged example results](examples/baseline/summary.json) come from a real local execution of this release. Timing values vary by machine. A policy denial is not automatically an attack detection; `elapsed_ms` includes process overhead; synthetic work units are not tokens or currency. The [measurement guide](docs/measurement.md) defines these distinctions.

For the statistical teaching example:

```sh
python decision_stats.py --demo
python decision_stats.py --csv examples/paired-outcomes.csv
```

The CSV is explicitly illustrative. Both commands use the book's constructed paired counts, not the deterministic suite's cases. Do not feed correlated repeats into an analysis that assumes independent sampled cases.

## Repository layout

```text
purple-teaming-companion/
├── README.md
├── LICENSE
├── NOTICE.md
├── SECURITY.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── release.json
├── SHA256SUMS
├── purplelab/                 # Original core and optional model adapter
├── field_server.py            # Original loopback-only field fixtures
├── decision_stats.py          # Original statistical utility
├── tests/                     # Book tests plus companion checks
├── scripts/                   # Validation and release-integrity check
├── docs/                      # Scenario, setup, measurement and operations guides
├── templates/                 # Editable campaign and finding records
├── examples/                  # Observed simulation evidence and illustrative CSV
└── .github/workflows/ci.yml    # GitHub-hosted validation matrix
```

## Compatibility and scope

The core server intentionally implements a small **historical MCP 2025-11-25 stdio subset**. The book separately discusses MCP 2026-07-28. This repository does not claim full MCP conformance, a current-protocol SDK, real OAuth verification, or a production multi-agent framework. See [architecture](docs/architecture.md) before adapting it.

Core effects are synthetic in-memory records, with temporary local storage for the memory exercise. The optional field server binds only to `127.0.0.1`; its `X-Lab-Role` header is a spoofable test selector, not authentication. The model adapter uses numeric loopback HTTP and never executes a proposed tool. Real-model inference was not performed for the release verification; adapter tests use mocked transport.

## Using Git and CI

The ZIP is a clean source snapshot without a `.git` directory, virtual environment, credentials, or machine-specific caches. To create your own local Git repository after extraction:

```sh
git init
git add .
git commit -m "Import purple teaming book companion 1.0.0"
```

The last command requires your own Git author configuration. Upload to a repository you control if you want hosted CI. The included workflow runs Python 3.11, 3.12 and 3.13 on Ubuntu, macOS and Windows, with read-only repository permissions and action revisions pinned to commits. It does not publish packages, deploy services, or run paid/model inference. Hosted CI has not been executed during ZIP preparation. See [CI provenance](docs/ci.md).

## Integrity, contributions and license

`SHA256SUMS` records release file digests. `scripts/verify_integrity.py` checks the listed files; modified files will intentionally fail after you begin development. This is an integrity check, not a cryptographic signature or proof of provenance. Verify the downloadable ZIP against its separately supplied checksum if needed.

Read [contribution guidance](CONTRIBUTING.md) before adding cases and [security boundaries](SECURITY.md) before connecting other systems. Original companion code and repository documentation are offered under the [MIT License](LICENSE); the book itself is a separate artifact. External standards and references retain their respective ownership, as recorded in [NOTICE](NOTICE.md).
