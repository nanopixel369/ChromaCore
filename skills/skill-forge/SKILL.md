---
name: skill-forge
description: Create skills following the OS/ES evolutionary paradigm. Builds Operational Skills (workflow execution with L1/L2 separation), Evolutionary Skills (refinement systems), or standalone Grunt Skills (simple utilities).
metadata:
  tier: mastercraft
  declared: 2025-12-31
  rationale: Foundation skill for the evolutionary skill system. Changes require ADR.
---

# skill-forge

The foundational skill for creating Operational Skills (OS) and their paired Evolutionary Skills (ES).

<essential_principles>
## The OS/ES Evolutionary Paradigm

Skills are living systems that mature through use:

**Three Tiers:**
- **Grunt**: Simple utilities, no evolution (operational/SKILL.md only)
- **Journeyman**: Competent but unoptimized, ES-enabled (operational/ + evolutionary/)
- **Mastercraft**: Refined through use, ES-disabled, changes via ADR

**Two Layers:**
- **Layer 1 (Skeletal)**: Immutable core workflow in `<L1></L1>` tags
- **Layer 2 (Surface)**: Tunable optimizations, wisdoms, heuristics

**Evolution Mechanics:**
Activates when ALL true: non-interrupting + 48hr cooldown + candidates available
ES modifies Layer 2 only via 5-phase workflow with 1/8 selection rule

## Skill Structure Created by skill-forge

Generated skills use operational/evolutionary architecture:
```
my-skill/
├── operational/
│   └── SKILL.md              (workflow execution, journeyman tier)
└── evolutionary/
    ├── SKILL.md              (evolution system)
    └── resources/
        └── os_changelog.md
```

## Architecture Inspiration

Output follows create-agent-skills pattern:
- Router architecture (intake → routing table)
- XML semantic structure
- Progressive disclosure
- Modular composition
</essential_principles>

<intake>
What would you like to create?

1. **Full skill pair** (OS + ES for complex workflows)
2. **Grunt skill** (OS only for simple utilities)
3. **Add evolution** (ES to existing OS)
4. **Convert legacy** (upgrade old skill to OS/ES)

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "full", "pair", "journeyman" | workflows/create-skill-pair.md |
| 2, "grunt", "simple", "utility" | workflows/create-grunt.md |
| 3, "evolution", "ES", "add ES" | workflows/add-evolution.md |
| 4, "convert", "upgrade", "legacy" | workflows/convert-legacy.md |
</routing>

<resource_index>
## Available Resources

**Workflows:**
- create-skill-pair.md - Main workflow for journeyman skills
- create-grunt.md - Simple utility creation
- add-evolution.md - Add ES to existing OS
- convert-legacy.md - Migrate legacy skills

**Templates:**
- modules/os/ - 11 OS building blocks
- modules/es/ - 10 ES building blocks

**References:**
- composition-presets.md - Pre-built module combinations
- layer-separation-guide.md - L1/L2 identification
- guidance.md - Best practices

**Scripts:**
- builder.py - Assemble modules into skills
- validate_os.py - Validate OS structure
- validate_es.py - Validate ES binding
- extract_l1_map.py - Parse L1 boundaries
</resource_index>

<success_criteria>
## Completion Criteria

- [ ] User intent routed correctly
- [ ] Appropriate workflow executed
- [ ] Skills validated successfully
- [ ] User informed of next steps
</success_criteria>