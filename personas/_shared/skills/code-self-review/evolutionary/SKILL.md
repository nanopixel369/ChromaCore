---
name: ES_code-self-review
tier: journeyman
description: Evolutionary Skill paired with code-self-review. Refines OS through controlled Layer 2 modifications based on execution experience and comprehensive evaluation.
version: 0.1.0
author: ChromaCore
created: 2026-01-04
binding:
  os_path: ../SKILL.md
  os_name: code-self-review
last_evolution: null
---

# ES_code-self-review

Evolution system for code-self-review.


## Binding Information

**Paired Operational Skill:** code-self-review
**OS Path:** ../SKILL.md
**Binding Type:** 1:1 (this ES exclusively refines the paired OS)

## Evolution Authority

This ES has authority to modify:
- ✓ Layer 2 content (parameters, wisdoms, heuristics)
- ✗ Layer 1 content (skeletal workflow)

**Exception cases for L1 modification:**
- Fatal flaw causing 100% failure rate
- Security vulnerability
- Paradigm shift invalidating core assumptions
(All require explicit justification in changelog)


## Layer 1/Layer 2 Boundary Definition

### What is Layer 1 (Immutable)

Layer 1 content is wrapped in `<L1></L1>` tags throughout the OS.

**DO NOT MODIFY Layer 1 content** except in cases of:
- Fatal workflow breakage
- Security vulnerabilities
- Paradigm shifts (requires human approval)

### Layer 1 Content Map

The following sections are marked as Layer 1 in code-self-review:

- SKILL.md lines 103-111: Core Routing Workflow
- SKILL.md lines 114-116: Evolution Check
- SKILL.md lines 137-140: Core workflow section

**L1 Coverage:** 16/159 lines (10.1%)

### What is Layer 2 (Tunable)

Everything NOT wrapped in L1 tags, including:
- Optimization parameters (retry counts, timeouts, thresholds)
- Wisdoms section (append-only)
- Heuristics and shortcuts
- Examples and explanations
- Resource file implementations (when not part of L1 workflow)

**Layer 2 is your modification target.**


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
## [01052026 0223] Evolution Event

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


## Validation Phase

Execute the test suite:

```bash
python ../evolutionary/scripts/test_os.py --verbose
```

**If all tests pass:**
- Changes are valid
- Skill is functional
- Evolution successful → commit changes

**If any test fails:**
- Changes broke the skill
- Revert ALL modifications
- Log failure in changelog:

```bash
cat >> ../evolutionary/resources/os_changelog.md << 'EOF'
## [01052026 0223] Evolution Attempt Failed

**Attempted Modifications:**
[list attempted changes]

**Validation Failure:**
[what broke]
EOF
```

- End evolution workflow
