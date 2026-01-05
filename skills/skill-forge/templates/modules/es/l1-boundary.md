## Layer 1/Layer 2 Boundary Definition

### What is Layer 1 (Immutable)

Layer 1 content is wrapped in `<L1></L1>` tags throughout the OS.

**DO NOT MODIFY Layer 1 content** except in cases of:
- Fatal workflow breakage
- Security vulnerabilities
- Paradigm shifts (requires human approval)

### Layer 1 Content Map

The following sections are marked as Layer 1 in $os-skill-name:

$l1-boundary-map

### What is Layer 2 (Tunable)

Everything NOT wrapped in L1 tags, including:
- Optimization parameters (retry counts, timeouts, thresholds)
- Wisdoms section (append-only)
- Heuristics and shortcuts
- Examples and explanations
- Resource file implementations (when not part of L1 workflow)

**Layer 2 is your modification target.**
