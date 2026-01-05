<L1>
## Evolution Workflow

### Phase 1: Context Gathering

**Analyze recent OS execution:**
- What friction occurred during workflow?
- What succeeded vs struggled?
- Edge cases discovered?
- Performance observations?

**Read evaluation report** from previous section.

**Review changelog:**
```bash
cat ../evolutionary/resources/os_changelog.md | tail -n 20
```

**Context to consider:**
- Fresh execution experience (just used the skill)
- Evaluation metrics (comprehensive analysis)
- Evolution history (what's been tried before)

### Phase 2: Generate Modification Candidates

Based on all gathered context, propose Layer 2 improvements.

**Focus on:**
- Tuning parameters (retry counts, timeouts, thresholds)
- Adding wisdom entries (tacit knowledge from usage)
- Optimizing heuristics (conditional shortcuts)
- Refining examples/documentation (clarity improvements)

**For each candidate, include:**
- Description of change
- Expected impact
- Execution cost
- Confidence level

**Output complete candidate list to lock it in context:**

```
MODIFICATION CANDIDATES:
1. [Candidate description with impact/cost/confidence]
2. [Candidate description with impact/cost/confidence]
...
```

If no candidates → end evolution workflow.
### Phase 3: Apply 1/8 Selection Rule

Calculate maximum modifications allowed:
```
max_modifications = max(1, ceil(total_candidates / 8))
```

**Score candidates by:**
- quality_gain - execution_cost
- Confidence level
- Alignment with skill's purpose

**Output selected candidates to lock them in context:**

```
SELECTED MODIFICATIONS (top [max_modifications]):
1. [Selected candidate with rationale]
2. [Selected candidate with rationale]
...
```

### Phase 4: Apply Modifications

Make the prescribed changes to Layer 2 content:
- Update parameter values
- Append wisdom entries
- Refine heuristics
- Improve documentation

**CRITICAL:** Do NOT modify anything inside `<L1></L1>` tags.

### Phase 5: Post-Modification Steps

After applying changes:

1. **Update changelog:**
```bash
cat >> ../evolutionary/resources/os_changelog.md << 'EOF'
## [$timestamp] Evolution Event

**Modifications Applied:**
[list changes]

**Evaluation Metrics:**
[key metrics from evaluation]

**Rationale:**
[why these changes]
EOF
```

2. **Update timestamp** in OS evolution check step to current time

3. **Increment version** (patch bump)

Changes are now committed - proceed to validation.
</L1>
