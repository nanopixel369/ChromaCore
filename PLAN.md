# Plan Format (Short + Verifiable)

Use this for any multi-step task.

1) Step: <what changes>
   Output: <file(s)/artifact(s)>
   Verify: <command/check> => <expected>

2) Step: <...>
   Output: <...>
   Verify: <...>

Stop condition:
- <what ends this plan; e.g., tests pass, checklist gates satisfied, docs updated>

Escalation:
- If blocked 3 times on the same step: consult `SOLUTIONS.md` / `ERRORS.md` / `GLOBALS.md` (if present),
  reduce scope to minimal reproducible step, retry once, then stop with a blocker note in `TODO.md`.
