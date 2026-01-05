# Mnemosyne Engine Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [Chroma Nodes](./Chroma_Nodes_Specification.md) - Storage fields for memory
- [ChromaQuery](./Chroma_Query_Spec.md) - Ranks results via Mnemosyne

---

## Overview

The Mnemosyne Engine is ChromaCore's **organic memory evolution system**. It treats stored knowledge as living memory - strengthening with use, decaying with neglect, and achieving permanence through sustained importance.

Unlike traditional databases where all data is equally accessible, Mnemosyne creates a **dynamic relevance landscape** where recent, strong, and semantically relevant memories naturally surface while weak, stale memories fade into the background or are marked for removal.

ChromaCore v1.0 is **Python-only**. Future language ports are not in scope for this specification.

**Core Philosophy:**

- **Use Strengthens:** Every retrieval reinforces memory strength
- **Neglect Decays:** Unused memories gradually weaken
- **Time Matters:** Recent memories get temporary retrieval advantages
- **Excellence Persists:** Strong memories achieve permanence and immunity to decay
- **Failure Rots:** Weak, stale memories are marked for pruning

The engine is **enabled by default** but can be disabled for static knowledge bases (documentation, archives, reference materials).

---

## Responsibilities

1. **Compute Memory Signals:** Calculate recency, relevance, and normalized strength for each node
2. **Score & Rank:** Combine signals into unified scores for retrieval ordering
3. **Reinforce on Use:** Strengthen memories when accessed
4. **Apply Decay:** Weaken unused memories over time
5. **Manage Lifecycle:** Promote strong memories to permanence, mark weak ones as rotten
6. **Mode Tuning:** Apply different parameter sets based on use case requirements

---

## Configuration Hierarchy

Memory system behavior is controlled by a three-level hierarchy:

### Level 1: Global Toggle (ChromaConfig)

`memory.enabled` in `chroma.toml`:
- `true` (default): Memory system is active, decay cycles run
- `false`: Memory system completely disabled, all nodes treated equally

**Effect when disabled:**
- Decay cycles don't run
- Scoring uses only relevance (distance-based)
- Recency and strength signals are ignored
- Lifecycle transitions (ascension, rot) don't occur

### Level 2: Per-Node Toggle (Chroma Nodes)

`decay_enabled` field on individual nodes:
- `1` (default): Node participates in decay cycles
- `0`: Node is frozen, immune to decay (but not ascended)

**Use cases:**
- Static reference data (documentation, specifications)
- Temporarily freezing important nodes during analysis
- Pinning critical memories

**Interaction with global:**
- If `memory.enabled = false`, per-node settings are ignored (global override)
- If `memory.enabled = true`, per-node settings control individual decay

### Level 3: Query-Time Override

`score_weights` parameter in query:
- Override Mnemosyne weights for a specific query
- Does not affect stored state, only result ranking

**Example:**
```python
# Ignore recency/strength, pure semantic match
results = core.query(
    hashtags=[...],
    score_weights={'relevance': 1.0, 'recency': 0.0, 'strength': 0.0}
)
```

### Precedence Rules

1. Global disabled → all memory features off, regardless of other settings
2. Global enabled + node decay disabled → node doesn't decay but still scores with memory signals
3. Query-time weights → temporary override for that query only

---

## Core Memory Signals

### 1. Recency

**Definition:** How recently the node was accessed.

**Formula:**

```
recency = exp(-Δt_used / τ_rec)
```

Where:
- `Δt_used` = days since last access = `(now - last_accessed) / 86400`
- `τ_rec` = recency timescale in days (mode-dependent)

**Properties:**

- Range: (0, 1] (approaches 0 as time passes, equals 1 when just accessed)
- Exponential decay - recent memories have strong advantage
- Never reaches exactly 0 (asymptotic)

**Interpretation:**

- `recency = 1.0` → Just accessed (maximum freshness)
- `recency = 0.5` → Accessed τ_rec × ln(2) days ago (half-life)
- `recency = 0.05` → Accessed 3τ_rec days ago (very stale)

**Example (Adaptive mode, τ_rec = 3 days):**

```python
def compute_recency(last_accessed: int, now: int, tau_rec_days: float) -> float:
    """
    Calculate recency signal.
    Returns value in (0, 1].
    """
    delta_days = (now - last_accessed) / 86400.0
    return math.exp(-delta_days / tau_rec_days)
```

---

### 2. Relevance

**Definition:** Semantic proximity to the current query.

