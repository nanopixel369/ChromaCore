# plugins AGENTS (Execution: Spectral Plugins System)

Mission:
Implement and enforce the Spectral Plugins system: hook semantics, safe Plugin API boundaries, compatibility behaviors, and security constraints.

Primary specs owned:
- `Spectral_Plugins_Spec.md`

Scope:
- Allowed:
  - plugin registration lifecycle, dependency validation, version gating
  - hook execution semantics (sequential/parallel/exclusive as specified)
  - plugin API boundary enforcement (no coordinate mutation; no raw SQL by default)
  - plugin config capture/compatibility interactions with backpack manifests
- Forbidden:
  - changing core physics (Gravity/Stack/Mnemosyne) → `algorithms`
  - changing DB schema except via the schema-extension mechanism defined in spec (still owned here, but must not alter core columns)
  - changing public SDK surface unless explicitly delegated → `api`

Tools (/commands only):
- none

Verification Norms:
- Must verify:
  - coordinate immutability enforcement for plugin operations
  - no direct SQL access unless explicitly enabled by declared escape hatch
  - hook ordering semantics where specified (e.g., pre_storage_filter sequential)

Fail-x3 Recovery:
- Consult: SOLUTIONS.md / ERRORS.md / GLOBALS.md (if present)
- Reduce scope; retry once; then stop with blocker note in TODO.md.

Journal:
- Append to `personas/plugins/journal.md` after completed runs (append-only).
