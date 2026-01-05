## Evaluation Phase

Execute the evaluation script:

```bash
python ../evolutionary/scripts/evaluate_os.py \
  --os-path ../SKILL.md \
  --output eval_report.json
```

Load eval_report.json into context for decision-making.

**Evaluation provides:**
- Security analysis (5 layers)
- Quality metrics (code/docs/structure/functionality)
- Compliance validation
- Utility assessment
- Specific improvement recommendations
