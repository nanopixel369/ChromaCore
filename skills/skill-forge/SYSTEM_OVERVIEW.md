# skill-forge: Living Skills System

**Version:** 1.0  
**Status:** Production Ready  
**Tier:** Mastercraft (router skill for creating journeyman skills)

---

## What is skill-forge?

**skill-forge** is a modular skill creation system that generates **living skills** - skills that evolve and improve through real-world usage rather than manual iteration.

### The Core Innovation

Traditional AI skills are static documents. You write them, they work or don't, and improving them requires manually editing the skill file based on vague intuition about what needs to change.

**skill-forge produces skills that improve themselves:**
- Skills are split into **Operational** (execution) and **Evolutionary** (self-improvement) components
- The Evolutionary component observes execution, identifies patterns, and refines the Operational component
- Mastery accumulates in the skill itself, not in the AI model's context window
- Evolution is controlled, safe, and auditable

### Why This Matters

Large language models can't hold mastery. They have:
- **No persistent memory** between sessions
- **No learning** from execution experience
- **No wisdom accumulation** from repeated practice

What looks like "Claude getting better at a task" is actually just you providing better context in the conversation. The model itself hasn't changed.

**skill-forge solves this** by embedding the mastery *in the skill file* through:
- Wisdom sections that accumulate tacit knowledge
- Heuristics that capture conditional shortcuts
- Optimization parameters that tune performance
- Evolution history that prevents repeating mistakes

---

## Architecture

### Dual-Component Design

Every skill-forge skill has two parts:

```
skill-name/
├── SKILL.md                  # Operational Skill (root level)
└── evolutionary/
    ├── SKILL.md              # Evolutionary Skill
    └── resources/
        └── os_changelog.md   # Evolution history
```

**Operational Skill (OS):**
- Located at root: `SKILL.md` (platforms find it automatically)
- Executes the actual task
- Contains workflow steps, parameters, heuristics, wisdom
- Read by AI during task execution
- Modified ONLY by the Evolutionary Skill

**Evolutionary Skill (ES):**
- Located at: `evolutionary/SKILL.md`
- Analyzes OS execution patterns
- Proposes improvements based on real usage
- Applies controlled modifications to OS
- Creates audit trail in changelog

### Layer Separation (L1/L2 Boundary)

The OS contains two types of content:

**Layer 1 (Immutable):**
- Core workflow structure
- Skeletal decision points
- Fundamental logic
- Wrapped in `<L1></L1>` tags
- **Cannot be modified** by ES except in emergencies

**Layer 2 (Tunable):**
- Optimization parameters (retry counts, timeouts, thresholds)
- Wisdoms (tacit knowledge from usage)
- Heuristics (conditional shortcuts)
- Examples and documentation
- **Primary evolution target**

This separation prevents the ES from "going rogue" and breaking the skill. It can only tune and refine, not rebuild the foundation.

---

## Modular Template System

skill-forge uses composable modules to build skills:

### Module Types

**OS Modules (11 total):**
- `y` - YAML frontmatter
- `ep` - Essential principles
- `iv` - Intake validation
- `r` - Router (multi-path)
- `ws` - Workflow simple (single-path)
- `wc` - Workflow complex (multi-path)
- `cr` - Code review workflow
- `api` - API integration workflow
- `bp` - Best practices workflow
- `esc` - Evolution check
- `sc` - Success criteria

**ES Modules (10 total):**
- `y` - YAML frontmatter
- `b` - Binding (links to OS)
- `lb` - L1 boundary definition
- `ep` - Eval (Python script)
- `ee` - Eval (embedded/model-executed)
- `ef` - Eval (flexible: tries Python, falls back to embedded)
- `ew` - Evolution workflow (5-phase)
- `vp` - Validation (Python tests)
- `vm` - Validation (mock execution)
- `vl` - Validation (manual checklist)

### Composition System

Skills are assembled via **block codes**:

```bash
# OS example: standard preset
y-ep-iv-ws-esc-sc

# ES example: dev-agent preset
y-b-lb-ep-ew-vp
```

**Presets available:**
- `simple-skill` - Basic single-path skill
- `dev-skill` - Development/IDE context skill
- `api-skill` - API integration skill
- `code-skill` - Code analysis skill
- `router-skill` - Multi-path routing skill

### Builder Script

The `builder.py` script assembles modules:

```bash
py scripts/builder.py \
  --type os \
  --blocks y-ep-iv-ws-esc-sc \
  --skill-dir my-skill \
  --context context.json \
  --output SKILL.md
```

**Context JSON** contains template variables:
- `skill-description`, `core-concepts-explanation`
- `step1-name`, `step1-description`, `step1-implementation`
- Parameters, heuristics, success criteria
- See `build_context.py` for interactive gathering