**Calculation:**

Relevance is computed from the **distance** between query coordinates and node coordinates in L\*a\*b\* space:

```
distance = √((L_q - L_n)² + (a_q - a_n)² + (b_q - b_n)²)

relevance = exp(-distance / σ)
```

Where:
- `(L_q, a_q, b_q)` = query coordinates (from Chromatic Gravity)
- `(L_n, a_n, b_n)` = node coordinates
- `σ` = relevance decay constant (mode-dependent, typically ~20)

**Properties:**

- Range: (0, 1] (1 = exact match, approaches 0 for distant nodes)
- Distance of 0 → relevance = 1.0 (perfect semantic match)
- Already computed during k-NN query

**Interpretation:**

- `relevance = 1.0` → Identity match (exact hashtags)
- `relevance = 0.6` → Related hashtag
- `relevance = 0.1` → Distant hashtag

**Example:**

```python
def compute_relevance(
    query_color: tuple[float, float, float],
    node_color: tuple[float, float, float],
    sigma: float = 20.0
) -> float:
    """
    Calculate relevance from L*a*b* distance.
    Returns value in (0, 1].
    """
    distance = math.sqrt(sum(
        (q - n) ** 2 
        for q, n in zip(query_color, node_color)
    ))
    
    return math.exp(-distance / sigma)
```

---

### 3. Strength

**Definition:** Cumulative use-based reinforcement.

**Raw Strength:**

`strength_raw` is an unbounded value (≥ 0) that grows with each access and decays during idle periods.

**Normalized Strength:**

For scoring, raw strength is normalized to [0, 1) using a saturation curve:

```
strength_norm = strength_raw / (strength_raw + kS)
```

Where:
- `kS` = normalization constant (typically 5.0)

**Properties:**

- Range: [0, 1) (approaches 1 asymptotically, never reaches it)
- `strength_raw = 0` → `strength_norm = 0` (new memory)
- `strength_raw = kS` → `strength_norm = 0.5` (half-saturated)
- `strength_raw = 10×kS` → `strength_norm ≈ 0.91` (highly saturated)

**Why Normalize?**

- Prevents strength from dominating scores for very old, heavily-used nodes
- Creates diminishing returns - 10th access matters less than 1st access
- Bounded range allows balanced weighting with recency and relevance

**Example:**

```python
def normalize_strength(strength_raw: float, kS: float = 5.0) -> float:
    """
    Normalize raw strength to [0, 1) range.
    """
    return strength_raw / (strength_raw + kS)
```

---

### 4. Decay Health

**Definition:** Freshness indicator for rot detection.

**Formula:**

```
decay_health = exp(-Δt_used / τ_decay)
```

Where:
- `Δt_used` = days since last access
- `τ_decay` = decay timescale in days (mode-dependent)

**Properties:**

- Range: (0, 1] (1 = fresh, 0 = completely decayed)
- Separate from strength - tracks absolute freshness
- Used primarily for rot detection

**Purpose:**

While `strength_raw` can be sustained by periodic access, `decay_health` tracks whether the node has been *recently* used. A node might have high strength from historical heavy use but low decay_health if it hasn't been touched in months.

**Example:**

```python
def compute_decay_health(last_accessed: int, now: int, tau_decay_days: float) -> float:
    """
    Calculate decay health signal.
    Returns value in (0, 1].
    """
    delta_days = (now - last_accessed) / 86400.0
    return math.exp(-delta_days / tau_decay_days)
```

---

## Combined Scoring

### Score Formula

The final score combines all three signals:

```
score = w_rel × relevance + w_rec × recency + w_str × strength_norm
```

Where:
- `w_rel` = relevance weight
- `w_rec` = recency weight
- `w_str` = strength weight
- **Constraint:** `w_rel + w_rec + w_str = 1.0` (weights sum to 1)

**Score Range:** [0, 1]

**Mode-Dependent Weights:**

Different modes emphasize different signals:

| Mode | w_rel | w_rec | w_str | Emphasis |
|------|-------|-------|-------|----------|
| **Sparse** | 0.60 | 0.30 | 0.10 | Semantic match dominates |
| **Adaptive** | 0.50 | 0.30 | 0.20 | Balanced |
| **Spacey** | 0.50 | 0.20 | 0.30 | Strength matters more |
| **Eidetic** | 0.40 | 0.20 | 0.40 | Historical use valued |

**Example:**

