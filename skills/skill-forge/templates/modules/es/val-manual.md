## Validation Phase

Perform manual validation checks:

**Validation Checklist:**
- [ ] $validation-criterion1
- [ ] $validation-criterion2
- [ ] $validation-criterion3
- [ ] L1 tags still properly paired (`<L1>` has matching `</L1>`)
- [ ] YAML frontmatter valid
- [ ] Workflow steps still sequential
- [ ] No syntax errors introduced

**If ALL checks pass:**
- Changes are valid
- Skill is functional
- Evolution successful → changes committed

**If ANY check fails:**
- Changes broke the skill
- Revert ALL modifications
- Log failure in changelog:

```bash
cat >> ../evolutionary/resources/os_changelog.md << 'EOF'
## [$timestamp] Evolution Attempt Failed

**Attempted Modifications:**
[list attempted changes]

**Validation Failure:**
[which check failed]
EOF
```

- End evolution workflow