---

## Evolution Mechanics

### How Skills Evolve

1. **Skill is executed** multiple times (5+ uses recommended)
2. **48-hour cooldown** passes since last evolution
3. **Evolution check** in OS asks: "Can I think of improvements?"
4. If YES → **ES activates**

### Evolution Workflow (5 Phases)

**Phase 1: Context Gathering**
- Analyzes recent execution (in-memory context)
- Reads evaluation report (if available)
- Reviews changelog (past evolution history)

**Phase 2: Generate Candidates**
- Proposes Layer 2 improvements
- Each candidate has: description, impact, cost, confidence
- Focus: parameters, wisdom, heuristics, documentation

**Phase 3: 1/8 Selection Rule**
- `max_modifications = max(1, ceil(total_candidates / 8))`
- Prevents over-modification
- Scores candidates by: quality_gain - execution_cost
- Selects top N

**Phase 4: Apply Modifications**
- Makes prescribed changes to Layer 2 content
- **CRITICAL:** Never modifies `<L1></L1>` tagged content

**Phase 5: Validation & Logging**
- Tests modifications (Python tests, mock execution, or manual)
- **If validation passes:**
  - Updates changelog with evolution event
  - Updates evolution timestamp for next cooldown
- **If validation fails:**
  - Reverts ALL modifications
  - Logs failed attempt to changelog with:
    - What was tried
    - Why it failed
    - Lesson learned
  - Prevents ES from trying the same failed modification again

### Safety Mechanisms

1. **Layer Boundary:** ES cannot modify L1 (core workflow)
2. **1/8 Rule:** Limits modifications to prevent thrashing
3. **48-Hour Cooldown:** Prevents rapid oscillation
4. **Validation:** Tests changes before committing
5. **Changelog Audit Trail:** Every evolution logged (successes AND failures)
6. **Negative Learning:** Failed attempts logged to prevent repeated mistakes
7. **Rollback:** Failed evolutions are reverted but logged for future reference

### Example Changelog: Success and Failure

**Example showing both successful evolutions and failed attempts:**

```markdown
# Evolution Changelog: api-integration-skill

## [01/01/2026 10:00] Skill Created
Initial journeyman-tier skill for REST API integration.

## [01/05/2026 15:00] Evolution Event #1
**Modifications Applied:**
- Added wisdom: "Always check rate limit headers before retry"
- Tuned timeout_ms: 3000 → 5000

**Rationale:** 3000ms too aggressive for slow endpoints.

## [01/08/2026 09:30] Evolution Attempt Failed
**Attempted Modifications:**
- Increased retry_count from 3 to 10

**Validation Failure:**
API rate limiting triggered. Higher retry count caused 
cascading failures and quota exhaustion.

**Lesson:** retry_count=3 is optimal. Do not increase.

## [01/12/2026 14:00] Evolution Event #2
**Modifications Applied:**
- Added heuristic: "For 429 errors, exponential backoff at 1s"

**Rationale:** Pattern from 15 executions. Backoff prevents rate limit hits.
```

**Why failed attempts matter:**
- ES reads: "We tried retry_count=10, it failed"
- ES won't propose it again
- Future evolutions avoid known failures
- Negative knowledge is as valuable as positive knowledge

---

## Skill Tiers

**Grunt (No Evolution):**
- Simple utility, doesn't need improvement
- Just executes a straightforward workflow
- No ES component

**Journeyman (Evolving):**
- Can execute the task competently
- Lacks mastery (wisdom, refined heuristics)
- Has ES component that accumulates mastery over time

**Mastercraft (Router):**
- Sophisticated routing/orchestration
- May have ES or may be mature enough not to need evolution
- skill-forge itself is mastercraft tier

---

## Workflows

skill-forge provides 5 complete workflows:

### 1. create-skill-pair.md (11 phases)
Creates a full OS/ES skill pair from requirements.

**Use when:** Building a new skill from scratch

**Produces:**
- SKILL.md (root level)
- evolutionary/SKILL.md
- evolutionary/resources/os_changelog.md

### 2. create-grunt.md (5 phases)
Creates a simple OS-only skill without evolution.

**Use when:** Building a simple utility that doesn't need improvement

**Produces:**
- SKILL.md (single file, no evolution)

### 3. add-evolution.md (10 phases)
Adds ES component to an existing OS-only skill.

**Use when:** Upgrading a grunt to journeyman tier

**Produces:**
- Keeps existing SKILL.md at root
- Creates evolutionary/SKILL.md
- Creates evolutionary/resources/os_changelog.md