```python
def compute_score(
    relevance: float,
    recency: float,
    strength_norm: float,
    w_rel: float,
    w_rec: float,
    w_str: float
) -> float:
    """
    Combine signals into unified score.
    Returns value in [0, 1].
    """
    return (
        w_rel * relevance +
        w_rec * recency +
        w_str * strength_norm
    )
```

---

## Strength Dynamics

### Reinforcement (On Access)

When a node is retrieved, its strength increases:

```
strength_raw += α_hit × (1 + bonus)
```

Where:
- `α_hit` = base strength increment (mode-dependent)
- `bonus` = recency-based bonus (see below)

**Recency Bonus:**

If the node has high recency when accessed, it gets a bonus reinforcement:

```
if recency >= recency_bonus_threshold:
    bonus = recency_bonus_gain × recency
else:
    bonus = 0
```

**Rationale:** Repeated access to a fresh memory (working memory pattern) strengthens it more than sporadic access to a stale memory.

**Example:**

```python
def reinforce_strength(
    node: dict,
    recency: float,
    alpha_hit: float,
    recency_bonus_threshold: float,
    recency_bonus_gain: float
) -> float:
    """
    Increase strength on access.
    Returns updated strength_raw.
    """
    # Base increment
    increment = alpha_hit
    
    # Recency bonus
    if recency >= recency_bonus_threshold:
        bonus = recency_bonus_gain * recency
        increment *= (1.0 + bonus)
    
    new_strength = node['strength_raw'] + increment
    return new_strength
```

---

### Decay (During Idle)

When a node is NOT accessed, its strength decays:

```
strength_raw *= exp(-β_strength × Δt_used × decay_factor)
```

Where:
- `β_strength` = strength decay rate per day (mode-dependent)
- `Δt_used` = days since last access
- `decay_factor` = relevance protection factor (see below)

**Relevance Protection:**

High-relevance nodes decay slower:

```
decay_factor = (1 - λ_rel × relevance)
```

Where:
- `λ_rel` = relevance decay protection coefficient (mode-dependent, typically 0.2-0.3)

**Rationale:** Semantically relevant nodes (even if not recently accessed) should decay slower than irrelevant nodes.

**Example:**

```python
def apply_strength_decay(
    strength_raw: float,
    delta_days: float,
    beta_strength: float,
    relevance: float,
    lambda_rel: float
) -> float:
    """
    Apply exponential decay to strength.
    Returns updated strength_raw.
    """
    decay_factor = 1.0 - (lambda_rel * relevance)
    decay_amount = beta_strength * delta_days * decay_factor
    
    new_strength = strength_raw * math.exp(-decay_amount)
    return new_strength
```

---

### Health Decay (During Idle)

Decay health also decays, but independently:

```
decay_health *= exp(-Δt_used / τ_decay)
```

This is a **simple exponential decay** without relevance protection or other modifiers.

**Example:**

```python
def apply_health_decay(
    decay_health: float,
    delta_days: float,
    tau_decay_days: float
) -> float:
    """
    Apply exponential decay to health.
    Returns updated decay_health.
    """
    new_health = decay_health * math.exp(-delta_days / tau_decay_days)
    return max(0.0, min(1.0, new_health))  # Clamp to [0, 1]
```

---

## Lifecycle Transitions

### Ascension (Permanence)

**Trigger:**

A node achieves permanence when its normalized strength exceeds the ascension threshold:

```
if strength_norm >= ascension_norm:
    ascension = True
```

Where:
- `ascension_norm` = mode-dependent threshold (typically 0.80-0.90)

**Effects:**

1. `ascension` flag set to `True`
2. Node becomes **immune to decay** (strength_raw and decay_health stop decaying)
3. Node becomes **immune to rot** (cannot be marked rotten)
4. Node can still increase in strength if accessed
5. Node can still be scored lower than non-permanent nodes if relevance is low

**Rationale:**

Permanent nodes represent **crystallized knowledge** - hashtags and entries that have proven their value through sustained use. They're protected from decay but can still fall in search rankings if they're not relevant to the query.

**Example:**

```python
def check_ascension(strength_norm: float, ascension_norm: float) -> bool:
    """
    Check if node should achieve permanence.
    """
    return strength_norm >= ascension_norm
```

---

### Rot Detection

**Trigger:**

A node is marked as rotten when it satisfies **both** conditions:

```
if (recency <= rot_recency_min) AND (strength_norm <= rot_strength_min) AND (NOT ascension):
    rotten = True
```

