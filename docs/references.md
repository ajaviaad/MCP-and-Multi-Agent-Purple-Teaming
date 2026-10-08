# Reference register

The book's research and source-access baseline is **4 October 2026**. This companion was packaged on **8 October 2026** without claiming a new source review. Versioned URLs preserve the intended reference profile where available; mutable documentation and repository paths may change after that baseline. Book source identifiers are retained for traceability.

ATLAS names and identifiers come from **A02**, not the manifest. A laboratory-to-technique relationship is the author's analytical mapping, not MITRE endorsement or a claim that every element of a technique was reproduced. The content release is **2026.09** and the data-format version is **6.0.0**. The release manifest dates the release 15 September 2026; the associated changelog entry is dated 14 September. Those different metadata dates should not be silently treated as identical.

## Frameworks and taxonomy

<a id="a01"></a>
**A01 — MITRE ATLAS distribution manifest.** [Official repository manifest](https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/manifest.yaml). Mutable manifest used to identify release and format versions; it does not define technique titles.

<a id="a02"></a>
**A02 — MITRE ATLAS 2026.09 release data.** [Version-named release YAML](https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/v6/ATLAS-2026.09.yaml). Canonical source for the technique names, identifiers, and maturity labels used in the book and companion. The filename pins the content release, although the URL remains on the repository's mutable `main` branch.

<a id="a03"></a>
**A03 — MITRE ATLAS data changelog.** [Official changelog](https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/CHANGELOG.md). Establishes the September 2026 additions. Newly catalogued techniques are not necessarily newly invented behaviors; maturity labels are evidence categories rather than estimated compromise probabilities.

<a id="p01"></a>
**P01 — VerSprite, PASTA threat modeling.** [Framework overview from its co-originator](https://versprite.com/cybersecurity-listings/devsecops/pasta-threat-modeling/). Primary framework background for connecting business objectives, technical scope, decomposition, threats, weaknesses, attack simulation, and risk analysis. The companion's concrete metrics and acceptance criteria are application choices, not a claim that PASTA prescribes one universal numerical formula.

## MCP profiles

<a id="a05"></a>
**A05 — MCP versioning, 2026-07-28 documentation.** [Versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning). Baseline for explicit protocol version selection.

<a id="a06"></a>
**A06 — MCP architecture, 2026-07-28.** [Architecture](https://modelcontextprotocol.io/specification/2026-07-28/architecture). Reference architecture discussed by the book; not the profile implemented by the teaching runtime.

<a id="a07"></a>
**A07 — MCP tools, 2026-07-28.** [Tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools). Reference for tools, metadata, and their trust implications.

<a id="a08"></a>
**A08 — MCP authorization, 2026-07-28.** [Authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization). Reference for authorization at the protocol boundary. The repository does not implement OAuth or production token validation.

<a id="a09"></a>
**A09 — MCP security best practices, 2026-07-28 documentation.** [Security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices). Deployment guidance used by the book; the fixture service is intentionally narrower.

<a id="a11"></a>
**A11 — MCP change record, 2026-07-28.** [Protocol changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog). Source for the selected historical-to-reference-profile differences in [architecture.md](architecture.md).

<a id="a31"></a>
**A31 — MCP lifecycle, 2025-11-25.** [Historical lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle). Historical reference behind the core's initialization sequence.

<a id="a32"></a>
**A32 — MCP transports, 2025-11-25.** [Historical transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports). The core uses a limited stdio implementation and does not implement the complete transport specification.

<a id="a33"></a>
**A33 — MCP tools, 2025-11-25.** [Historical tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). Historical reference for the teaching subset's tool listing and invocation.

## Local model implementation

<a id="r02"></a>
**R02 — Ollama quickstart.** [Official quickstart](https://docs.ollama.com/quickstart). Mutable documentation. At the book's baseline it used `gemma4:e2b` as a local example, with an approximately 7.2 GB download and a recommendation of 8 GB available VRAM or unified memory. This is a documented example, not a security ranking or an October 8 revalidation.

<a id="r08"></a>
**R08 — Ollama chat API.** [Chat endpoint](https://docs.ollama.com/api/chat). Reference for the adapter's non-streamed chat request and JSON output mode. Runtime and model compatibility must be established on the reader's machine.

<a id="r09"></a>
**R09 — Ollama local model inventory API.** [List local models](https://docs.ollama.com/api/tags). Reference for recording the exact model digest before proposal requests.

## Further research behind the field exercises and defenses

<a id="a17"></a>
**A17 — CaMeL.** [Paper, version 2](https://arxiv.org/abs/2503.18813v2), 24 June 2025. Research on separating trusted control flow from untrusted data and enforcing capabilities.

<a id="a18"></a>
**A18 — CaMeL research implementation.** [Google Research repository](https://github.com/google-research/camel-prompt-injection). Research artifact with stated limitations; not a certification or a production guarantee.

<a id="a19"></a>
**A19 — OverThink.** [Paper, version 5](https://arxiv.org/abs/2502.02542v5), 17 September 2026. Resource-amplification research; reported multipliers are specific to evaluated conditions.

<a id="a20"></a>
**A20 — AttriGuard: Defeating Indirect Prompt Injection in LLM Agents via Causal Attribution of Tool Invocations.** [Paper, version 2](https://arxiv.org/abs/2603.10749v2), 10 June 2026. The record states acceptance at USENIX Security 2026. Counterfactual action attribution does not supply a universal production assurance claim.

<a id="a21"></a>
**A21 — ActGuard: Pre-execution Action Auditing against Indirect Prompt Injection in LLM Agents.** [Preprint](https://arxiv.org/abs/2609.14987), 14 September 2026. Recent pre-execution auditing research at the baseline, not independently established production assurance.

<a id="a22"></a>
**A22 — Manipulating Multimodal Agents via Cross-Modal Prompt Injection.** [CrossInject paper](https://arxiv.org/abs/2504.14348), submitted 19 April 2025. Motivates inspecting transformations between modalities. F03 is a visible synthetic fixture, not a reproduction of the paper's optimization method.

<a id="a23"></a>
**A23 — Microsoft Defender Security Research Team and Noam Kochavi, Manipulating AI memory for profit: The rise of AI Recommendation Poisoning.** [First-party research report](https://www.microsoft.com/en-us/security/blog/2026/02/10/ai-recommendation-poisoning/), 10 February 2026. Observed promotional attempts motivate integrity testing; the report does not establish a success rate for this repository's fixtures. Use A02 for the authoritative ATLAS names at the book's baseline.

## Weakness classifications used alongside ATLAS

These classify implementation weaknesses rather than replacing behavioral technique mappings:

- **A25 — CWE-22, Improper Limitation of a Pathname to a Restricted Directory:** [MITRE weakness entry](https://cwe.mitre.org/data/definitions/22.html).
- **A26 — CWE-367, Time-of-check Time-of-use Race Condition:** [MITRE weakness entry](https://cwe.mitre.org/data/definitions/367.html).
- **A27 — CWE-639, Authorization Bypass Through User-Controlled Key:** [MITRE weakness entry](https://cwe.mitre.org/data/definitions/639.html).

Return to [architecture](architecture.md), [field exercises](field-exercises.md), [model study](model-study.md), or the [README](../README.md).
