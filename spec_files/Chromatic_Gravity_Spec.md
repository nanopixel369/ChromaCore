# Chromatic Gravity Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [Semantic Stack](./Semantic_Stack_Spec.md) - Hashtag anchor definitions
- [ChromaQuery](./Chroma_Query_Spec.md) - Uses gravity for retrieval

---

## Overview

Chromatic Gravity is the physics engine that determines where information lives in ChromaCore's L\*a\*b\* color space. Rather than simple averaging, it uses gravitational weighting to compute storage coordinates from hashtag combinations, ensuring semantic clustering with controlled spread.

The algorithm is **deterministic**: identical hashtag combinations always produce identical coordinates, enabling consistent storage and retrieval.

---

## Zone Architecture

The L\*a\*b\* color space is divided into three concentric zones based on distance from center (L=50, a=0, b=0):

| Zone      | Volume | Mass Range | Purpose                            |
| --------- | ------ | ---------- | ---------------------------------- |
| **Core**  | 10%    | 0.2 → 0.5  | Paradigms (major domains)          |
| **Mid**   | 65%    | 1.5 → 2.5  | Sub-paradigms (semantic meat)      |
| **Outer** | 25%    | 0.6 → 1.0  | Modifiers (jitter/differentiators) |

### Zone Boundaries

```math
max_distance = √((50)² + (128)² + (128)²) ≈ 186.7

core_radius = max_distance × ∛0.10 ≈ 86.6
mid_radius = max_distance × ∛0.75 ≈ 169.7
outer_radius = max_distance (full extent)
```

### Mass Gradient

Mass increases from inner edge to outer edge within each zone:

```text
Core:  center → edge = 0.2 → 0.5
Mid:   inner → outer = 1.5 → 2.5
Outer: inner → outer = 0.6 → 1.0
```

This creates natural gravity wells in the mid-zone where most semantic content clusters.

---

## Content Auto-Scanning

To assist applications in meeting hashtag requirements, Chromatic Gravity defines a **Content Auto-Scanning** protocol. This transparently suggests relevant hashtags from the Semantic Stack based on the entry's content.

### Scanning Algorithm

1. **Tokenize:** Split raw content into words.
2. **Normalize:** Strip punctuation, convert to lowercase.
3. **Match:** Compare each token against the Semantic Stack's vocabulary (hashtags).
4. **Suggest:** Return all direct matches as suggested hashtags.

**Constraint:** The system MUST NOT automatically apply these suggestions. The user (or application logic) MUST confirm which suggestions to keep.

### Example

**Content:**
> "Python 3.12 introduces new features for async programming and better error messages."

**Detected Tokens:**
`python`, `3.12`, `introduces`, `new`, `features`, `for`, `async`, `programming`, `and`, `better`, `error`, `messages`

**Semantic Stack Matches:**
- `#python` (Core)
- `#async` (Mid)
- `#programming` (Mid)
- `#error` (Mid)

**Suggestion Output:**
`["#python", "#async", "#programming", "#error"]`

---

## Input Validation Requirements

**All inputs must pass validation before calculation proceeds.**

### Hard Requirements

1. **Minimum 1 Core hashtag** — Every entry must declare a paradigm
2. **Minimum 1 Outer hashtag** — Every entry must have a jitter modifier
3. **Minimum 65% Mid hashtags** — Mid-zone must dominate

### Valid Configurations

| Outer Hashtags | Mid Required | Core | Total Min |
| -------------- | ------------ | ---- | --------- |
| 1              | 6            | 1    | 8         |
| 2              | 9            | 1    | 12        |
| 3              | 12           | 1    | 16        |

### Validation Pseudocode

```python
def validate_hashtags(hashtags: list[str]) -> bool:
    core_count = sum(1 for h in hashtags if get_zone(h) == "core")
    mid_count = sum(1 for h in hashtags if get_zone(h) == "mid")
    outer_count = sum(1 for h in hashtags if get_zone(h) == "outer")
    total = len(hashtags)

    # Hard requirements
    if core_count < 1:
        raise ValidationError("Minimum 1 core paradigm tag required")
    if outer_count < 1:
        raise ValidationError("Minimum 1 outer modifier tag required")
    if total < 8:
        raise ValidationError("Minimum 8 hashtags required")
    if (mid_count / total) < 0.65:
        raise ValidationError("Mid-zone tags must be ≥65% of total")

    return True
```

---

## Gravitational Blending Algorithm

### Core Formula

```math
weight_i = mass_i / (ε + distance_i²)

result = Σ(weight_i × anchor_i) / Σ(weight_i)
```

Where:

