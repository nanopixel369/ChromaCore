# Task Card Template (Root)

This file defines the **canonical task card format** used to activate agents.

A task card is supplied **in the user prompt**, not edited in-repo.
Agents must parse the task card metadata and follow it exactly.

---

## Task Card Structure

```yaml
task_id: TASK-###
persona: <persona_name>
title: <short descriptive title>

specs:
  - <Spec_File_Name.md>
  - <Optional_Section_or_Subsystem>

scope:
  allowed:
    - <paths / modules / components>
  forbidden:
    - <explicit exclusions>

outputs:
  - <files / artifacts / behaviors>

verification:
  - <command | test | invariant check | placeholder>

notes:
  - <optional constraints or clarifications>