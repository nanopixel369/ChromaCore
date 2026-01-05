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
## [$timestamp] Evolution Attempt Failed

**Attempted Modifications:**
[list attempted changes]

**Validation Failure:**
[what broke]
EOF
```

- End evolution workflow
