# Create Skill Pair Workflow

Creates a journeyman-tier skill pair (Operational + Evolutionary).

<required_reading>
Before proceeding, read:
- references/composition-presets.md
- references/layer-separation-guide.md
</required_reading>

<L1>
## Core Workflow

### Phase 1: Gather Requirements

Ask user: **"What task should this skill perform?"**

Wait for detailed response, then ask clarifying questions:

**If workflow unclear:**
- "Can you give me a specific example of using this skill?"
- "What would the input and output look like?"

**If technical:**
- "What external dependencies? (APIs, tools, file formats)"
- "Error conditions to handle?"

**If complex:**
- "What decisions happen during execution?"
- "Any branching paths or conditional logic?"

Gather until you have:
- [ ] Clear task description
- [ ] Input/output formats
- [ ] External dependencies (if any)
- [ ] Decision points (if any)
- [ ] Error conditions

**Context Builder Tool**: After gathering requirements, use `scripts/build_context.py` to systematically collect all template variables:
```bash
# List required variables for your chosen preset
py scripts/build_context.py --preset os:standard --list-vars

# Build context interactively (prompts for each variable)
py scripts/build_context.py --preset os:standard --output /tmp/os_context.json
```

### Phase 2: Determine Context

Ask user: **"Where will this skill be used?"**

**Options:**
1. IDE/Dev Agent (terminal access, can execute Python)
2. Claude.ai webapp (browser, needs embedded evaluation)
3. Both contexts (flexible approach)

Store answer for ES configuration.

### Phase 3: Choose Validation Approach

Ask user: **"How should evolution validate changes?"**

**Options:**
1. Pre-made test scripts (I'll create test files)
2. Mock execution (ES runs workflow with test input)
3. Manual checklist (define validation criteria)

Store answer for ES configuration.

### Phase 4: Select Composition or Preset

Ask user: **"Choose a skill architecture:"**

Display from composition-presets.md:
- **simple-skill**: Single workflow, minimal (OS=standard + ES=webapp)
- **dev-skill**: Development/testing focus (OS=standard + ES=dev-agent)
- **api-skill**: API integration (OS=api-integration + ES=flexible)
- **code-review-skill**: Code analysis (OS=code-review + ES=dev-agent)
- **custom**: I'll help you compose modules

If custom selected, proceed to references/composition-presets.md for module selection.

Store: OS composition string, ES composition string

### Phase 5: Identify Layers

Using requirements from Phase 1, apply references/layer-separation-guide.md:

**Layer 1 (Skeletal):**
Identify core workflow steps that MUST happen:
- "If I remove this, does the skill break or just work less well?"
- "Is this about WHAT happens or HOW WELL it happens?"

Output L1 steps explicitly:
```
LAYER 1 (Skeletal):
1. [Core step]
2. [Core step]
...
```

**Layer 2 (Surface):**
Identify tunable parameters:
- Retry counts, timeouts, thresholds
- Conditional shortcuts
- Optimization heuristics

Output L2 elements explicitly:
```
LAYER 2 (Surface):
- [Parameter]: [default value]
- [Heuristic]: [description]
...
```

Confirm layer separation with user.

### Phase 6: Build Operational Skill

Create context file:
```bash
cat > /tmp/os_context.json << EOF
{
  "skill-name": "$SKILL_NAME",
  "skill-description": "$DESCRIPTION",
  "triggers-keywords": "$KEYWORDS",
  "triggers-patterns": "$PATTERNS",
  "l1-steps": "$L1_STEPS",
  "l2-params": "$L2_PARAMS"
}
EOF
```

Execute builder:
```bash
mkdir -p ~/.claude/skills/$SKILL_NAME

python scripts/builder.py \
  --type os \
  --blocks $OS_COMPOSITION \
  --skill-dir ~/.claude/skills/$SKILL_NAME \
  --context /tmp/os_context.json \
  --output ~/.claude/skills/$SKILL_NAME/SKILL.md
```

### Phase 7: Extract L1 Boundary Map
```bash
python scripts/extract_l1_map.py \
  --os-path ~/.claude/skills/$SKILL_NAME/SKILL.md \
  --output /tmp/l1_map.txt
```

### Phase 8: Build Evolutionary Skill

Create ES context:
```bash
cat > /tmp/es_context.json << EOF
{
  "os-skill-name": "$SKILL_NAME",
  "os-path": "../SKILL.md",
  "l1-boundary-map": "$(cat /tmp/l1_map.txt)",
  "eval-context": "$EVAL_CONTEXT",
  "validation-approach": "$VALIDATION_APPROACH"
}
EOF
```

Execute builder:
```bash
mkdir -p ~/.claude/skills/$SKILL_NAME/evolutionary/resources
mkdir -p ~/.claude/skills/$SKILL_NAME/evolutionary/scripts

python scripts/builder.py \
  --type es \
  --blocks $ES_COMPOSITION \
  --skill-dir ~/.claude/skills/$SKILL_NAME \
  --context /tmp/es_context.json \
  --output ~/.claude/skills/$SKILL_NAME/evolutionary/SKILL.md
```

### Phase 9: Initialize Resources
```bash
# Changelog
cat > ~/.claude/skills/$SKILL_NAME/evolutionary/resources/os_changelog.md << EOF
# Evolution Changelog: $SKILL_NAME

## [$(date '+%Y-%m-%d %H:%M')] Skill Created

Initial journeyman-tier skill created. No evolutions yet.
EOF

# Copy evaluation script if dev-agent context
if [ "$EVAL_CONTEXT" = "IDE/Dev Agent" ]; then
  cp templates/evaluate_os_template.py \
    ~/.claude/skills/$SKILL_NAME/evolutionary/scripts/evaluate_os.py
fi

# Copy test script if test validation
if [ "$VALIDATION_APPROACH" = "Pre-made test scripts" ]; then
  cp templates/test_os_template.py \
    ~/.claude/skills/$SKILL_NAME/evolutionary/scripts/test_os.py
fi
```

### Phase 10: Validate Skill Pair
```bash
python scripts/validate_os.py \
  --skill-path ~/.claude/skills/$SKILL_NAME/SKILL.md

python scripts/validate_es.py \
  --es-path ~/.claude/skills/$SKILL_NAME/evolutionary \
  --os-path ~/.claude/skills/$SKILL_NAME/SKILL.md
```

If validation fails, report errors and offer to fix.

### Phase 11: Report Success

Output to user:
```
✓ Created skill pair: $SKILL_NAME

Structure:
  SKILL.md - Operational Skill (workflow execution)
  evolutionary/SKILL.md - Evolutionary Skill (refinement system)

Files created:
  - SKILL.md
  - evolutionary/SKILL.md
  - evolutionary/resources/os_changelog.md
  [additional files based on context]

Next steps:
1. Test the skill with: "$EXAMPLE_TRIGGER"
2. After 48 hours of use, ES activates if improvements found
3. Check changelog to see evolution history
```
</L1>

<quality_criteria>
## Success Criteria

- [ ] All requirements gathered
- [ ] Context and validation determined
- [ ] Composition selected
- [ ] Layers identified and confirmed
- [ ] OS built successfully
- [ ] L1 map extracted
- [ ] ES built successfully
- [ ] Resources initialized
- [ ] Validation passed
- [ ] User notified
</quality_criteria>