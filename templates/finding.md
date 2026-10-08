# Finding: REPLACE_WITH_FAILED_BOUNDARY

> Unexecuted template. Replace every placeholder; do not present illustrative text or expected outcomes as observations. The [measurement guide](../docs/measurement.md) defines counts and acceptance. Keep a completed copy with its [campaign record](campaign.json) and raw evidence.

| Field | Value |
|---|---|
| Finding / campaign ID | REPLACE |
| Status | Not evaluated |
| Scenario / case collection | REPLACE |
| First observed / last retested | REPLACE |
| Engineering owner | REPLACE |
| Business decision owner | REPLACE |
| Configuration / source digest | REPLACE |
| Research source snapshot | Book baseline: 4 October 2026; record any later source separately |

## Business consequence and legitimate use

**Useful task:** REPLACE with the authorized user outcome.

**Prohibited consequence:** REPLACE with the sensitive effect and affected resource or information class.

**Invariant:** REPLACE with one checkable statement about the boundary.

**Severity and rationale:** REPLACE with consequence, realistic access, exposure, and scope. Do not treat the ATLAS mapping or fixture success rate as a severity score.

## Threat and weakness

- Attacker control and preconditions: REPLACE.
- Entry surface and trust transition: REPLACE.
- Absent or ineffective control: REPLACE.
- ATLAS identifier, exact name, source snapshot, and observed mapping basis: REPLACE or explicitly state that no exact mapping is asserted.
- Evidence state: relevant hypothesis / supported weakness / demonstrated path. Select one and explain.

## Reproduction

Record the operating system, Python version, source identifier, case definitions, modes, initial state, budgets, and any model digest/settings. Preserve the original cases and label added variants.

```text
python -m purplelab run --mode both --scenario S01 --output results/REPLACE_CAMPAIGN_ID
```

The command above is an illustrative S01 selector. Replace the scenario and output path to match the actual finding. List any required preparation and exact input changes here: REPLACE.

**Expected authorized behavior:** REPLACE.

**Observed result:** NOT RUN. After execution, cite the case, mode, event sequence, and artifact path. Distinguish proposed, attempted, accepted, committed, rolled back, and unresolved states.

## Evidence and oracle

| Evidence | Location / record key | What it establishes | Limitation |
|---|---|---|---|
| Case and command | REPLACE | Controlled input and declared conditions | REPLACE |
| Protocol or host trace | REPLACE | Requested operation and response | Does not alone prove a business effect |
| Effect observation | REPLACE | REPLACE impact oracle | State whether the observer trusts the tested component |
| Benign control | REPLACE | Useful authorized behavior still works | REPLACE utility scope |
| Integrity manifest | REPLACE digest / version | Reproducible artifact identity | Does not establish semantic truth |

Avoid bearer credentials and real confidential content in the finding. Use synthetic markers or restricted evidence references. Count only event records when using `evidence.jsonl`; embedded protocol snapshots repeat prior events.

## Paired results and denominators

| Count | Baseline | Corrected |
|---|---:|---:|
| Malicious attempted | NOT RUN | NOT RUN |
| Malicious excluded under the declared rule | NOT RUN | NOT RUN |
| Malicious eligible | NOT RUN | NOT RUN |
| Confirmed successful | NOT RUN | NOT RUN |
| Confirmed unsuccessful | NOT RUN | NOT RUN |
| Unresolved | NOT RUN | NOT RUN |
| Benign eligible | NOT RUN | NOT RUN |
| Benign completed | NOT RUN | NOT RUN |
| Benign false blocks | NOT RUN | NOT RUN |
| Benign other failures or unresolved | NOT RUN | NOT RUN |

Eligible malicious runs = successful + unsuccessful + unresolved. State the pairing key and whether repeated observations share a source case. Describe every exclusion and unresolved outcome. False blocks require attribution to the control; they are not every benign non-completion.

**Primary metric:** REPLACE numerator, denominator, and result. For curated deterministic fixtures, report counts without claiming population inference.

**Statistical analysis, if justified:** REPLACE sampling unit, population, interval method, pairing, repeated-run treatment, input file, exact command, and output. Otherwise mark not applicable. Never combine the statistical demo's constructed counts with experimental evidence.

## Correction and causal explanation

**Failed boundary:** REPLACE.

**Implemented change and location:** REPLACE.

**Why this prevents the effect:** REPLACE with the enforced identity, capability, data, or state constraint. Explain why blocking the exact payload string is insufficient.

**Tradeoffs:** REPLACE with measured utility, latency, operational burden, or compatibility impact. Separate measured observations from anticipated effects.

## Retest and recovery

| Required check | Case / evidence | Result |
|---|---|---|
| Original reproducer | REPLACE | NOT RUN |
| Equivalent adversarial variant | REPLACE | NOT RUN |
| Neighboring boundary or alternate route | REPLACE | NOT RUN |
| Benign edge cases | REPLACE | NOT RUN |
| Untouched evaluation set, if generalization is claimed | REPLACE | NOT RUN / justified N/A |
| Concurrency, cancellation, or crash recovery, where relevant | REPLACE | NOT RUN / justified N/A |
| Containment, effect reconciliation, and safe resumption | REPLACE | NOT RUN / justified N/A |

For persistent-state findings, record which source and derived entries were invalidated and which legitimate state was preserved. For replay or approval findings, reconcile already committed actions before resuming or requesting approval again.

## Decision and residual risk

- Acceptance rule declared before evaluation: REPLACE metric, threshold, unresolved limit, utility requirement, and any inference assumptions.
- Rule outcome and supporting evidence: NOT EVALUATED.
- Residual failures and untested conditions: REPLACE.
- Business exposure assumptions: REPLACE; test ASR is not annual incident probability.
- Decision: open / corrected pending verification / accepted with constraints / closed within stated scope. Select only after evidence review.
- Approving owner and date: REPLACE.
- Expiration and reassessment triggers: REPLACE.
- Related findings and next action: REPLACE.

Closure applies to the stated invariant and configuration. Document exclusions plainly rather than asserting that a passed fixture suite establishes system-wide security.
