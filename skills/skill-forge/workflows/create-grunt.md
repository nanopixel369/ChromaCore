# Create Grunt Skill Workflow

Creates a simple utility skill (Operational only, no Evolution).

<L1>
## Core Workflow

### Phase 1: Confirm Simplicity

Ask user: **"Describe the task this utility should perform."**

Analyze response for complexity indicators:

**Simple (proceed):**
- Single, straightforward operation
- No optimization opportunities
- No branching or decisions
- Examples: format text, convert units, calculate hash

**Complex (suggest upgrade):**
- Multi-step workflow
- Optimization potential
- Conditional logic
→ "This seems complex enough to benefit from evolution. Create full skill pair instead?"

If user insists on grunt tier, proceed.

### Phase 2: Gather Details

Ask:
- "What format is the input?"
- "What format is the output?"
- "Any error conditions to handle?"

### Phase 3: Build Operational Skill

Create context:
```bash
cat > /tmp/os_context.json << EOF
{
  "skill-name": "$SKILL_NAME",
  "tier": "grunt",
  "skill-description": "$DESCRIPTION",
  "triggers-keywords": "$KEYWORDS",
  "input-format": "$INPUT",
  "output-format": "$OUTPUT"
}
EOF
```

Execute builder (minimal composition - no ES check):
```bash
mkdir -p ~/.claude/skills/$SKILL_NAME/operational

python scripts/builder.py \
  --type os \
  --blocks y-ws-sc \
  --skill-dir ~/.claude/skills/$SKILL_NAME \
  --context /tmp/os_context.json \
  --output ~/.claude/skills/$SKILL_NAME/operational/SKILL.md
```

Note: Grunt uses `y-ws-sc` (yaml, workflow-simple, success-criteria) - NO es-check module.

### Phase 4: Validate
```bash
python scripts/validate_os.py \
  --skill-path ~/.claude/skills/$SKILL_NAME/operational \
  --tier grunt
```

### Phase 5: Report Success
```
✓ Created grunt skill: $SKILL_NAME

Structure:
  operational/SKILL.md (no evolution capability)

This is a simple utility. If complexity grows, you can upgrade
it to journeyman tier with: "Add evolution to $SKILL_NAME"
```
</L1>

<quality_criteria>
## Success Criteria

- [ ] Task confirmed as simple
- [ ] Details gathered
- [ ] OS built (no ES check)
- [ ] Validation passed
- [ ] User notified
</quality_criteria>