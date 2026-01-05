# Composition Presets

Pre-built module combinations for common skill patterns.

## OS Presets (Composition Strings)

### minimal
**Blocks:** `y-ws-sc`
**For:** Simplest possible OS (barebones workflow + success criteria)
**Use when:** Creating proof-of-concept or placeholder skills

### standard
**Blocks:** `y-ep-iv-ws-esc-sc`
**For:** Most common journeyman skill pattern
**Components:**
- yaml (frontmatter)
- essential-principles (core concepts)
- intake-validation (when to use)
- workflow-simple (single-path workflow)
- es-check (evolution activation)
- success-criteria (quality metrics)
**Use when:** Creating typical journeyman skills with evolution

### router
**Blocks:** `y-ep-iv-r-sc`
**For:** Complex skills needing multiple specialized workflows
**Components:**
- yaml (frontmatter)
- essential-principles (core concepts)
- intake-validation (when to use)
- router (intake + routing table)
- success-criteria (quality metrics)
**Use when:** Skill needs 3+ distinct execution paths
**Note:** Workflows go in separate files under workflows/

### code-review
**Blocks:** `y-ep-iv-cr-esc-sc`
**For:** Code analysis and review workflows
**Components:**
- yaml (frontmatter)
- essential-principles (core concepts)
- intake-validation (when to use)
- code-review (code analysis workflow)
- es-check (evolution activation)
- success-criteria (quality metrics)
**Use when:** Building code review/analysis skills

### api-integration
**Blocks:** `y-ep-iv-api-esc-sc`
**For:** REST API interaction workflows
**Components:**
- yaml (frontmatter)
- essential-principles (core concepts)
- intake-validation (when to use)
- api-integration (HTTP request/response workflow)
- es-check (evolution activation)
- success-criteria (quality metrics)
**Use when:** Fetching/posting data to APIs

### best-practices
**Blocks:** `y-ep-iv-bp-esc-sc`
**For:** Guidance and recommendation workflows
**Components:**
- yaml (frontmatter)
- essential-principles (core concepts)
- intake-validation (when to use)
- best-practices (analysis + recommendations workflow)
- es-check (evolution activation)
- success-criteria (quality metrics)
**Use when:** Providing domain-specific guidance

## ES Presets (Composition Strings)

### dev-agent
**Blocks:** `y-b-lb-ep-ew-vp`
**For:** IDE/development agent context with terminal access
**Components:**
- yaml (frontmatter)
- binding (OS link)
- l1-boundary (layer map)
- eval-python (script-based evaluation)
- evolution-workflow (5 phases)
- val-python (test-based validation)
**Use when:** Skill runs in IDE or has Python execution capability

### webapp
**Blocks:** `y-b-lb-ee-ew-vm`
**For:** Claude.ai browser interface
**Components:**
- yaml (frontmatter)
- binding (OS link)
- l1-boundary (layer map)
- eval-embedded (model-executed evaluation)
- evolution-workflow (5 phases)
- val-mock (mock execution validation)
**Use when:** Skill runs in Claude.ai webapp

### flexible
**Blocks:** `y-b-lb-ef-ew-vp`
**For:** Adaptive execution (IDE or webapp)
**Components:**
- yaml (frontmatter)
- binding (OS link)
- l1-boundary (layer map)
- eval-flexible (tries Python, falls back to embedded)
- evolution-workflow (5 phases)
- val-python (test-based validation)
**Use when:** Skill might run in multiple contexts

### manual
**Blocks:** `y-b-lb-ee-ew-vn`
**For:** Custom validation requirements
**Components:**
- yaml (frontmatter)
- binding (OS link)
- l1-boundary (layer map)
- eval-embedded (model-executed evaluation)
- evolution-workflow (5 phases)
- val-manual (checklist validation)
**Use when:** Pre-made tests don't fit the skill's needs

## Combined Presets (OS + ES Pairs)

### simple-skill
**OS:** standard (`y-ep-iv-ws-esc-sc`)
**ES:** webapp (`y-b-lb-ee-ew-vm`)
**For:** Most common journeyman skill on Claude.ai
**Use when:** Creating typical skills for browser use

### dev-skill
**OS:** standard (`y-ep-iv-ws-esc-sc`)
**ES:** dev-agent (`y-b-lb-ep-ew-vp`)
**For:** Development/testing skills with terminal access
**Use when:** Creating skills for IDE integration

### api-skill
**OS:** api-integration (`y-ep-iv-api-esc-sc`)
**ES:** flexible (`y-b-lb-ef-ew-vp`)
**For:** API interaction skills for any context
**Use when:** Building REST API integrations

### code-skill
**OS:** code-review (`y-ep-iv-cr-esc-sc`)
**ES:** dev-agent (`y-b-lb-ep-ew-vp`)
**For:** Code analysis/review in development context
**Use when:** Building code quality/review tools

### router-skill
**OS:** router (`y-ep-iv-r-sc`)
**ES:** webapp (`y-b-lb-ee-ew-vm`)
**For:** Complex multi-path skills
**Use when:** Need 3+ distinct workflows in one skill
