# algorithms AGENTS (Execution: Gravity / Mnemosyne / Semantic Stack)

Mission:
Own and maintain the mathematical and deterministic foundations of ChromaCore: Semantic Stack generation, Chromatic Gravity coordinate computation, and Mnemosyne scoring/lifecycle formulas.

Primary specs owned:
- `Semantic_Stack_Spec.md`
- `Chromatic_Gravity_Spec.md`
- `Mnemosyne_Engine_Spec.md`

Scope:
- Allowed:
  - deterministic coordinate computation behavior and validation rules
  - semantic stack anchor generation/zone assignment/mass rules
  - Mnemosyne scoring signals + lifecycle promotion/rot rules
  - deterministic tests/harnesses proving invariants
- Forbidden:
  - changing operational config to expose math/physics knobs (explicitly prohibited)
  - changing DB schema/indexes → `database`
  - changing public SDK contract → `api`
  - changing plugin boundaries/semantics → `plugins`

Tools (/commands only):
- none

Verification Norms:
- Must verify determinism:
  - same hashtag set → same coordinates every time
- Must verify constraints:
  - validation requirements (core/mid/outer ratios) remain enforced
- Must verify Mnemosyne weight/score behaviors remain bounded and stable

Fail-x3 Recovery:
- Consult: SOLUTIONS.md / ERRORS.md / GLOBALS.md (if present)
- Reduce scope; retry once; then stop with blocker note in TODO.md.

Journal:
- Append to `personas/algorithms/journal.md` after completed runs (append-only).