Where:
- `rot_recency_min` = minimum recency threshold (mode-dependent, typically 0.03-0.05)
- `rot_strength_min` = minimum strength threshold (mode-dependent, typically 0.15-0.25)

**Conditions Explained:**

1. **Low Recency:** Node hasn't been accessed in a long time
2. **Low Strength:** Node was never strongly reinforced
3. **Not Permanent:** Permanent nodes are immune

**Effects:**

1. `rotten` flag set to `True`
2. Node is **excluded from queries by default** (unless explicitly requested)
3. Node is **eligible for archival or deletion** during maintenance
4. Node can be "rescued" if accessed again (flag cleared, strength reinforced)

**Eidetic Mode Exception:**

In Eidetic mode, `rot_recency_min` and `rot_strength_min` are set to `NULL` (rot disabled).

**Example:**

```python
def check_rot(
    recency: float,
    strength_norm: float,
    ascension: bool,
    rot_recency_min: float,
    rot_strength_min: float
) -> bool:
    """
    Check if node should be marked rotten.
    Returns True if eligible for rot.
    """
    if ascension:
        return False  # Permanent nodes can't rot
    
    if rot_recency_min is None or rot_strength_min is None:
        return False  # Rot disabled (Eidetic mode)
    
    return (recency <= rot_recency_min) and (strength_norm <= rot_strength_min)
```

---

## Mode Presets

Four built-in modes with distinct personalities:

### Sparse Mode

**Philosophy:** Aggressive pruning, only the strongest survive.

**Use Case:** Resource-constrained environments, focused knowledge bases.

**Characteristics:**

- **Fast decay:** `β_strength = 0.15` (high daily decay rate)
- **High standards:** `ascension_norm = 0.85` (hard to achieve permanence)
- **Aggressive rot:** `rot_recency_min = 0.05`, `rot_strength_min = 0.20`
- **Relevance dominant:** `w_rel = 0.60` (semantic match is king)
- **Short memory:** `τ_rec = 1.5 days`, `τ_decay = 60 days`

**Result:** Only frequently-accessed, highly-relevant memories persist.

---

### Adaptive Mode (Default)

**Philosophy:** Balanced retention, adapts to usage patterns.

**Use Case:** General-purpose applications, personal knowledge management.

**Characteristics:**

- **Moderate decay:** `β_strength = 0.05` (gentle daily decay)
- **Balanced thresholds:** `ascension_norm = 0.80`
- **Moderate rot:** `rot_recency_min = 0.03`, `rot_strength_min = 0.15`
- **Balanced scoring:** `w_rel = 0.50`, `w_rec = 0.30`, `w_str = 0.20`
- **Medium memory:** `τ_rec = 3.0 days`, `τ_decay = 90 days`

**Result:** Retains working memory while pruning truly unused content.

---

### Spacey Mode

**Philosophy:** Privacy-aware, moderate retention with encryption support.

**Use Case:** Sensitive data, personal information, private thoughts.

**Characteristics:**

- **Moderate-fast decay:** `β_strength = 0.08`
- **High standards:** `ascension_norm = 0.85`
- **Moderate rot:** `rot_recency_min = 0.05`, `rot_strength_min = 0.25`
- **Strength valued:** `w_str = 0.30` (historical use matters)
- **Short-medium memory:** `τ_rec = 2.0 days`, `τ_decay = 60 days`

**Special Feature:** Supports per-node encryption (application layer responsibility).

**Result:** Sensitive memories that prove useful persist, others decay faster.

---

### Eidetic Mode

**Philosophy:** Maximum retention, minimal decay, comprehensive archives.

**Use Case:** Research databases, documentation, reference materials.

**Characteristics:**

- **Slow decay:** `β_strength = 0.02` (very gentle decay)
- **High permanence bar:** `ascension_norm = 0.90` (requires sustained excellence)
- **No rot:** `rot_recency_min = NULL`, `rot_strength_min = NULL` (disabled)
- **Strength dominant:** `w_str = 0.40` (historical use heavily weighted)
- **Long memory:** `τ_rec = 7.0 days`, `τ_decay = 120 days`

**Result:** Near-permanent retention, only extreme neglect causes decay.

---

## Mode Parameter Table

**Complete Parameter Set:**

