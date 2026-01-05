---
name: code-self-review
tier: journeyman
description: Final self-review of task card completion and verification evidence before closing a coding task.
version: 0.1.0
author: ChromaCore
created: 2026-01-04
evo_pair: evolutionary/SKILL.md
triggers:
  keywords: [code-self-review, self-review, final review, task closeout]
  intent_patterns: ["\\$code-self-review", "self review", "close task card"]
---


# code-self-review

Routes to the correct verification workflow (tests, lint, typecheck, build, or manual) and confirms the task card is fully complete before closeout.

<essential_principles>
## Core Concepts

This skill verifies that all required validation steps actually ran, that evidence exists, and that every task-card step is complete before marking work done.

### Key Terminology

- Task card: the checklist of work and verification steps
- Verification type: how correctness was checked (tests/lint/typecheck/build/manual)
- Evidence: logs, outputs, or files that prove verification ran
- Closeout: marking the task complete and moving to the next item

### When to Use This Skill

Use after code changes are implemented and any required verification has been executed.

### Quality Standards

- No missing task-card steps
- Verification evidence is present and matches the chosen workflow
- Closeout is recorded clearly
</essential_principles>


<intake_validation>
## When to Use This Skill

This skill should be invoked when:
- Final review step after code changes
- When a task card requires verification before completion

**Input Requirements:**
- Task card with steps and verification requirements
- Evidence of verification (command output, logs, or files)

**Prerequisites:**
- Implementation work completed
- Verification already executed (or ready to execute now)

**Not Suitable For:**
- Running the actual tests or linting from scratch
- Replacing in-depth code review
</intake_validation>


<intake>
## What would you like to do?

Which verification method was used for this task? Choose the matching workflow.

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
unit tests, unit, pytest | workflows/unit-tests.md
integration tests, integration | workflows/integration-tests.md
lint, linting | workflows/lint.md
typecheck, type check | workflows/typecheck.md
build | workflows/build.md
manual, checklist | workflows/manual-checklist.md
</routing>

<resource_index>
## Available Resources

**Workflows:**
- workflows/unit-tests.md
- workflows/integration-tests.md
- workflows/lint.md
- workflows/typecheck.md
- workflows/build.md
- workflows/manual-checklist.md

**References:**
- resources/verification-evidence.md
- resources/task-closeout-checklist.md

**Scripts:**
- evolutionary/scripts/evaluate_os.py
- evolutionary/scripts/test_os.py
</resource_index>

<L1>
## Core Routing Workflow

1) Identify the verification method used for the task.
2) Route to the matching workflow in `workflows/`.
3) Verify evidence exists and task-card steps are complete.
4) If any step is incomplete, instruct to complete it and resume.
5) Record closeout and move to the next task-card step.
</L1>


<L1>
## Evolution Check
</L1>

**Timestamp:** 2026-01-04 18:00

Check three conditions:

1. **Non-interrupting?**
   - Am I still in the middle of a larger task?
   - If yes → FALSE, if no → TRUE

2. **Cooldown passed?**
   - Has 48 hours passed since this timestamp?
   - If yes → TRUE, if no → FALSE

3. **Candidates available?**
   - Can I think of at least one improvement to this skill?
   - If yes → TRUE, if no → FALSE

**If ALL TRUE:** Proceed to evolutionary/SKILL.md
**If ANY FALSE:** Skip evolution, end workflow

<L1>
---
End of Operational Skill workflow
</L1>


<quality_criteria>
## Success Criteria

Task is successful when:
- [ ] Verification workflow matched and executed
- [ ] All task-card steps are complete
- [ ] Closeout recorded and next task identified

Quality indicators:
- Missing steps: 0
- Evidence completeness: All required evidence present

Failure conditions:
- Verification evidence missing for selected workflow
- Any task-card step remains incomplete
</quality_criteria>
