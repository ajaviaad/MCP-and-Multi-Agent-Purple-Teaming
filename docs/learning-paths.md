# Learning paths

Both tracks start from the [README setup](../README.md) and end with a reviewable finding. All deterministic scenarios use synthetic data and the standard library. The [architecture](architecture.md) explains the historical protocol subset and its limits; the [verification record](verification.md) states what was actually executed for the book.

## Learner track

| Step | Activity | Evidence of understanding |
|---|---|---|
| 1. Establish a working baseline | Run the test suite and the full matrix from the README. Read one row and its constituent runs. | Explain why 96 executions are not 96 malicious or independent attack cases. |
| 2. Follow one boundary | Run [S01](scenarios.md#s01--indirect-retrieval-injection). Trace retrieved text → proposal → tool attempt → effect or denial. | Locate the vulnerable canary export and the hardened denial; explain why an unsafe proposal is not itself an export. |
| 3. Separate identity from content | Run [S03](scenarios.md#s03--audience-and-scope-authorization) and [S04](scenarios.md#s04--cross-tenant-retrieval). | Show one valid signature that lacks authorization and one record filtered by tenant. |
| 4. Inspect persistence and state | Run [S05](scenarios.md#s05--persistent-memory-poisoning), [S07](scenarios.md#s07--replay-and-idempotency), and [S12](scenarios.md#s12--approval-mismatch-and-stale-state). | Identify a real process restart, a cached receipt, and a resource version increment without claiming distributed safety. |
| 5. Compare remaining mechanisms | Run S02, S06, and S08–S11 using the [runbook](scenarios.md). | Name the distinct invariant for each; distinguish metadata integrity, delegation, path confinement, information class, budget, and evidence support. |
| 6. Write the decision | Fill the [campaign](../templates/campaign.json) and [finding](../templates/finding.md) templates using [measurement guidance](measurement.md). | Report raw counts, positive controls, limitations, one repair, and one meaningful retest. |

Read `cases.py` before changing it, then follow the relevant branch in `runner.py` and `server.py`. Make one reversible change in a working copy: add a new fixture through the existing `add(...)` pattern while preserving the original cases. A quoted benign instruction is a useful first boundary case. Record why it should be benign before running it. Keep the original verification results separate from your changed suite's results.

Do not change the expected result simply to make a test pass. Determine whether the fixture, control, or oracle is wrong. The [troubleshooting guide](troubleshooting.md) addresses environment and execution failures; those are different from demonstrated security outcomes.

## Experienced practitioner track

1. **Choose a business boundary.** Fill stages 1–3 of the campaign record using a real architecture represented by synthetic resources. Identify who can change content, who grants authority, and which state persists. Select a scenario because its mechanism fits that boundary, not because its ATLAS identifier is fashionable.
2. **Challenge the oracle.** Compare server events with an independent staging receipt or datastore observation. Deliberately distinguish proposal, acceptance, commit, rollback, and unresolved state. Where a judge is necessary, freeze its rubric and validate it against independently labeled cases.
3. **Extend the control test.** Add attacker-equivalent variants and benign edge cases. Test an ablation only in the isolated environment and retain an untouched evaluation set. Preserve tenant, task, budget, and initial state across paired conditions. For S07/S12, move the retest to the actual transaction boundary before making concurrency claims.
4. **Introduce model variability deliberately.** Use the [local model study](model-study.md) to observe S01 proposals without executing model-selected tools. Preserve model digest, settings, parse failures, and repetition structure. Results remain proposal measurements; do not combine them with committed-effect counts.
5. **Run an integration exercise.** Use [field exercises](field-exercises.md) to supply controlled inputs to an explicitly chosen workflow. Record separately what the fixture service delivered, what the model selected, and what the final service committed. Synthetic role headers do not establish real authentication.
6. **Close the operational gap.** Exercise revocation, cancellation, recovery, and evidence retention. Set acceptance with the business owner, including utility and unresolved outcomes. Document which new version or permission change will require another campaign.

## Keep the resulting artifacts distinct

Preserve the original regression suite and its evidence; store experimental variants, model outputs, and integration results in separately named campaign directories. A complete review bundle contains a filled campaign record, exact commands and versions, raw observations, calculation inputs if used, a finding, and the residual-risk decision. Archive unsuccessful attempts as well as the successful reproducer.

Completion means another engineer can reproduce the bounded claim and understand its limits. It does not require forcing an ATLAS mapping onto every defect, passing an arbitrary aggregate score, or claiming that a deterministic fixture establishes model security.