| Parameter | Sparse | Adaptive | Spacey | Eidetic | Unit |
|-----------|--------|----------|--------|---------|------|
| **Time Scales** |
| `tau_rec_days` | 1.5 | 3.0 | 2.0 | 7.0 | days |
| `tau_decay_days` | 60 | 90 | 60 | 120 | days |
| **Strength Dynamics** |
| `strength_hit` | 0.06 | 0.10 | 0.10 | 0.12 | increment |
| `strength_decay_per_day` | 0.15 | 0.05 | 0.08 | 0.02 | rate/day |
| `recency_bonus_threshold` | 0.70 | 0.70 | 0.70 | 0.60 | recency |
| `recency_bonus_gain` | 1.0 | 1.0 | 1.0 | 1.0 | multiplier |
| **Lifecycle Thresholds** |
| `ascension_norm` | 0.85 | 0.80 | 0.85 | 0.90 | strength_norm |
| `rot_recency_min` | 0.05 | 0.03 | 0.05 | NULL | recency |
| `rot_strength_min` | 0.20 | 0.15 | 0.25 | NULL | strength_norm |
| **Decay Protection** |
| `relevance_decay_protect` | 0.30 | 0.20 | 0.20 | 0.10 | coefficient |
| **Scoring Weights** |
| `w_rel` | 0.60 | 0.50 | 0.50 | 0.40 | weight |
| `w_rec` | 0.30 | 0.30 | 0.20 | 0.20 | weight |
| `w_str` | 0.10 | 0.20 | 0.30 | 0.40 | weight |

**Storage:**

```sql
INSERT INTO mode_params(param_name, sparse_val, adaptive_val, spacey_val, eidetic_val, type_hint, doc)
VALUES
-- Time scales
('tau_rec_days', 1.5, 3.0, 2.0, 7.0, 'real', 'Recency timescale in days'),
('tau_decay_days', 60, 90, 60, 120, 'real', 'Decay window for health'),

-- Strength dynamics
('strength_hit', 0.06, 0.10, 0.10, 0.12, 'real', 'Strength increment on use'),
('strength_decay_per_day', 0.15, 0.05, 0.08, 0.02, 'real', 'Idle strength decay rate per day'),
('recency_bonus_threshold', 0.70, 0.70, 0.70, 0.60, 'real', 'Recency needed for bonus'),
('recency_bonus_gain', 1.0, 1.0, 1.0, 1.0, 'real', 'Bonus gain multiplier'),

-- Lifecycle thresholds
('ascension_norm', 0.85, 0.80, 0.85, 0.90, 'real', 'Normalized strength for permanence'),
('rot_recency_min', 0.05, 0.03, 0.05, NULL, 'real', 'Min recency before rot eligible'),
('rot_strength_min', 0.20, 0.15, 0.25, NULL, 'real', 'Min normalized strength before rot'),

-- Decay protection
('relevance_decay_protect', 0.30, 0.20, 0.20, 0.10, 'real', 'How relevance slows decay'),

-- Scoring weights
('w_rel', 0.60, 0.50, 0.50, 0.40, 'real', 'Score weight: relevance'),
('w_rec', 0.30, 0.30, 0.20, 0.20, 'real', 'Score weight: recency'),
('w_str', 0.10, 0.20, 0.30, 0.40, 'real', 'Score weight: strength');
```

---

## Core Algorithms

### Query-Time Processing

**Full Pipeline:**

