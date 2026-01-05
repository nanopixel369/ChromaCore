# ChromaCore Agent Harness

Mission:
Build and evolve **ChromaCore** as a deterministic semantic memory engine where **meaning is explicit and stable** and **memory is temporal**.

The **primary sources of truth are the component spec files** defined in this repository. Architecture summaries are contextual only. Specs define invariants, contracts, and required behaviors.

---

## Persona Activation (Task Card Metadata → Persona Folder)

Agents are activated by your prompt (task card).  
The **task card metadata must include a persona name**.

### Mandatory Routing Rule
1) Read `AGENTS.md` (this file).
2) Read the task card metadata and extract `persona`.
3) Load **only** `personas/<persona>/AGENTS.md` and files inside that folder.
4) Ignore all other personas completely.

If the persona folder does not exist:
- STOP and request correction, **or**
- Fall back to `task-author` to author a correct task card.

### Supported Persona Names
These names must match folder names exactly:

- `task-author`
- `backend`
- `api`
- `database`
- `plugins`
- `algorithms`
- `frontend`

---

## Read Order (Always)

1) `AGENTS.md`
2) `personas/<persona>/AGENTS.md`
3) `WORKFLOW.md`
4) `CHECKLIST.md`
5) `PLAN.md` (if multi-step)
6) `TODO.md` (if selecting work)
7) `DECISIONS.md` / `REFLECTION.md` (as needed)

---

## Global Invariants (Non-Negotiable)

- Deterministic meaning → coordinate mapping  
- Semantic coordinates are immutable once created  
- Memory lifecycle is directional (strengthen, decay, permanence, rot)  
- Persistence is disk-first; memory is for active operations only  
- Configuration is operational only and must not expose core math or physics  
- Plugins must not bypass invariants, mutate coordinates, or access storage unless explicitly allowed

Breaking an invariant requires:
- explicit verification
- an ADR entry in `DECISIONS.md`

---

## Spec Ownership Map (Routing Authority)

Use this map to determine **which persona owns which work**.

### algorithms
Owns:
- Semantic Stack generation and rules
- Chromatic Gravity coordinate computation and determinism
- Mnemosyne scoring, memory lifecycle math

### database
Owns:
- Node persistence schema
- SQLite indexes and constraints
- Transactional behavior and storage performance

### api
Owns:
- Public SDK and API contracts
- Method signatures, parameters, error semantics
- Public query interfaces

### plugins
Owns:
- Spectral Plugin system
- Hook semantics and execution rules
- Plugin API boundaries and safety enforcement

### backend
Owns:
- System orchestration and integration
- Configuration loading and enforcement
- Packer import/export/restore flows
- Cross-component glue (without owning internals)

### frontend
Owns:
- Client/UI/CLI layers that consume the SDK
- Integration examples and usage validation
- Placeholder scope until frontend specs exist

---

## Guardrails (Hard Rules)

- Do **not** invent repository commands, frameworks, paths, or APIs.
  - Use placeholders like `{{TEST_CMD}}` when unknown.
- Do **not** cross persona boundaries.
- Keep diffs minimal and reviewable.
- No randomness or time-based inputs in semantic computation.
- Plugins must never bypass core constraints.

---

## Repo Command Placeholders

These are intentionally undefined until the repo provides them:

- Build: `{{BUILD_CMD}}`
- Test: `{{TEST_CMD}}`
- Lint: `{{LINT_CMD}}`
- Typecheck: `{{TYPECHECK_CMD}}`

---

## Fail-x3 Recovery (Global)

If blocked on the same subtask **three times**:

1) Consult `SOLUTIONS.md`, `ERRORS.md`, or `GLOBALS.md` (if present)
2) Reduce scope to the smallest reproducible step
3) Retry once
4) Stop and write a blocker entry in `TODO.md` describing:
   - what was attempted
   - what failed
   - what information is missing

---

## Definition of Done (Global)

Work is complete only when:
- Declared outputs exist
- Verification is run or explicitly deferred with placeholders
- The related `TODO.md` item is checked with a completion note
- Any irreversible change is logged in `DECISIONS.md`
- An entry is appended to the active persona’s `journal.md`

This file is authoritative.
Do not weaken it.