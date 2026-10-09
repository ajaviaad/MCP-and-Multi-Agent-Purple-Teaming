# MCP and Multi-Agent Purple Teaming

**Companion repository for _MCP and Multi Agent Purple Teaming: Generative AI attack simulation and defense using MITRE ATLAS and PASTA_.**

Reproduce a control failure, inspect the effect, apply a correction, and retest the same cases. This repository provides executable examples, scenario guides, evidence collection, measurement utilities, and campaign templates for learners and experienced security practitioners.

**Release 1.0.0 · Python 3.11+ · Standard-library core · Local simulations**

The core exercises need no API key, paid service, GPU, model download, or third-party Python package. You can follow the book or begin with the included [learning paths](docs/learning-paths.md).

## Install from GitHub

### 1. Prerequisites

Install Git and Python 3.11 or newer. Python 3.12 is a suitable choice for reproducing the recorded release environment. Check that both commands are available in your terminal before continuing.

### 2. Clone the repository

The following commands work in macOS/Linux terminals and Windows PowerShell:

```sh
git clone https://github.com/ajaviaad/MCP-and-Multi-Agent-Purple-Teaming.git
cd MCP-and-Multi-Agent-Purple-Teaming
```

Run all subsequent commands from the project root: the directory containing `README.md`, `purplelab/`, `scripts/`, and `docs/`. The guide links in this README are relative to that directory.

### 3. Prepare Python and verify the installation

**macOS or Linux**

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python scripts/verify_integrity.py
.venv/bin/python scripts/validate.py
.venv/bin/python -m purplelab run --mode both --scenario S01 --output results/S01-baseline
```

Ensure the displayed Python version is at least 3.11. If necessary, replace `python3` in the first two commands with your installed supported interpreter, such as `python3.12`.

**Windows PowerShell**

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe scripts/verify_integrity.py
.\.venv\Scripts\python.exe scripts/validate.py
.\.venv\Scripts\python.exe -m purplelab run --mode both --scenario S01 --output results/S01-baseline
```

These Windows commands select an installed Python 3.12 interpreter. Substitute another installed supported version if needed. Using the virtual environment's executable directly avoids activation and execution-policy changes.

There is no `pip install` step: the project runs directly from its source checkout. Wait for each verification command to finish successfully before continuing. The validator checks the supplied tests, field-fixture self-test, statistics example, and complete scenario matrix without contacting a model or starting a network listener.

The final command runs **eight S01 executions**: two attack fixtures and two benign fixtures in each mode. Open `results/S01-baseline/summary.json` for outcomes and `results/S01-baseline/evidence.jsonl` for the recorded decisions and effects.

## Run a purple-team campaign

For the complete matrix, run the command for your operating system:

```sh
# macOS / Linux
.venv/bin/python -m purplelab run --mode both --scenario all --output results/campaign-01
```

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m purplelab run --mode both --scenario all --output results/campaign-01
```

| Option | Accepted values | Purpose |
|---|---|---|
| `--scenario` | `all`, `S01` through `S12` | Select the scenario fixtures |
| `--mode` | `vulnerable`, `hardened`, `both` | Select the control configuration |
| `--output` | A directory path | Choose where to write reports |

Use a new output directory for each campaign. Reusing a directory **replaces its three core report files**.

The supplied full matrix has 96 executions: 12 scenarios × 4 fixtures × 2 modes. Its expected baseline is:

| Mode | Attack effects observed / attack cases | Benign tasks completed / benign cases |
|---|---:|---:|
| Vulnerable | 24 / 24 | 24 / 24 |
| Hardened | 0 / 24 | 24 / 24 |

These are constructed, deterministic regression cases. They establish the behavior of the supplied controls on those fixtures; they do not measure a trained model's attack success rate. See the [recorded verification](docs/verification.md) and [example evidence](examples/README.md).

## Scenarios and learning paths

Start with S01 and trace the retrieved article, the proposed `private.export` call, the authorization decision, and the synthetic export effect. Hardened mode rejects that call at the server boundary while allowing the legitimate summary task.

Then use the [scenario guide](docs/scenarios.md) for each scenario's setup, attack, defense, evidence predicate, and retest:

| Scenario | Control under examination |
|---|---|
| S01 — Indirect retrieval injection | Retrieved content must not authorize private export |
| S02 — Tool metadata poisoning and approval drift | Tool metadata must match its approved definition |
| S03 — Audience and scope authorization | Credentials must authorize the intended resource and operation |
| S04 — Cross-tenant retrieval | Retrieval must respect tenant boundaries |
| S05 — Persistent memory poisoning | Stored untrusted text must retain its provenance across a restart |
| S06 — Delegation provenance | A child task must stay within its authenticated delegation |
| S07 — Replay and idempotency | Repeated requests must not repeat a protected effect |
| S08 — Artifact path escape | An artifact destination must remain within the allowed virtual path |
| S09 — Secret payload at an approved sink | An allowed destination must not bypass payload checks |
| S10 — Retry amplification | Tool hints must not override the task's work budget |
| S11 — Unsupported claim with apparent authority | A claim must be supported by its cited evidence |
| S12 — Approval mismatch and stale state | Approval must bind to the exact action and resource version |

Learners can follow the [guided progression](docs/learning-paths.md). Experienced teams can begin with the [architecture and boundaries](docs/architecture.md), define their own business invariants, and extend the fixtures with fresh attack variants and legitimate controls.

## Measure, correct, and retest with PASTA

Use the [measurement guide](docs/measurement.md) to carry an experiment through PASTA's seven stages: objectives, technical scope, application decomposition, threat analysis, weakness analysis, attack modeling, and risk/impact analysis.

1. Copy the [campaign template](templates/campaign.json). Define the business outcome at risk, attacker-controlled input, permitted action, and observable failure condition. This is a planning record; the runner does not load it as configuration.
2. Run the vulnerable and hardened conditions against the same fixtures. Keep attack and benign cases separate, and retain the case identities and evidence.
3. Count a prohibited effect as attack success. Record legitimate completion separately so that blocking all work cannot appear to be a successful defense.
4. Use the [finding template](templates/finding.md) to document the cause, corrective action, owner, and evidence. Retest the original case, a fresh variant, and a legitimate control after making changes.

Each core run produces:

| File | Contents |
|---|---|
| `summary.json` | Result class, protocol profile, grouped metrics, and individual outcomes |
| `summary.csv` | Scenario/mode aggregates for spreadsheet review |
| `evidence.jsonl` | Application events and JSON-RPC traffic identified by scenario, case, and mode |

When counting effects, use evidence records with `record == "event"`; protocol responses also contain event snapshots and must not be counted again. A policy denial alone does not establish attack success or failure. Elapsed time includes process overhead, and synthetic work units are neither tokens nor currency.

For the statistical teaching example, use the commands below. Here and in the optional model example, replace `python` with `.venv/bin/python` on macOS/Linux or `.\.venv\Scripts\python.exe` on Windows.

```sh
python decision_stats.py --demo
python decision_stats.py --csv examples/paired-outcomes.csv
```

This example uses 100 constructed paired cases, with 30 baseline successes and two hardened successes. It is separate from the core matrix and any live-model observation. The utility expects `case_id,baseline_success,hardened_success` columns; the core `summary.csv` is not compatible input. See the measurement guide for sampling assumptions and interpretation of Wilson intervals, McNemar's test, and paired bootstrap results.

## Optional field exercises and model observations

The [six field exercises](docs/field-exercises.md) cover response biasing, crafted links, multimodal instruction transfer, cloaking, exposed service operations, and capability discovery. The guide supplies complete setup, requests, evidence requirements, corrective actions, and retests.

Their fixture service binds to `127.0.0.1:8766` and makes no outbound requests. Its `X-Lab-Role` header is a spoofable experiment selector. Hardened mode changes the F05/F06 role-policy decisions; F01–F04 retain hostile content so that you can test defenses in your own isolated application. The fixture service itself performs no model inference and implements no MCP endpoint.

The [optional model study](docs/model-study.md) uses an already configured local Ollama runtime to observe tool proposals for the four S01 fixtures. Obtain the exact installed model name with `ollama list`, then substitute it below:

```sh
python -m purplelab.model_probe --model EXACT_LOCAL_MODEL_NAME --repetitions 1 --output results/model-study/run-01.json
```

The adapter uses numeric loopback HTTP, defaults to `http://127.0.0.1:11434/api/chat`, and **never executes proposed tools**. Review parsing, proposed tool, and policy decision separately. This study is optional and is not a live-model evaluation of all twelve scenarios.

