# Security boundaries

## Intended use

This is a local teaching and regression-test repository. Its supplied attacks operate on synthetic records and explicitly vulnerable configurations. The original code is preserved so results can be compared with the book.

- Run the core exercise as an ordinary user in a directory you control. It launches local Python subprocesses and writes report files plus temporary memory data.
- Keep the field server on its built-in loopback binding. Do not put it behind a public proxy. The role header is deliberately forgeable, and the service has no real authentication or TLS.
- The printed HMAC key is a public fixture. It cannot protect a production credential, payment, or approval.
- The virtual path map does not demonstrate secure operating-system file access. Sequential in-memory transactions do not prove distributed atomicity or durable replay protection.
- The evidence evaluator trusts synthetic server events. A hostile production server needs an independent outcome observer.
- Model integration is optional. Keep the selected runtime genuinely local; loopback alone does not establish where a server performs inference. The supplied adapter records proposals without executing them.

Connecting real data, identities, networks, payment systems, or external tools changes the threat model and requires separate authorization and controls. [Architecture](docs/architecture.md) lists the boundaries demonstrated by each component.

## Reporting a defect

This ZIP is not a hosted project and has no monitored security contact. If you publish a maintained fork, configure a private reporting channel before inviting reports. Report unintended boundary escapes privately to that fork's maintainer. Supply a minimal synthetic reproduction, release version, operating system, Python version, observed effect, and expected boundary. Do not include live credentials or customer data.

An intended vulnerable-mode result is part of the exercise. A hardened-mode invariant failure on the published fixtures, a path escaping its declared sandbox in real filesystem operations, or unexpected external communication is a defect worth investigating.

## Dependency and release review

The local runtime is standard-library only. Hosted CI actions are pinned to full commits; review changes before updating pins. Retain the release checksum and original evidence when you create a variant. The manifest detects file changes but is unsigned and cannot establish who produced an archive.
