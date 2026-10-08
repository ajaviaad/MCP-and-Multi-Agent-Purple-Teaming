# Attribution and scope of license

The MIT license in this repository applies to its original source code and repository documentation. It does not grant rights to the separately supplied book, MITRE datasets, protocol specifications, model weights, or other referenced publications.

MITRE ATLAS technique identifiers and names are attributed to MITRE. The ATLAS data repository is distributed under the [Apache License 2.0](https://github.com/mitre-atlas/atlas-data/blob/main/LICENSE). No complete ATLAS dataset is bundled here. The versioned reference and mapping rationale are in [references](docs/references.md) and [scenarios](docs/scenarios.md).

PASTA refers to Process for Attack Simulation and Threat Analysis. The scenario designs and measurement rules are this project's application of the methodology, not an official PASTA certification or prescribed scoring formula. MCP specifications, Ollama, and GitHub Actions are external projects; this repository is not endorsed by them or by MITRE. Models downloaded separately remain subject to their own licenses.

No third-party Python code is vendored, and the core runtime has no third-party Python dependencies. The optional hosted CI downloads its specified actions and interpreter. The optional local model exercise requires a separately installed runtime and model.