## Documentation and project layout

| Resource | Purpose |
|---|---|
| [Troubleshooting](docs/troubleshooting.md) | Interpreter, working-directory, execution, and report problems |
| [Verification record](docs/verification.md) | Recorded checks and the limits of the evidence |
| [CI documentation](docs/ci.md) | Automated validation configuration and provenance |
| [References](docs/references.md) | Research baseline, standards, and ATLAS sources |
| [Contribution guide](CONTRIBUTING.md) | Adding scenarios and submitting changes |

```text
MCP-and-Multi-Agent-Purple-Teaming/
├── README.md
├── purplelab/                 # Core scenarios and optional model adapter
├── field_server.py            # Local field-exercise fixtures
├── decision_stats.py          # Paired-outcome statistics
├── tests/                     # Core, field, and statistics tests
├── scripts/                   # Validation and integrity utilities
├── docs/                      # Operational and scenario guides
├── templates/                 # Campaign and finding records
├── examples/                  # Simulation evidence and illustrative data
├── .github/workflows/ci.yml   # Cross-platform validation configuration
├── release.json               # Release metadata and recorded verification
├── SHA256SUMS                 # Unsigned file digests
├── LICENSE
└── NOTICE.md
```

## Compatibility and verification scope

The book's research baseline is **4 October 2026**, using **ATLAS content release 2026.09**. Repository release 1.0.0 is dated **8 October 2026**. These dates identify the supplied material's research snapshot; they do not imply a continuous threat-intelligence update. The measurement workflow and scenario mappings are teaching applications of PASTA and ATLAS, not certification by either source.

The executable core implements a **historical MCP 2025-11-25 stdio teaching subset**. The book separately discusses MCP 2026-07-28. Before adapting the examples, read the architecture guide: this implementation does not provide full MCP conformance, real OAuth verification, or a production multi-agent security framework. The signing key is a public fixture; path containment uses a virtual map; the evaluator relies on server-reported events. Real integrations need authenticated identities and independent observation of resource effects.

The recorded release validation passed **45 tests and 96 scenario executions on macOS with Python 3.12.14**. CI is configured for Python 3.11, 3.12, and 3.13 on Ubuntu, macOS, and Windows; hosted CI was not executed as part of that recorded validation. Model transport was mocked, and no live inference results are claimed.

To retain your own validation evidence, run `scripts/validate.py --output results/release-check` with your virtual environment's Python. This output directory must be new or empty. Without `--output`, validation artifacts are temporary.

## Integrity and license

`scripts/verify_integrity.py` compares the release's listed files against `SHA256SUMS`. Intentional edits will fail that comparison until the corresponding digests are updated. The manifest is unsigned and does not authenticate the author.

Read the [security boundaries](SECURITY.md) before connecting other systems. Original companion code and repository documentation use the [MIT License](LICENSE). The book is a separate work; external standards and references retain their respective ownership, as described in [NOTICE](NOTICE.md).
