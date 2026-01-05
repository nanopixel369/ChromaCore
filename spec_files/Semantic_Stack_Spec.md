# Semantic Stack Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Chromatic Gravity](./Chromatic_Gravity_Spec.md) - Geometric foundation
- [Chroma Nodes](./Chroma_Nodes_Specification.md) - Storage for hashtags

---

## Overview

The Semantic Stack is a fixed-size collection of 10,000 evenly-distributed color anchors in L\*a\*b\* color space. Each anchor can be assigned a hashtag (semantic identifier), creating a permanent binding between a hashtag and a spatial coordinate.

---

## Generation Algorithm

### Stage 1: Halton Sequence Generation

Generate 10,000 anchors using Halton low-discrepancy sequences:

```math
L* = halton(i, base=2) × 100           (range: 0-100)
a* = halton(i, base=3) × 255 - 128     (range: -128 to +127)  
b* = halton(i, base=5) × 255 - 128     (range: -128 to +127)
```

Where `i` ranges from 1 to 10,000.

**Halton function:**

```
halton(index, base):
    f = 1
    r = 0
    while index > 0:
        f = f / base
        r = r + f × (index % base)
        index = floor(index / base)
    return r
```

---

### Stage 2: Distance Calculation

Calculate Euclidean distance from center of L\*a\*b\* space:

```math
center = (L=50, a=0, b=0)
distance = sqrt((L - 50)² + a² + b²)
```

---

### Stage 3: Zone Assignment

Sort all anchors by distance (ascending), then assign zones by index:

- **Indices 0-999** (10%): Core zone
- **Indices 1000-7499** (65%): Mid zone  
- **Indices 7500-9999** (25%): Outer zone

---

### Stage 4: Mass Calculation

Calculate mass value based on position within zone. Mass increases linearly from inner edge to outer edge of each zone.

**Core Zone (0.2 → 0.5):**

```
min_dist = minimum distance in Core
max_dist = maximum distance in Core
t = (anchor.distance - min_dist) / (max_dist - min_dist)
mass = 0.2 + (0.3 × t)
```

**Mid Zone (1.5 → 2.5):**

```
min_dist = minimum distance in Mid
max_dist = maximum distance in Mid
t = (anchor.distance - min_dist) / (max_dist - min_dist)
mass = 1.5 + (1.0 × t)
```

**Outer Zone (0.6 → 1.0):**

```
min_dist = minimum distance in Outer
max_dist = maximum distance in Outer
t = (anchor.distance - min_dist) / (max_dist - min_dist)
mass = 0.6 + (0.4 × t)
```

---

### Stage 5: Sort Within Zones by Hue

Calculate hue angle for each anchor:

```
hue = atan2(b, a)
```

Separate anchors by zone, sort each zone by hue (ascending), then concatenate: Core + Mid + Outer.

---

### Stage 6: Assign Sequential IDs

After all sorting is complete, assign sequential IDs starting from 1.

---

## Output Format

**File:** `semantic_stack_v1.json`

**Schema:**

```json
{
  "version": "1.0.0",
  "generated_at": "2025-12-18T12:34:56Z",
  "total_anchors": 10000,
  "anchors": [
    {
      "id": 1,
      "zone": "Core",
      "L": 12,
      "a": -6,
      "b": 9,
      "mass": 0.23,
      "hashtag": null
    },
    {
      "id": 2,
      "zone": "Core",
      "L": 16,
      "a": -2,
      "b": 11,
      "mass": 0.26,
      "hashtag": null
    }
    // ... 9998 more
  ]
}
```

**Field Specifications:**

| Field  | Type    | Description                                                 |
| ------ | ------- | ----------------------------------------------------------- |
| `id`   | integer | Sequential ID (1-10000)                                     |
| `zone` | string  | "Core", "Mid", or "Outer"                                   |
| `L`    | integer | Lightness (0-100), rounded to nearest integer               |
| `a`    | integer | Green-red axis (-128 to +127), rounded to nearest integer   |
| `b`    | integer | Blue-yellow axis (-128 to +127), rounded to nearest integer |
| `mass` | float   | Gravitational mass (0.2-2.5), rounded to 2 decimals         |
| `hashtag`  | null    | Empty by default, filled at runtime                         |

---

## Validation Requirements

The generator script **must** validate the following:

### 1. Zone Distribution

- Exactly 1000 Core anchors
- Exactly 6500 Mid anchors
- Exactly 2500 Outer anchors
- **Total:** 10,000 anchors

### 2. Mass Gradients

For each zone, verify mass increases monotonically from inner to outer edge:

- Core: First anchor ≈ 0.2, last anchor ≈ 0.5
- Mid: First anchor ≈ 1.5, last anchor ≈ 2.5
- Outer: First anchor ≈ 0.6, last anchor ≈ 1.0

### 3. No Duplicate Colors

Every (L, a, b) tuple must be unique. No two anchors can have identical coordinates.

### 4. Zone Hashtags Present

Every anchor must have a `zone` field with value "Core", "Mid", or "Outer".

### 5. Sequential IDs

IDs must be sequential integers from 1 to 10,000 with no gaps.

### 6. Integer Coordinates

L, a, and b values must be integers (no decimal points). Only mass should have decimals (2 places).

---

## Usage Notes

- **Immutable:** This file is generated once and never modified.
- **Python-only:** ChromaCore v1.0 is Python-only. Future language ports are not in scope for this specification.
- **Backpack initialization:** Every new backpack starts with a copy of this master file.
- **No regeneration:** Halton sequences are deterministic, but we freeze the output to ensure perfect cross-platform compatibility.

---

**End of Specification**
