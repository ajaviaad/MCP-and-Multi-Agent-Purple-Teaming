# Contributing

## Run the baseline first

Follow [README](README.md), then run `python scripts/validate.py` with your selected virtual environment interpreter. Review [architecture](docs/architecture.md) and [measurement](docs/measurement.md) before changing a result predicate.

The ten original book files are listed with their hashes in `release.json`. Preserve their behavior when preparing a book-compatible release. A deliberate behavior change needs a changelog entry, updated evidence and an explicit compatibility statement. Do not silently alter expected results to make a failing test pass.

## Add a useful case

1. Name the business invariant, attacker-controlled field, precondition and observable prohibited effect.
2. Find the existing scenario that owns that boundary. A new payload spelling usually belongs as a fixture there; a new trust boundary may justify a new scenario.
3. Add the malicious fixture and a matched legitimate control to `purplelab/cases.py`. Keep secrets, recipients and records synthetic.
4. Enforce policy at the component that commits the effect. Attack labels are evaluator metadata and must never be consumed by the policy decision.
5. Update the independent violation and positive-effect predicates only when the changed semantics require it. Add a regression that would fail without the correction.
6. Document the ATLAS identifier, source revision, exact versus contextual relationship, evidence fields, remediation owner and retest in the scenario guide.
7. Run all tests and the complete case matrix. Recalculate expected counts in the validator if the fixture population intentionally changes; retain the old release results for comparison.

Use the [campaign](templates/campaign.json) and [finding](templates/finding.md) templates for an assessment. Extensions involving stochastic models need their own sampling design; deterministic fixture passes do not establish model robustness.

## Keep changes reviewable

Prefer small, focused changes with a concrete before/after effect. Include the commands executed, platform, Python version, result population, and any limitations. Use descriptive names and standard-library features supported by Python 3.11. Never submit real tokens, raw private prompts or production event logs. Generated runs under `results/` are ignored; publish a curated example only after checking its contents.

## Release checklist

- Run the local validator from a fresh extracted directory, including a path containing spaces.
- Verify every relative documentation link and every JSON template.
- Check original-listing hashes and state any intended deviations.
- Record local and hosted-CI outcomes separately; do not claim a platform passed because it appears in a workflow matrix.
- Update `CHANGELOG.md`, `release.json`, example provenance and verification notes.
- Regenerate `SHA256SUMS` after all source/documentation edits, then create the ZIP without caches, `.git`, virtual environments or unrelated results.
- Extract that ZIP and rerun integrity verification and the validator.

The default workflow is intentionally read-only and has no deployment, publication or credentialed model step.
