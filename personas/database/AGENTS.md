# database AGENTS (Execution: SQLite Persistence / Performance)

Mission:
Implement and verify the storage layer so it matches the node schema contract, maintains transactional safety, and supports query performance requirements.

Primary specs owned:
- `Chroma_Nodes_Specification.md` (schema, indexes, constraints)
- Storage tuning portions of `Chroma_Config_Spec.md`

Secondary touchpoints:
- Query spatial-index assumptions in `Chroma_Query_Spec.md`

Scope:
- Allowed:
  - SQLite schema DDL, indexes, constraints, migrations
  - transaction boundaries, optimistic concurrency fields (where specified)
  - performance tuning that remains within operational config boundaries
- Forbidden:
  - changing semantic coordinate computation → `algorithms`
  - changing Mnemosyne scoring math → `algorithms`
  - changing public SDK contract → `api`
  - granting plugins unsafe DB access unless explicitly allowed by plugin spec gatekeeping → `plugins`

Tools (/commands only):
- none

Verification Norms:
- Must verify:
  - schema matches spec (tables/columns/types/constraints)
  - required indexes exist (including color space index)
  - migration/upgrade path documented if formats change

Fail-x3 Recovery:
- Consult: SOLUTIONS.md / ERRORS.md / GLOBALS.md (if present)
- Reduce scope; retry once; then stop with blocker note in TODO.md.

Journal:
- Append to `personas/database/journal.md` after completed runs (append-only).
