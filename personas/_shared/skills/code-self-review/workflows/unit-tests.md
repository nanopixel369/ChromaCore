# Unit Tests Verification Workflow

Purpose: Confirm unit tests ran successfully and the task card is ready to close.

<L1>
## Core Steps
1) Verify unit test command was executed and passed.
2) Confirm evidence is present (logs or reports).
3) Confirm all task-card steps are complete.
4) Record closeout and move to the next task card step.
</L1>

## Evidence Required
- Use `resources/verification-evidence.md` to confirm proof of unit test execution.
- Expected command: `{{TEST_CMD}}` (or the repo-defined unit test command).

## If Evidence Is Missing
- Instruct to run unit tests, capture output, then return to this step.

## Closeout
- Use `resources/task-closeout-checklist.md`.
