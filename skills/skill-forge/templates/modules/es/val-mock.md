## Validation Phase

Execute a mock run of the OS workflow with test inputs:

1. **Prepare test input:** $test-input-spec

2. **Execute modified OS workflow**

3. **Verify:**
   - [ ] Workflow completes without errors
   - [ ] Output matches expected format
   - [ ] No exceptions thrown
   - [ ] Quality criteria still met

**If validation passes:**
- Changes are valid
- Skill is functional
- Evolution successful → changes committed

**If validation fails:**
- Changes broke the skill
- Revert ALL modifications
- Log failure in changelog:

```bash
cat >> ../evolutionary/resources/os_changelog.md << 'EOF'
## [$timestamp] Evolution Attempt Failed

**Attempted Modifications:**
[list attempted changes]

**Validation Failure:**
[what broke during mock execution]
EOF
```

- End evolution workflow
