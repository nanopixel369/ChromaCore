# Layer 1 vs Layer 2 Separation Guide

How to identify what's skeletal (L1) vs surface (L2) in any skill.

## The Core Question

**"If I change/remove this, does the skill BREAK or just work LESS WELL?"**

- **BREAK** → Layer 1 (skeletal, immutable)
- **LESS WELL** → Layer 2 (surface, tunable)

## Layer 1 (Skeletal) - Immutable

### Definition
Core workflow logic required for correctness. Without these, the skill fails.

### Identification Patterns

**Sequential Steps That Must Happen:**
- "Parse input file" ← must happen for skill to work
- "Validate schema" ← must happen for correctness
- "Send API request" ← core action
- "Check response status" ← required validation
- "Generate output" ← final required step

**I/O Contracts:**
- Input format definitions
- Output format definitions
- Schema specifications

**Correctness Validation:**
- "Verify data completeness"
- "Check for errors"
- "Confirm success conditions"

**Decision Structure (not criteria):**
```markdown
<L1>
If condition met:
  Take path A
Else:
  Take path B
</L1>

condition_threshold: 0.85  <!-- L2: the threshold is tunable -->
```

The **structure** of the decision is L1. The **criteria** for the decision is L2.

### Examples

**Code Review Skill:**
```markdown
<L1>
### Step 1: Load Code
Load the code to review from file/paste/repository.

### Step 2: Analyze Structure
Examine architecture, organization, patterns.

### Step 3: Check Quality
Review style, naming, documentation, error handling.
### Step 4: Generate Report
Produce structured feedback with findings.
</L1>
```

These steps MUST happen in this order for correctness.

## Layer 2 (Surface) - Tunable

### Definition
Optimizations, heuristics, and knowledge that improve performance but aren't required for correctness.

### Identification Patterns

**Numeric Parameters:**
- `retry_count: 3` ← tunable
- `timeout_seconds: 30` ← tunable
- `cache_ttl_minutes: 5` ← tunable
- `threshold: 0.85` ← tunable
- `batch_size: 100` ← tunable

**Conditional Shortcuts:**
- "Skip validation if filename matches pattern"
- "Use cache if response size < 1MB"
- "Fast path for known input types"

**Wisdoms (Tacit Knowledge):**
- "[2025-12-15] For scanned PDFs, use 300 DPI for better OCR"
- "[2025-12-20] API rate limits reset at midnight UTC"
- "[2025-12-22] Large datasets (>10K rows) need streaming"

**Heuristics:**
- "If first request fails with 429, wait 60s before retry"
- "For files >10MB, increase timeout to 120s"
- "When response is HTML, strip tags before processing"

**Examples and Documentation:**
- Usage examples
- Troubleshooting tips
- Best practices notes
- Explanation text

### Examples

**API Integration Skill:**
```markdown
## Request Configuration

retry_count: 3  <!-- L2: tunable -->
timeout_seconds: 30  <!-- L2: tunable -->
backoff_multiplier: 2  <!-- L2: tunable -->

## Heuristics

- If status code 429 (rate limit), wait retry_count * backoff_multiplier seconds
- For endpoints returning >1MB, skip caching
- For POST/PUT requests, always validate payload before sending

## Wisdoms

*[Empty initially - will populate through evolution]*
```

All of this is L2 - removing it doesn't break the skill, just makes it less optimized.

## Common Mistakes

### Mistake 1: Over-tagging
**DON'T:**
```markdown
<L1>
Retry up to 3 times with 30 second timeout
</L1>
```

The numbers are L2! Only the retry structure is L1:

**DO:**
```markdown
<L1>
Retry up to max_retries with timeout_seconds
</L1>

max_retries: 3  <!-- L2: tunable -->
timeout_seconds: 30  <!-- L2: tunable -->
```

### Mistake 2: Under-tagging

**DON'T:**
```markdown
Parse input file, validate schema, send request, check status
```

No L1 tags means ES can modify the core workflow!

**DO:**
```markdown
<L1>
### Step 1: Parse Input
Load and parse the input file.

### Step 2: Validate Schema
Check against specification.

### Step 3: Send Request
Execute the API call.

### Step 4: Check Status
Verify response code is 2xx.
</L1>
```

### Mistake 3: Tagging Documentation

**DON'T:**
```markdown
<L1>
This skill fetches data from REST APIs with retry logic and caching.
It's useful for...
</L1>
```

Documentation is L2 (can be improved without breaking skill).

## Decision Tree

```
Is this a sequential step that MUST happen?
├─ YES → Probably L1
│   └─ Can I skip it without breaking the skill?
│       ├─ NO → Definitely L1
│       └─ YES → Actually L2
│
└─ NO → Probably L2
    └─ Is it a parameter value, heuristic, or wisdom?
        ├─ YES → Definitely L2
        └─ NO → Re-examine (might be L1 decision structure)
```

## Quick Reference

| Type | Layer | Reasoning |
|------|-------|-----------|
| "Step 1: Parse input" | L1 | Required workflow step |
| `retry_count: 3` | L2 | Tunable parameter |
| "If X then Y else Z" (structure) | L1 | Decision flow logic |
| `threshold: 0.85` (criteria) | L2 | Decision threshold value |
| Wisdom: "Use 300 DPI for scans" | L2 | Tacit knowledge |
| Input/output schema | L1 | Contract definition |
| Usage example | L2 | Documentation |
| Error handling structure | L1 | Required correctness |
| Timeout value | L2 | Performance tuning |
