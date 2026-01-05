# Workflow (Deterministic Agent Loop)

## Read Order (always)
1) `AGENTS.md`
2) `personas/<persona>/AGENTS.md` (based on task card metadata)
3) `WORKFLOW.md`
4) `TODO.md` (if selecting work)
5) `PLAN.md` (if multi-step)
6) `CHECKLIST.md`
7) `DECISIONS.md` / `REFLECTION.md` (as needed)

## Stages

### A) Clarify
- If critical primitives are missing (repo shape, commands, required constraints):
  - Ask up to **3 focused questions**, or
  - Use explicit placeholders (`{{...}}`) and proceed with harness-only work.

### B) Plan
- Produce a short plan (3–8 steps) using `PLAN.md` format.
- Each step must specify: output + verification.

### C) Execute
- Make the smallest viable change set.
- Do not broaden scope beyond the plan.
- Keep invariants intact (see `AGENTS.md` + relevant spec files).

### D) Verify
- Run verification commands **or** record explicit placeholders when commands are unknown.
- Update `CHECKLIST.md` only if harness rules change.

### E) Record
- Update `TODO.md` (check item; add done note).
- Append ADRs to `DECISIONS.md` if the change is irreversible/high-cost.
- Append a short note to `REFLECTION.md` (recommended) with verification + gotchas.
- Append to the active persona `journal.md` (required by persona contract).

## Fail-x3 Recovery
If blocked 3 times on the same subtask:
- Consult `SOLUTIONS.md` / `ERRORS.md` / `GLOBALS.md` (if present)
- Reduce scope to minimal reproducible step; retry once
- Stop and write a blocker entry into `TODO.md`
