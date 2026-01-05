## Evaluation Phase

**Adaptive evaluation:** Attempts Python script evaluation, falls back to embedded if unavailable.

### Method 1: Python Script (Preferred)

Try executing:
```bash
python ../evolutionary/scripts/evaluate_os.py \
  --os-path ../SKILL.md \
  --output eval_report.json
```

If successful, load eval_report.json and proceed.

### Method 2: Embedded Evaluation (Fallback)

If script unavailable or execution fails, perform manual evaluation:

**Security:** Check input validation, execution control, output sanitization, privilege management, self-protection

**Quality:** Assess code quality, documentation, structure, functionality

**Utility:** Evaluate problem-solving value, efficiency, usability

Generate evaluation summary in context.
