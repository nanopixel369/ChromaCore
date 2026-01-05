--- filename: CHECKLIST.md ---
# Checklist (Harness + Code Gates)

### Harness Integrity
- [ ] `AGENTS.md` exists and defines:
  - [ ] persona activation via task card metadata → `personas/<persona>/AGENTS.md`
  - [ ] the supported persona names list
  - [ ] spec ownership map (who owns which spec files)
  - [ ] global invariants and guardrails
- [ ] Persona folders exist for all supported persona names:
  - [ ] `personas/task-author/`
  - [ ] `personas/backend/`
  - [ ] `personas/api/`
  - [ ] `personas/database/`
  - [ ] `personas/plugins/`
  - [ ] `personas/algorithms/`
  - [ ] `personas/frontend/`
- [ ] Each persona folder contains:
  - [ ] `AGENTS.md` with mission, scope (allowed/forbidden), and verification norms
  - [ ] `journal.md` (append-only) and journal protocol in AGENTS.md
- [ ] Personas do not overlap ownership without an explicit “handoff” rule.
- [ ] `WORKFLOW.md` is present and references `CHECKLIST.md` as the gate list.
- [ ] Fail-x3 recovery is present in `AGENTS.md` and each persona `AGENTS.md`.
- [ ] No invented repo commands: any unknown command is a placeholder `{{...}}`.

### Code Integrity (fill in repo-specific commands)
- [ ] Build: `{{BUILD_CMD}}`
- [ ] Test: `{{TEST_CMD}}`
- [ ] Lint: `{{LINT_CMD}}`
- [ ] Typecheck (if applicable): `{{TYPECHECK_CMD}}`

### Spec Integrity (project-specific)
- [ ] Tasks reference the correct spec file(s) and stay within that persona’s ownership.
- [ ] Changes to determinism/coordinate mapping include a deterministic verification hook.
- [ ] Changes to persistence formats include migration/compatibility note + verification.
- [ ] Plugin changes do not allow coordinate mutation or invariant bypass.

### Delivery Integrity (only if in scope)
- [ ] Versioning policy defined (or placeholder): `{{VERSIONING_POLICY}}`
- [ ] Release process defined (or placeholder): `{{RELEASE_PROCESS}}`