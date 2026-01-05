<L1>
## Evolution Check
</L1>

**Timestamp:** $current-timestamp

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

**If ALL TRUE:** Proceed to $es-path
**If ANY FALSE:** Skip evolution, end workflow

<L1>
---
End of Operational Skill workflow
</L1>