```python
def query_with_memory(
    hashtags: list[str],
    k: int = 5,
    mode_name: str = 'Adaptive',
    include_rotten: bool = False
) -> list[dict]:
    """
    Query with full memory system processing.
    """
    # Step 1: Load mode configuration
    config = load_mode_config(mode_name)
    now = int(time.time())
    
    # Step 2: Compute query coordinates
    query_color = compute_node_color(hashtags)
    
    # Step 3: Fetch candidate nodes (k-NN spatial query)
    candidates = fetch_spatial_candidates(query_color, k * 3, include_rotten)
    
    # Step 4: Score each candidate
    scored = []
    for node in candidates:
        # Calculate temporal signals
        recency = compute_recency(node['last_accessed'], now, config['tau_rec_days'])
        relevance = compute_relevance(query_color, 
                                      (node['color_L'], node['color_a'], node['color_b']))
        
        # Normalize strength
        strength_norm = normalize_strength(node['strength_raw'], kS=5.0)
        
        # Combine into score
        score = compute_score(
            relevance, recency, strength_norm,
            config['w_rel'], config['w_rec'], config['w_str']
        )
        
        scored.append({
            **node,
            'recency': recency,
            'relevance': relevance,
            'strength_norm': strength_norm,
            'score': score
        })
    
    # Step 5: Sort by score
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    # Step 6: Take top k
    results = scored[:k]
    
    # Step 7: Update access state for returned nodes
    for node in results:
        update_on_access(node['entry_id'], now, recency, config)
    
    return results


def update_on_access(
    entry_id: str,
    now: int,
    recency: float,
    config: dict
) -> None:
    """
    Update node state when accessed.
    Uses optimistic locking.
    """
    # Read current state
    cursor.execute("""
        SELECT strength_raw, version, ascension
        FROM nodes
        WHERE entry_id = ?
    """, (entry_id,))
    
    row = cursor.fetchone()
    if not row:
        return
    
    old_version = row['version']
    old_strength = row['strength_raw']
    ascension = bool(row['ascension'])
    
    # Calculate new strength (if not permanent)
    if not ascension:
        new_strength = reinforce_strength(
            {'strength_raw': old_strength},
            recency,
            config['strength_hit'],
            config['recency_bonus_threshold'],
            config['recency_bonus_gain']
        )
    else:
        new_strength = old_strength  # Permanent nodes don't decay, but also don't strengthen
    
    # Update with optimistic lock
    cursor.execute("""
        UPDATE nodes
        SET 
            last_accessed = ?,
            access_count = access_count + 1,
            strength_raw = ?,
            version = version + 1
        WHERE entry_id = ? AND version = ?
    """, (now, new_strength, entry_id, old_version))
    
    if cursor.rowcount == 0:
        # Version conflict - retry
        update_on_access(entry_id, now, recency, config)
    else:
        conn.commit()
```

---

### Decay Cycle (Background Task)

**Scheduled Process (runs periodically, e.g., daily):**

```python
def decay_cycle(mode_name: str = None) -> dict:
    """
    Apply decay to all non-permanent nodes.
    If mode_name is None, applies per-node mode settings.
    Returns statistics.
    """
    now = int(time.time())
    
    # Fetch all non-permanent, decay-enabled nodes
    cursor.execute("""
        SELECT 
            entry_id, last_accessed, 
            strength_raw, decay_health,
            mode_name, version
        FROM nodes
        WHERE ascension = 0 AND decay_enabled = 1
    """)
    
    nodes = cursor.fetchall()
    
    stats = {
        'processed': 0,
        'strength_decayed': 0,
        'health_decayed': 0,
        'errors': 0
    }
    
    for node in nodes:
        try:
            # Load mode config
            config = load_mode_config(node['mode_name'] if not mode_name else mode_name)
            
            # Calculate time delta
            delta_days = (now - node['last_accessed']) / 86400.0
            
            if delta_days <= 0:
                continue  # Node just accessed, skip
            
            # Apply strength decay (with average relevance assumption of 0.5)
            # Note: True relevance-aware decay requires query context
            new_strength = apply_strength_decay(
                node['strength_raw'],
                delta_days,
                config['strength_decay_per_day'],
                relevance=0.5,  # Baseline assumption
                lambda_rel=config['relevance_decay_protect']
            )
            
            # Apply health decay
            new_health = apply_health_decay(
                node['decay_health'],
                delta_days,
                config['tau_decay_days']
            )
            
            # Update with optimistic lock
            cursor.execute("""
                UPDATE nodes
                SET 
                    strength_raw = ?,
                    decay_health = ?,
                    version = version + 1
                WHERE entry_id = ? AND version = ?
            """, (new_strength, new_health, node['entry_id'], node['version']))
            
            if cursor.rowcount > 0:
                stats['processed'] += 1
                if new_strength < node['strength_raw']:
                    stats['strength_decayed'] += 1
                if new_health < node['decay_health']:
                    stats['health_decayed'] += 1
            
        except Exception as e:
            stats['errors'] += 1
            print(f"Error decaying node {node['entry_id']}: {e}")
    
    conn.commit()
    return stats
```

---

### Lifecycle Check (Background Task)

**Runs after decay cycle:**

