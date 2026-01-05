# Convert Legacy Skill Workflow

Migrates an old-style skill to OS/ES paradigm.

<required_reading>
- references/layer-separation-guide.md
</required_reading>

<L1>
## Core Workflow

### Phase 1: Locate Legacy Skill

Ask user: **"Which skill do you want to convert?"**

Options:
1. Skill name
2. Full path to SKILL.md

Validate file exists and read content.

### Phase 2: Backup Original
```bash
cp -r ~/.claude/skills/$SKILL_NAME \
  ~/.claude/skills/$SKILL_NAME.backup.$(date '+%Y%m%d')

echo "✓ Created backup: $SKILL_NAME.backup.$(date '+%Y%m%d')"
```

### Phase 3: Analyze Legacy Structure

Read legacy SKILL.md and identify:
- Workflow steps (will become L1)
- Configuration/parameters (will become L2)
- Current structure (single file? multiple files?)

### Phase 4: Create New Structure
```bash
mkdir -p ~/.claude/skills/$SKILL_NAME/operational
mkdir -p ~/.claude/skills/$SKILL_NAME/evolutionary/resources

# Move legacy content to operational/
cp ~/.claude/skills/$SKILL_NAME/SKILL.md \
  ~/.claude/skills/$SKILL_NAME/operational/SKILL.md

# Archive old structure
mkdir ~/.claude/skills/$SKILL_NAME/legacy
mv ~/.claude/skills/$SKILL_NAME/SKILL.md \
  ~/.claude/skills/$SKILL_NAME/legacy/ 2>/dev/null || true
```

### Phase 5: Identify and Tag Layers

Apply references/layer-separation-guide.md to migrated OS:

**Identify L1 (core workflow):**
Parse operational/SKILL.md for sequential steps that define correctness.

**Wrap in tags:**
For each L1 section, add `<L1>` before and `</L1>` after.

**Identify L2 (parameters, examples, wisdoms):**
Everything not tagged is L2 by default.

Show user the tagged result and confirm layer separation.

### Phase 6: Modernize YAML

Update frontmatter to include:
- `tier: journeyman`
- `evo_pair: evolution/SKILL.md`
- Modern trigger format

### Phase 7: Add Evolution Check

Append evolution check module:
```bash
cat templates/modules/os/es-check.md | \
  sed "s/\$current-timestamp/$(date '+%m%d%Y %H%M')/" \
  >> ~/.claude/skills/$SKILL_NAME/operational/SKILL.md
```

### Phase 8: Extract L1 Map
```bash
python scripts/extract_l1_map.py \
  --os-path ~/.claude/skills/$SKILL_NAME/operational/SKILL.md \
  --output /tmp/l1_map.txt
```

### Phase 9: Build ES

Ask user for context and validation preferences, then:
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

python scripts/builder.py \
  --type es \
  --blocks $ES_COMPOSITION \
  --skill-dir ~/.claude/skills/$SKILL_NAME/operational \
  --context /tmp/es_context.json \
  --output ~/.claude/skills/$SKILL_NAME/evolutionary/SKILL.md
```

### Phase 10: Initialize Changelog
```bash
cat > ~/.claude/skills/$SKILL_NAME/evolutionary/resources/os_changelog.md << EOF
# Evolution Changelog: $SKILL_NAME

## [$(date '+%Y-%m-%d %H:%M')] Legacy Skill Converted

Migrated from legacy format to OS/ES paradigm.
- Added Layer 1/2 separation
- Added evolution capability
- Preserved original functionality in backup

Original backed up to: $SKILL_NAME.backup.$(date '+%Y%m%d')
EOF
```

### Phase 11: Validate Migration
```bash
python scripts/validate_os.py \
  --skill-path ~/.claude/skills/$SKILL_NAME/operational

python scripts/validate_es.py \
  --es-path ~/.claude/skills/$SKILL_NAME/evolutionary \
  --os-path ~/.claude/skills/$SKILL_NAME/operational
```

### Phase 12: Report Success
```
✓ Converted legacy skill: $SKILL_NAME

Migration complete:
  - Original backed up to: $SKILL_NAME.backup.$(date '+%Y%m%d')
  - Migrated to operational/SKILL.md with L1/L2 separation
  - Added evolutionary/SKILL.md for evolution capability
  - Initialized changelog

Structure:
  operational/SKILL.md - Modernized workflow
  evolutionary/SKILL.md - Evolution system
  legacy/ - Original files (archived)

Next steps:
1. Test the migrated skill to ensure functionality preserved
2. After 48 hours, ES can activate and begin improvements
```
</L1>

<quality_criteria>
## Success Criteria

- [ ] Legacy skill located and backed up
- [ ] New structure created
- [ ] Layers identified and tagged
- [ ] YAML modernized
- [ ] Evolution check added
- [ ] L1 map extracted
- [ ] ES built successfully
- [ ] Changelog initialized
- [ ] Validation passed
- [ ] Original functionality preserved
- [ ] User notified
</quality_criteria>