# Add Evolution Workflow

Adds an Evolutionary Skill to an existing Operational Skill.

<required_reading>
- references/layer-separation-guide.md
</required_reading>

<L1>
## Core Workflow

### Phase 1: Locate Existing OS

Ask user: **"What skill do you want to add evolution to?"**

Options:
1. Skill name (if in standard location)
2. Full path to operational/SKILL.md

Validate OS exists and is readable.

### Phase 2: Analyze Existing OS

Read the OS file:
```bash
cat ~/.claude/skills/$SKILL_NAME/operational/SKILL.md
```

Check:
- [ ] Is this already journeyman tier? (has evo_pair in YAML)
- [ ] Does evolutionary/ directory already exist?

If yes to either → "This skill already has evolution capability."

### Phase 3: Identify Layers

Apply references/layer-separation-guide.md to existing OS:

Parse workflow to identify:
- Core steps that must happen (L1)
- Parameters and heuristics (L2)

If no `<L1>` tags exist, recommend adding them:
"I should add L1 tags to mark the skeletal workflow. May I modify the OS?"

If approved, insert `<L1></L1>` tags around core steps.

### Phase 4: Extract L1 Map
```bash
python scripts/extract_l1_map.py \
  --os-path ~/.claude/skills/$SKILL_NAME/operational/SKILL.md \
  --output /tmp/l1_map.txt
```

### Phase 5: Determine Context & Validation

Ask same questions as create-skill-pair:
- Execution context (IDE/webapp/both)
- Validation approach (tests/mock/manual)

### Phase 6: Add Evolution Check to OS

Append evolution check module to OS:
```bash
cat templates/modules/os/es-check.md | \
  sed "s/\$current-timestamp/$(date '+%m%d%Y %H%M')/" \
  >> ~/.claude/skills/$SKILL_NAME/operational/SKILL.md
```

Update YAML frontmatter:
```bash
# Add evo_pair field if not present
sed -i '/^tier:/a evo_pair: evolution/SKILL.md' \
  ~/.claude/skills/$SKILL_NAME/operational/SKILL.md
```

### Phase 7: Build ES

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

Select ES composition based on context, then build:
```bash
mkdir -p ~/.claude/skills/$SKILL_NAME/evolutionary/resources
mkdir -p ~/.claude/skills/$SKILL_NAME/evolutionary/scripts

python scripts/builder.py \
  --type es \
  --blocks $ES_COMPOSITION \
  --skill-dir ~/.claude/skills/$SKILL_NAME/operational \
  --context /tmp/es_context.json \
  --output ~/.claude/skills/$SKILL_NAME/evolutionary/SKILL.md
```

### Phase 8: Initialize Resources
```bash
cat > ~/.claude/skills/$SKILL_NAME/evolutionary/resources/os_changelog.md << EOF
# Evolution Changelog: $SKILL_NAME

## [$(date '+%Y-%m-%d %H:%M')] Evolution Capability Added

Existing skill upgraded to journeyman tier. Evolution system initialized.
EOF
```

### Phase 9: Validate
```bash
python scripts/validate_os.py \
  --skill-path ~/.claude/skills/$SKILL_NAME/operational

python scripts/validate_es.py \
  --es-path ~/.claude/skills/$SKILL_NAME/evolutionary \
  --os-path ~/.claude/skills/$SKILL_NAME/operational
```

### Phase 10: Report Success
```
✓ Added evolution to: $SKILL_NAME

Changes:
  - Added evolution check to operational/SKILL.md
  - Created evolutionary/SKILL.md
  - Initialized changelog

The skill is now journeyman tier and will evolve through use.
After 48 hours and with improvement candidates, ES will activate.
```
</L1>

<quality_criteria>
## Success Criteria

- [ ] Existing OS located
- [ ] Layers identified
- [ ] L1 map extracted
- [ ] Evolution check added to OS
- [ ] ES built successfully
- [ ] Resources initialized
- [ ] Validation passed
- [ ] User notified
</quality_criteria>