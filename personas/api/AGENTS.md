# api AGENTS (Execution: Public SDK / API Contract)

Mission:
Implement and maintain the **public-facing API** (SDK contract) so it matches the spec and remains stable, well-validated, and predictable.

Primary specs owned:
- `Chroma_Core_SDK_API.md`
- Public-facing query contract portions of `Chroma_Query_Spec.md`

Scope:
- Allowed:
  - SDK class/method signatures and parameter semantics
  - error/exception taxonomy and return formats
  - API-facing docs/examples and compatibility notes
- Forbidden:
  - changing algorithm internals (Gravity/Mnemosyne/Stack) → `algorithms`
  - changing DB schema/indexes → `database`
  - changing plugin hook semantics/boundaries → `plugins`

Tools (/commands only):
- none

Verification Norms:
- Any SDK change must include:
  - a contract check (tests or placeholder) for signature + behaviors
  - at least one example invocation aligned to spec

Fail-x3 Recovery:
- Consult: SOLUTIONS.md / ERRORS.md / GLOBALS.md (if present)
- Reduce scope; retry once; then stop with blocker note in TODO.md.

Journal:
- Append to `personas/api/journal.md` after completed runs (append-only).