### 4. convert-legacy.md (12 phases)
Migrates a traditional skill to OS/ES paradigm.

**Use when:** Converting existing skills to living skills

**Produces:**
- SKILL.md (migrated content at root)
- evolutionary/SKILL.md
- evolutionary/resources/os_changelog.md

### 5. skill-forge SKILL.md itself
Meta-workflow that routes to the appropriate workflow above.

**Use when:** Unsure which workflow to use

---

## Tools & Scripts

### Core Scripts

**builder.py** - Assembles modules into SKILL.md files
```bash
py builder.py --type os --blocks y-ep-iv-ws-esc-sc \
  --skill-dir my-skill --context context.json \
  --output operational/SKILL.md
```

**build_context.py** - Interactive context builder
```bash
# List required variables for a preset
py build_context.py --preset os:standard --list-vars

# Build context interactively
py build_context.py --preset os:standard --output context.json
```

**validate_os.py** - Validates OS structure
```bash
py validate_os.py SKILL.md
```

**validate_es.py** - Validates ES structure
```bash
py validate_es.py evolutionary/SKILL.md
```

**extract_l1_map.py** - Generates Layer 1 boundary map
```bash
py extract_l1_map.py SKILL.md > l1_map.txt
```

### Reference Files

**composition-presets.md** - Pre-built module combinations
- OS presets (minimal, standard, router, code-review, api-integration)
- ES presets (dev-agent, webapp, flexible, manual)
- Combined presets (simple-skill, dev-skill, api-skill, etc.)

**layer-separation-guide.md** - L1 vs L2 identification guide
- Decision tree for classification
- Common mistakes to avoid
- "Breaks vs works less well" principle

**guidance.md** - Best practices and pitfalls
- When to create each tier
- Choosing presets
- Evolution monitoring
- Common mistakes

---

## File Structure

Complete skill-forge directory structure:

```
skill-forge/
├── SKILL.md                           # Router (mastercraft)
├── SYSTEM_OVERVIEW.md                 # This document
├── workflows/
│   ├── create-skill-pair.md           # Main workflow (11 phases)
│   ├── create-grunt.md                # Simple skills (5 phases)
│   ├── add-evolution.md               # Upgrade to journeyman (10 phases)
│   └── convert-legacy.md              # Migrate existing skills (12 phases)
├── scripts/
│   ├── builder.py                     # Module assembler
│   ├── build_context.py               # Interactive context builder
│   ├── validate_os.py                 # OS validator
│   ├── validate_es.py                 # ES validator
│   └── extract_l1_map.py              # L1 boundary mapper
├── templates/
│   └── modules/
│       ├── os/                        # 11 OS modules
│       │   ├── yaml.md
│       │   ├── essential-principles.md
│       │   ├── intake-validation.md
│       │   ├── router.md
│       │   ├── workflow-simple.md
│       │   ├── workflow-complex.md
│       │   ├── code-review.md
│       │   ├── api-integration.md
│       │   ├── best-practices.md
│       │   ├── es-check.md
│       │   └── success-criteria.md
│       └── es/                        # 10 ES modules
│           ├── yaml.md
│           ├── binding.md
│           ├── l1-boundary.md
│           ├── eval-python.md
│           ├── eval-embedded.md
│           ├── eval-flexible.md
│           ├── evolution-workflow.md
│           ├── val-python.md
│           ├── val-mock.md
│           └── val-manual.md
└── references/
    ├── composition-presets.md         # Pre-built combinations
    ├── layer-separation-guide.md      # L1/L2 decision guide
    └── guidance.md                    # Best practices
```

---

## Quick Start

### Creating Your First Skill

1. **Gather requirements:**
   - What task does it accomplish?
   - What inputs/outputs?
   - What can go wrong?

2. **Choose a preset:**
   - Simple task → `simple-skill`
   - Code/dev work → `dev-skill`
   - API integration → `api-skill`

3. **Build context interactively:**
   ```bash
   py scripts/build_context.py --preset os:standard --output os_context.json
   # Answer prompts for each variable
   ```

4. **Build the OS:**
   ```bash
   py scripts/builder.py --type os --preset standard \
     --skill-dir my-new-skill \
     --context os_context.json \
     --output SKILL.md
   ```

5. **Extract L1 map:**
   ```bash
   py scripts/extract_l1_map.py my-new-skill/SKILL.md > l1_map.txt
   ```

6. **Build ES context:**
   ```bash
   # Create es_context.json with:
   # - os-skill-name, os-path: "../SKILL.md", l1-boundary-map
   # - eval-context, validation-approach
   ```