```python
def lifecycle_check(mode_name: str = None) -> dict:
    """
    Check all nodes for ascension and rot transitions.
    Returns statistics.
    """
    now = int(time.time())
    kS = 5.0  # Normalization constant
    
    stats = {
        'ascensions': 0,
        'rots': 0,
        'errors': 0
    }
    
    # Fetch all nodes
    cursor.execute("""
        SELECT 
            entry_id, last_accessed,
            strength_raw, decay_health,
            ascension, rotten,
            mode_name, version
        FROM nodes
    """)
    
    nodes = cursor.fetchall()
    
    for node in nodes:
        try:
            config = load_mode_config(node['mode_name'] if not mode_name else mode_name)
            
            # Calculate signals
            delta_days = (now - node['last_accessed']) / 86400.0
            recency = compute_recency(node['last_accessed'], now, config['tau_rec_days'])
            strength_norm = normalize_strength(node['strength_raw'], kS)
            
            # Check ascension (if not already permanent)
            if not node['ascension']:
                if check_ascension(strength_norm, config['ascension_norm']):
                    cursor.execute("""
                        UPDATE nodes
                        SET ascension = 1, rotten = 0, version = version + 1
                        WHERE entry_id = ? AND version = ?
                    """, (node['entry_id'], node['version']))
                    
                    if cursor.rowcount > 0:
                        stats['ascensions'] += 1
                        continue  # Skip rot check if just ascended
            
            # Check rot (if not already rotten and not permanent)
            if not node['rotten'] and not node['ascension']:
                if check_rot(
                    recency,
                    strength_norm,
                    node['ascension'],
                    config.get('rot_recency_min'),
                    config.get('rot_strength_min')
                ):
                    cursor.execute("""
                        UPDATE nodes
                        SET rotten = 1, version = version + 1
                        WHERE entry_id = ? AND version = ?
                    """, (node['entry_id'], node['version']))
                    
                    if cursor.rowcount > 0:
                        stats['rots'] += 1
            
        except Exception as e:
            stats['errors'] += 1
            print(f"Error checking lifecycle for node {node['entry_id']}: {e}")
    
    conn.commit()
    return stats
```

---

## Configuration Management

### Loading Mode Config

```python
def load_mode_config(mode_name: str) -> dict:
    """
    Load mode parameters from database.
    Returns dict with all parameters.
    """
    cursor.execute(f"""
        SELECT param_name, {mode_name.lower()}_val as value
        FROM mode_params
    """)
    
    rows = cursor.fetchall()
    config = {}
    
    for row in rows:
        param = row['param_name']
        value = row['value']
        
        # Convert to appropriate type
        if value is None:
            config[param] = None
        elif '.' in str(value):
            config[param] = float(value)
        else:
            config[param] = int(value)
    
    return config
```

---

### Global Settings

```python
def get_global_setting(key: str, default: str = None) -> str:
    """
    Retrieve global engine setting.
    """
    cursor.execute("""
        SELECT val FROM engine_config WHERE key = ?
    """, (key,))
    
    row = cursor.fetchone()
    return row['val'] if row else default


def set_global_setting(key: str, val: str) -> None:
    """
    Set global engine setting.
    """
    cursor.execute("""
        INSERT OR REPLACE INTO engine_config(key, val)
        VALUES (?, ?)
    """, (key, val))
    
    conn.commit()
```

---

## Disabling Memory System

**Per-Node:**

```python
def disable_decay(entry_id: str) -> bool:
    """
    Disable decay for specific node.
    """
    cursor.execute("""
        UPDATE nodes
        SET decay_enabled = 0, version = version + 1
        WHERE entry_id = ?
    """, (entry_id,))
    
    conn.commit()
    return cursor.rowcount > 0
```

**Globally:**

```python
def disable_memory_system() -> None:
    """
    Disable memory system globally.
    Sets flag that decay cycle respects.
    """
    set_global_setting('decay_enabled_global', '0')
```

**Decay Cycle Respects Global Setting:**

```python
def decay_cycle_with_global_check(mode_name: str = None) -> dict:
    """
    Decay cycle that respects global disable flag.
    """
    # Check global flag
    if get_global_setting('decay_enabled_global', '1') == '0':
        return {'processed': 0, 'skipped': 'global_disabled'}
    
    # Run normal decay cycle
    return decay_cycle(mode_name)
```

---

## Statistics & Monitoring

### Memory System Stats

