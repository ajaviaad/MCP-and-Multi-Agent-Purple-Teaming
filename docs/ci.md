# Continuous integration

The included [GitHub Actions workflow](../.github/workflows/ci.yml) is ready for a repository you control. It runs on pushes, pull requests, and manual dispatch. The release ZIP does not create a GitHub repository or execute a hosted workflow.

## Configuration

The matrix has nine combinations: Ubuntu, macOS and Windows GitHub-hosted runners, each with Python 3.11, 3.12 and 3.13. Every job invokes `python scripts/validate.py`. Jobs have a ten-minute timeout; at most three matrix jobs run concurrently. Repository permissions are limited to reading contents. Checkout does not persist Git credentials. No deployment, model download, package publication or model inference is configured.

The release was locally verified on macOS with Python 3.12.14. The other environments remain configured coverage until you run the workflow and inspect its results. The fixture field server's command-line self-test does not bind a network listener.

## Pinned actions

The action revisions were verified against their official release pages when preparing this archive on 8 October 2026:

| Action | Release | Pinned commit |
|---|---|---|
| `actions/checkout` | [v7.0.0](https://github.com/actions/checkout/releases/tag/v7.0.0) | `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0` |
| `actions/setup-python` | [v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0) | `5fda3b95a4ea91299a34e894583c3862153e4b97` |

A commit pin fixes the referenced action source. It does not freeze hosted runner images, Python patch releases or services outside the workflow. Review action updates before replacing these pins. The workflow deliberately uses the runner's chosen Python and the repository's standard-library-only code.

## Reading failures

Open the failed job and read the validator's stage name and diagnostic output. Reproduce locally with the same Python minor version:

```sh
python scripts/validate.py --output results/ci-reproduction
```

The output directory must be new or empty. Retained records include `validation.json`, individual command logs, the constructed statistics demo, and the complete scenario evidence. Review logs before sharing them: paths and environment details can identify a workstation.

A passing job demonstrates regression behavior for the included fixtures. It does not certify a production agent, a trained model, protocol conformance, or untested operating-system versions. The workflow does not run the release integrity check on each commit, because legitimate source edits change release digests. Rebuild `SHA256SUMS` when preparing a new release, as described in [contribution guidance](../CONTRIBUTING.md).
