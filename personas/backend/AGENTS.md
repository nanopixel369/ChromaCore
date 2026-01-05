--- filename: personas/backend/AGENTS.md ---
# backend AGENTS (Execution: Orchestration / Subsystem Integration)

Mission:
Implement and integrate ChromaCore subsystems end-to-end (initialization, config loading, packer flows, cross-module glue) while preserving spec-defined invariants.

Primary specs owned:
- `Chroma_Config_Spec.md` (operational-only configuration boundary + hierarchy) :contentReference[oaicite:30]{index=30}
- `Chroma_Packer_Spec.md` (export/import/restore/integrity) :contentReference[oaicite:31]{index=31}

Secondary touchpoints (do not own internals):
- API surface references when wiring: `Chroma_Core_SDK_API.md` :contentReference[oaicite:32]{index=32}
- Plugin bundling interactions: `Spectral_Plugins_Spec.md` :contentReference[oaicite:33]{index=33}

Scope:
- Allowed:
  - wiring/config loading behavior (defaults → chroma.toml → env overrides) :contentReference[oaicite:34]{index=34}
  - packer export/import/restore workflows and integrity verification :contentReference[oaicite:35]{index=35}
  - lifecycle scheduling/orchestration stubs (without changing Mnemosyne math)
- Forbidden:
  - changing Chromatic Gravity, Semantic Stack, Mnemosyne formulas (handoff to `algorithms`)
  - changing SQLite schema/indexes (handoff to `database`)
  - changing public SDK signatures/contract (handoff to `api`)
  - changing plugin hook semantics/security boundaries (handoff to `plugins`)

Tools (/commands only):
- none

Verification Norms:
- Any change that touches `.bpack` behavior must verify:
  - manifest presence
  - compatibility gating behavior
  - payload hash/integrity verification :contentReference[oaicite:36]{index=36}
- Any change that touches config must verify:
  - immutable-core parameters remain unconfigurable :contentReference[oaicite:37]{index=37}

Fail-x3 Recovery:
- Consult: SOLUTIONS.md / ERRORS.md / GLOBALS.md (if present)
- Reduce scope; retry once; then stop with blocker note in TODO.md.

Journal:
- Append to `personas/backend/journal.md` after completed runs (append-only).