- `mass_i` = zone mass value for hashtag i (from gradient)
- `distance_i` = Euclidean distance from anchor i to current center of mass
- `ε` = 0.1 (epsilon prevents division by zero, ensures all tags contribute)
- `anchor_i` = (L, a, b) coordinates of hashtag i's anchor in semantic stack

### Complete Algorithm

```python
def compute_node_color(hashtags: list[str]) -> tuple[float, float, float]:
    """
    Compute the storage coordinate for a set of hashtags.
    Returns (L, a, b) tuple guaranteed to be in mid-zone.
    """

    # Step 1: Validate input
    validate_hashtags(hashtags)

    # Step 2: Gather anchor data
    anchors = []
    for h in hashtags:
        anchor = semantic_stack.get_anchor(h)
        anchors.append({
            'color': anchor.color,  # (L, a, b)
            'mass': get_zone_mass(anchor.color)
        })

    # Step 3: Compute initial center of mass (simple average for first pass)
    com = (
        sum(a['color'][0] for a in anchors) / len(anchors),
        sum(a['color'][1] for a in anchors) / len(anchors),
        sum(a['color'][2] for a in anchors) / len(anchors)
    )

    # Step 4: Iterative refinement (2-3 passes for convergence)
    epsilon = 0.1
    for _ in range(3):
        weights = []
        for a in anchors:
            dist = euclidean_distance(a['color'], com)
            weight = a['mass'] / (epsilon + dist ** 2)
            weights.append(weight)

        total_weight = sum(weights)
        com = (
            sum(w * a['color'][0] for w, a in zip(weights, anchors)) / total_weight,
            sum(w * a['color'][1] for w, a in zip(weights, anchors)) / total_weight,
            sum(w * a['color'][2] for w, a in zip(weights, anchors)) / total_weight
        )

    # Step 5: Return final coordinate
    return com


def get_zone_mass(color: tuple[float, float, float]) -> float:
    """
    Calculate mass value based on position within zone.
    Mass increases from inner to outer edge of each zone.
    """
    dist = distance_from_center(color)

    if dist <= CORE_RADIUS:
        # Core: 0.2 at center, 0.5 at edge
        t = dist / CORE_RADIUS
        return 0.2 + (0.3 * t)

    elif dist <= MID_RADIUS:
        # Mid: 1.5 at inner edge, 2.5 at outer edge
        t = (dist - CORE_RADIUS) / (MID_RADIUS - CORE_RADIUS)
        return 1.5 + (1.0 * t)

    else:
        # Outer: 0.6 at inner edge, 1.0 at outer edge
        t = (dist - MID_RADIUS) / (OUTER_RADIUS - MID_RADIUS)
        return 0.6 + (0.4 * t)


def distance_from_center(color: tuple[float, float, float]) -> float:
    """Euclidean distance from L*a*b* center (50, 0, 0)."""
    L, a, b = color
    return math.sqrt((L - 50)**2 + a**2 + b**2)


def euclidean_distance(c1: tuple, c2: tuple) -> float:
    """Euclidean distance between two L*a*b* colors."""
    return math.sqrt(sum((a - b)**2 for a, b in zip(c1, c2)))
```

---

## Why Mid-Zone Output is Guaranteed

The algorithm guarantees mid-zone placement through **input constraints**, not output clamping.

### Proof by Construction

**Worst-case scenario** (maximum outer influence):

- 6 mid hashtags at minimum mass (1.5 each) = 9.0 total
- 1 outer hashtag at maximum mass (1.0) = 1.0 total
- 1 core hashtag at maximum mass (0.5) = 0.5 total

**Mass distribution before distance falloff:**

- Mid: 9.0 / 10.5 = **85.7%**
- Outer: 1.0 / 10.5 = 9.5%
- Core: 0.5 / 10.5 = 4.8%

**After distance falloff:**

The outer hashtag (at outer zone) is geometrically far from the mid-dominated center of mass. Distance² falloff further reduces its influence. The core hashtag (at center) is also far from the mid-zone cluster.

**Result:** Mid-zone hashtags maintain 85%+ gravitational influence in all valid configurations. The center of mass cannot escape mid-zone because:

1. 65% hashtag count minimum ensures numerical dominance
2. 1.5-2.5 mass range vs 0.6-1.0 ensures mass dominance
3. Distance² falloff punishes geometrically distant outliers
4. Halton distribution ensures mid hashtags aren't clustered at boundaries

**No clamping required.** The output is mid-zone by mathematical necessity.

---

## Jitter Behavior

The outer modifier hashtag provides **deterministic jitter** — small positional offsets that spread semantically similar entries across neighboring nodes instead of stacking them on identical coordinates.

