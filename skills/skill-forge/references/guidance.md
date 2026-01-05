# skill-forge Usage Guidance

Best practices for creating skills with skill-forge.

## When to Create Each Tier

### Grunt (Simple Utility)
**Create when:**
- Single, straightforward operation
- No optimization opportunities
- No branching or decisions
- Won't benefit from evolution

**Examples:**
- Format JSON with proper indentation
- Convert units (meters to feet)
- Calculate hash of file
- Strip whitespace from text

**Don't create grunt if:**
- Workflow has multiple steps
- Parameters could be tuned
- Usage patterns might vary
- Complexity might grow

### Journeyman (Evolvable Skill)
**Create when:**
- Multi-step workflow
- Optimization opportunities exist
- Benefits from accumulated wisdom
- Will be used repeatedly

**Examples:**
- API integration with retry logic
- Code review with quality checks
- Document generation with templates
- Data processing pipelines

**This is the default tier** - when in doubt, create journeyman.

### Mastercraft (Canonical)
**Never create directly** - skills earn this through use.

Promotion criteria:
- Extensive real-world usage (50+ invocations)
- Dense with accumulated wisdoms
- Proven reliability
- Team consensus via ADR

## Choosing Composition Presets

### Start Simple
**Recommendation:** Use `simple-skill` preset (OS=standard + ES=webapp)

This covers 80% of use cases:
- Single workflow path
- Browser-based evaluation
- Mock execution validation

### When to Use Router Pattern
**Use `router-skill` when:**
- 3+ distinct execution paths needed
- Different workflows for different scenarios
- Complex branching logic

**Example:** A documentation skill that:
- Routes to "create-api-docs" workflow for code
- Routes to "create-user-guide" workflow for features
- Routes to "create-readme" workflow for projects

### Context-Specific Presets

**Use `dev-skill` when:**
- Skill runs in IDE or dev agent
- Can execute Python scripts
- Needs comprehensive test suites

**Use `api-skill` when:**
- Primary purpose is REST API interaction
- Needs retry/timeout tuning
- Rate limiting is a concern

**Use `code-skill` when:**
- Analyzing or reviewing code
- Quality metrics are important
- Style/structure matters

## Layer Separation Tips

### Start Conservative
**When identifying L1:**
- If unsure, mark it L1 initially
- ES can't hurt L1, so errors are safe
- Better to over-protect than under-protect

### Iterate Through Use
**After 2-3 evolutions:**
- Review what ES tried to modify
- If it consistently hits L1 boundaries, maybe those should be L2
- If parameters aren't changing, maybe they're not worth being L2

### Trust the Process
**ES learns over time:**
- Bad tweaks teach what not to do
- Wisdoms accumulate from real usage
- 1/8 rule prevents thrashing

## Common Pitfalls

### Pitfall 1: Too Many Parameters
**Problem:**
Exposing 20 tunable parameters creates analysis paralysis for ES.

**Solution:**
Start with 3-5 most impactful parameters. Add more only if ES consistently wants to tune something that's currently fixed.

### Pitfall 2: Vague Wisdoms
**Problem:**
"Sometimes this works better" ← Not actionable

**Solution:**
"[2025-12-31] For PDF files >10MB, increase timeout from 30s to 60s. Prevents timeout errors on large documents."

Be specific: When? Why? What changed?

### Pitfall 3: Ignoring Validation Failures
**Problem:**
ES keeps making same breaking change, validation catches it, nothing learned.

**Solution:**
Review failed evolution attempts. If ES repeatedly tries the same thing, maybe:
- The validation is too strict
- The L1 boundary is wrong
- The skill needs refactoring

### Pitfall 4: Premature Mastercraft Declaration
**Problem:**
Promoting to mastercraft after 5 uses because "it works great!"

**Solution:**
Wait for 50+ real-world uses. Let ES accumulate diverse wisdoms. Mastercraft should represent proven excellence, not early success.

## Best Practices

### 1. Descriptive Skill Names
**Good:** `api-rate-limited-fetcher`
**Bad:** `get-data`

Name should indicate what it does and key characteristics.

### 2. Specific Triggers
**Good:**
```yaml
keywords: [fetch api data, get rest endpoint, call external api]
intent_patterns: [need data from api, retrieve from endpoint]
```

**Bad:**
```yaml
keywords: [data, fetch, get]
```

### 3. Quality Criteria Early
Define success metrics upfront:
```markdown
<quality_criteria>
Task is successful when:
- [ ] API response received with 2xx status
- [ ] Data validated against schema
- [ ] Output formatted correctly

Quality indicators:
- Response time: < 5 seconds
- Success rate: > 95%
</quality_criteria>
```

### 4. Progressive Disclosure in Complex Skills
**For router-pattern skills:**
- Main SKILL.md: 100-200 lines (intake, routing, principles)
- Each workflow file: 200-400 lines (focused on one path)
- References: loaded on-demand

Don't dump everything in one 2000-line file.

### 5. Test Before Deploying
After skill-forge creates the pair:
```bash
# Validate structure
python scripts/validate_os.py --skill-path path/to/skill/operational
python scripts/validate_es.py --es-path path/to/skill/evolutionary

# Test execution
# Invoke the skill with a real task
# Verify it works before relying on it
```

### 6. Monitor Evolution
After each evolution:
```bash
# Check what changed
cat path/to/skill/evolutionary/resources/os_changelog.md

# Review if changes make sense
# If ES is thrashing, investigate why
```

### 7. Use Existing Skills as Templates
Before creating from scratch, check:
- Does a similar skill already exist?
- Can I copy and adapt it?
- What wisdoms has it accumulated?

## Workflow Tips

### Creating Your First Skill
1. Start with `simple-skill` preset
2. Use a real task you do often
3. Be specific about workflow steps
4. Mark obvious L1 (sequential steps)
5. Identify 3-5 L2 parameters
6. Test immediately after creation
7. Use it 5+ times before first evolution

### Evolving Skills Effectively
1. Don't force evolution (let conditions trigger naturally)
2. Review changelog after each evolution
3. If ES makes bad tweaks, let it learn (don't rollback unless broken)
4. After 10 evolutions, review accumulated wisdoms
5. Consider mastercraft promotion after 50+ uses

### Converting Legacy Skills
1. Backup original first
2. Identify L1 by asking "what must happen?"
3. Add L1 tags conservatively
4. Test converted skill thoroughly
5. Let ES tune L2 over time

## Success Metrics

**A skill-forge skill is successful when:**
- Used regularly (10+ times/month)
- Evolutions improve it measurably
- Wisdoms are specific and actionable
- Team members understand how to invoke it
- Maintenance is minimal (ES handles tuning)

**The system is successful when:**
- 80% of skills are journeyman tier
- Evolutions succeed >70% of time (validation passes)
- Skills improve measurably over 6 months
- Team has 3-5 mastercraft skills as exemplars