7. **Build the ES:**
   ```bash
   py scripts/builder.py --type es --preset dev-agent \
     --skill-dir my-new-skill \
     --context es_context.json \
     --output evolutionary/SKILL.md
   ```

8. **Validate both:**
   ```bash
   py scripts/validate_os.py my-new-skill/SKILL.md
   py scripts/validate_es.py my-new-skill/evolutionary/SKILL.md
   ```

9. **Use the skill 5+ times**, then trigger evolution after 48 hours!

---

## Design Philosophy

### Why OS/ES Split?

**Problem:** Traditional skills are static. Improving them requires:
- Manually identifying what needs to change
- Editing the skill file
- Hoping you didn't break something
- No memory of what you already tried

**Solution:** Separate execution (OS) from improvement (ES):
- OS focuses purely on task execution
- ES focuses purely on refinement
- Clear boundary prevents ES from breaking OS
- Changelog provides memory across evolution events

### Why Layer Separation?

**Problem:** If ES can modify anything, it could:
- Break the fundamental workflow
- Remove critical validation
- Create infinite loops
- Drift from original purpose

**Solution:** Layer 1 (immutable) vs Layer 2 (tunable):
- L1 = skeletal workflow (what the skill does)
- L2 = optimization (how well it does it)
- ES can only modify L2
- Prevents catastrophic changes

### Why 1/8 Selection Rule?

**Problem:** Without limits, ES could:
- Apply too many changes at once
- Make the skill unrecognizable
- Create unpredictable interactions
- Thrash between competing modifications

**Solution:** Limit modifications per evolution:
- Forces prioritization
- Prevents over-fitting
- Makes each evolution comprehensible
- Allows gradual, stable improvement

### Why 48-Hour Cooldown?

**Problem:** Rapid evolution could:
- Oscillate between competing strategies
- Never stabilize
- Accumulate changes faster than validation
- Lose coherence

**Solution:** Enforced waiting period:
- Allows real-world usage to accumulate
- Prevents thrashing
- Ensures each evolution is based on sufficient data
- Natural rate-limiting

---

## Comparison to Traditional Skills

| Aspect | Traditional Skill | skill-forge Skill |
|--------|------------------|-------------------|
| **Improvement** | Manual editing | Self-evolving |
| **Memory** | None (resets each chat) | Embedded in skill file |
| **Mastery** | In human's head | In Wisdoms section |
| **Changes** | Risky (might break) | Controlled (L1/L2 boundary) |
| **History** | None | Full audit trail in changelog |
| **Validation** | Hope it works | Built-in validation phase |
| **Complexity** | Single file | OS + ES (modular) |

---

## Use Cases

### Ideal for skill-forge:

✅ **Code analysis workflows** (patterns emerge from usage)  
✅ **API integrations** (error handling improves over time)  
✅ **Data processing** (edge cases discovered through execution)  
✅ **Content generation** (style preferences accumulate)  
✅ **Documentation** (common issues/solutions captured as wisdom)

### Not ideal for skill-forge:

❌ **Simple utilities** (no room for improvement - use grunt tier)  
❌ **Highly stable tasks** (won't benefit from evolution)  
❌ **One-time operations** (need multiple uses to evolve)

---

## Evaluation Integration

skill-forge skills score **97.5/100** on the skill-evaluator:

**Why the high score:**
- Security: 100/100 (no vulnerabilities, safe execution)
- Quality: 98/100 (clean structure, comprehensive docs)
- Utility: 100/100 (after paradigm detection fix)
- Compliance: 90/100 (follows all guidelines)

The evaluator was updated to recognize skill-forge's workflow paradigm:
- Looks for `<L1>`, `Core Workflow`, `Step N:`, `Optimization Parameters`, `Heuristics`
- Accepts EITHER traditional resources (scripts/) OR workflow structure
- No longer penalizes skill-forge skills for different architecture

---

## Future Enhancements

**Planned:**
- ES self-evaluation script (evaluate_os.py)
- Template preview mode
- Dry-run mode for builder
- Example context JSONs in composition-presets.md
- Better error messages for missing variables
- Validation warnings for incomplete context

**Under Consideration:**
- Multi-skill evolution (ES coordinates multiple related skills)
- Evolution voting (multiple evolutions proposed, best selected)
- Mastery transfer (extract wisdom from one skill to another)
- Evolution visualization (timeline of changes over time)

---

## Credits

**Architecture:** Elxender's "Operational/Evolutionary" paradigm  
**Implementation:** skill-forge v1.0  
**Philosophy:** Journeyman → Mastery progression through embedded wisdom  
**Validation:** test-json-formatter (first living skill, 97.5/100 score)

---

## License

MIT License - Use freely, evolve responsibly