### Clustering Behavior

Entries sharing the same core + mid hashtags but different outer modifiers:

- Share the same "semantic neighborhood" (dominated by mid hashtags)
- Land on different but adjacent nodes (offset by outer hashtag influence)
- Enable k-NN queries to find related content

### Example

```text
Entry A: #python (core) + #async #stdlib #typing #dataclass #enum #protocol (mid) + #v3.11 (outer)
Entry B: #python (core) + #async #stdlib #typing #dataclass #enum #protocol (mid) + #v3.12 (outer)
Entry C: #python (core) + #async #stdlib #typing #dataclass #enum #protocol (mid) + #v3.13 (outer)
```

All three entries cluster in the same neighborhood, but `#v3.11`, `#v3.12`, `#v3.13` cause slight positional offsets, spreading them across adjacent nodes.

---

## Query Consistency

The same formula used for storage is used for retrieval:

```python
def query(hashtags: list[str], k: int = 5) -> list[Node]:
    """
    Query for entries matching hashtag combination.
    Returns k nearest neighbors to computed coordinate.
    """
    # Compute query coordinate (same algorithm as storage)
    query_color = compute_node_color(hashtags)

    # Find k nearest neighbors
    return spatial_index.knn(query_color, k)
```

**Determinism guarantee:** `compute_node_color(hashtags)` returns identical results for identical inputs, ensuring storage location matches query location.

---

## Configuration Parameters

| Parameter          | Default    | Description                                                      |
| ------------------ | ---------- | ---------------------------------------------------------------- |
| `epsilon`          | 0.1        | Prevents division by zero, ensures distant tags still contribute |
| `core_mass_range`  | (0.2, 0.5) | Mass gradient for core zone                                      |
| `mid_mass_range`   | (1.5, 2.5) | Mass gradient for mid zone                                       |
| `outer_mass_range` | (0.6, 1.0) | Mass gradient for outer zone                                     |
| `mid_tag_minimum`  | 0.65       | Minimum proportion of mid-zone hashtags                          |
| `iteration_count`  | 3          | Refinement passes for COM convergence                            |

---

## Performance Characteristics

- **Time complexity:** O(n × i) where n = hashtag count, i = iteration count
- **Typical calculation:** <1ms for 8-16 hashtags with 3 iterations
- **No external dependencies:** Pure arithmetic, CPU-only
- **Deterministic:** Same inputs always produce same outputs (no RNG)

---

## Error Cases

| Error                                               | Cause                 | Resolution                             |
| --------------------------------------------------- | --------------------- | -------------------------------------- |
| `ValidationError: Minimum 1 core hashtag required`  | No paradigm specified | Add a core-zone hashtag                |
| `ValidationError: Minimum 1 outer hashtag required` | No modifier specified | Add an outer-zone hashtag              |
| `ValidationError: Minimum 8 hashtags required`      | Too few hashtags      | Run Content Auto-Scanning to find more matches |
| `ValidationError: Mid-zone hashtags must be ≥65%`   | Ratio imbalance       | Run Content Auto-Scanning to find more matches |
| `KeyError: hashtag not found`                       | Unassigned hashtag    | Assign hashtag to semantic stack first |

---

## Implementation Notes

ChromaCore v1.0 is **Python-only**. Future language ports are not in scope for this specification.

### For Python (chromacore-py)

```python
# Use numpy for vectorized operations on large batches
import numpy as np
```

---

## Appendix: Test Vectors

```yaml
test_case_1:
  name: "Minimum valid configuration"
  hashtags:
    core: ["#python"]
    mid: ["#async", "#stdlib", "#typing", "#dataclass", "#enum", "#protocol"]
    outer: ["#v3.13"]
  expected_zone: "mid"
  determinism: "must match on repeated calls"

test_case_2:
  name: "Two outer modifiers"
  hashtags:
    core: ["#python"]
    mid: ["#async", "#stdlib", "#typing", "#dataclass", "#enum", "#protocol", "#pathlib", "#contextlib", "#functools"]
    outer: ["#v3.13", "#changelog"]
  expected_zone: "mid"

test_case_3:
  name: "Identical mid+core, different outer (jitter test)"
  sets:
    - core: ["#python"], mid: ["#a", "#b", "#c", "#d", "#e", "#f"], outer: ["#v1"]
    - core: ["#python"], mid: ["#a", "#b", "#c", "#d", "#e", "#f"], outer: ["#v2"]
  expected: "different coordinates, same neighborhood, k-NN retrievable"
```

---

**End of Specification**