```python
def get_memory_stats() -> dict:
    """
    Get comprehensive memory system statistics.
    """
    stats = {}
    
    # Total nodes
    cursor.execute("SELECT COUNT(*) as total FROM nodes")
    stats['total_nodes'] = cursor.fetchone()['total']
    
    # Permanent nodes
    cursor.execute("SELECT COUNT(*) as count FROM nodes WHERE ascension = 1")
    stats['permanent_nodes'] = cursor.fetchone()['count']
    
    # Rotten nodes
    cursor.execute("SELECT COUNT(*) as count FROM nodes WHERE rotten = 1")
    stats['rotten_nodes'] = cursor.fetchone()['count']
    
    # Decay disabled nodes
    cursor.execute("SELECT COUNT(*) as count FROM nodes WHERE decay_enabled = 0")
    stats['decay_disabled'] = cursor.fetchone()['count']
    
    # Mode distribution
    cursor.execute("""
        SELECT mode_name, COUNT(*) as count
        FROM nodes
        GROUP BY mode_name
    """)
    stats['mode_distribution'] = {row['mode_name']: row['count'] 
                                  for row in cursor.fetchall()}
    
    # Strength distribution
    cursor.execute("""
        SELECT 
            AVG(strength_raw) as avg_strength,
            MIN(strength_raw) as min_strength,
            MAX(strength_raw) as max_strength
        FROM nodes
    """)
    row = cursor.fetchone()
    stats['strength'] = {
        'average': row['avg_strength'],
        'min': row['min_strength'],
        'max': row['max_strength']
    }
    
    # Health distribution
    cursor.execute("""
        SELECT 
            AVG(decay_health) as avg_health,
            MIN(decay_health) as min_health
        FROM nodes
    """)
    row = cursor.fetchone()
    stats['health'] = {
        'average': row['avg_health'],
        'min': row['min_health']
    }
    
    return stats
```

---

## Performance Considerations

### Query-Time Overhead

**Memory processing adds:**
- Signal calculations: ~0.1ms per node
- Strength reinforcement: ~1ms per accessed node
- Database updates: ~5ms per accessed node with optimistic locking

**Total overhead:** ~5-10ms for typical k=5 query.

---

### Background Processing

**Decay Cycle:**
- Processes all non-permanent nodes
- With 100k nodes: ~10-30 seconds (depends on hardware)
- Should run during low-traffic periods (e.g., nightly)

**Lifecycle Check:**
- Processes all nodes
- Similar performance to decay cycle
- Can run immediately after decay cycle

---

### Optimization Strategies

1. **Batch Updates:** Process decay in batches of 1000 nodes per transaction
2. **Incremental Decay:** Only process nodes accessed within last N days
3. **Parallel Processing:** Use connection pool for multi-threaded decay
4. **Cached Config:** Load mode configs once, cache in memory
5. **Skip Fresh Nodes:** Skip nodes accessed within last hour

---

## Implementation Checklist

- [ ] Implement all signal calculation functions
- [ ] Implement scoring algorithm
- [ ] Implement strength reinforcement
- [ ] Implement decay algorithms (strength + health)
- [ ] Implement lifecycle checks (ascension + rot)
- [ ] Create mode parameter loader
- [ ] Implement query-time processing pipeline
- [ ] Implement decay cycle background task
- [ ] Implement lifecycle check background task
- [ ] Add global enable/disable controls
- [ ] Implement statistics collection
- [ ] Write unit tests for all formulas
- [ ] Benchmark query-time overhead
- [ ] Benchmark background processing time
- [ ] Document mode selection guidelines

---

## Appendix: Mathematical Properties

### Signal Ranges

| Signal | Range | Type | Notes |
|--------|-------|------|-------|
| `recency` | (0, 1] | Continuous | Never 0, asymptotic |
| `relevance` | (0, 1] | Continuous | 1 = exact match |
| `strength_raw` | [0, ∞) | Continuous | Unbounded |
| `strength_norm` | [0, 1) | Continuous | Bounded, never reaches 1 |
| `decay_health` | (0, 1] | Continuous | 1 = fresh |
| `score` | [0, 1] | Continuous | Weighted combination |

---

### Half-Life Examples

**Recency (τ_rec = 3 days):**
- After 3 × ln(2) ≈ 2.08 days: recency = 0.5
- After 6.24 days: recency = 0.25
- After 9.36 days: recency = 0.125

**Decay Health (τ_decay = 90 days):**
- After 90 × ln(2) ≈ 62.4 days: health = 0.5
- After 124.8 days: health = 0.25

---

### Strength Saturation

With kS = 5.0:

| strength_raw | strength_norm | Interpretation |
|--------------|---------------|----------------|
| 0 | 0.000 | Brand new |
| 1 | 0.167 | Lightly used |
| 5 | 0.500 | Half-saturated |
| 10 | 0.667 | Well-established |
| 25 | 0.833 | Heavily used |
| 50 | 0.909 | Near maximum |
| 100 | 0.952 | Extremely saturated |

---

**End of Specification**
