# Chroma Nodes Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Chromatic Gravity](./Chromatic_Gravity_Spec.md) - Position calculation
- [Mnemosyne Engine](./Mnemosyne_Engine_Spec.md) - Memory lifecycle
- [Spectral Plugins](./Spectral_Plugins_Spec.md) - Schema extensions

---

## Overview

Chroma Nodes are the fundamental storage units in ChromaCore. Each node represents a piece of information positioned at a specific L\*a\*b\* coordinate in color space, determined by Chromatic Gravity blending of its hashtags.

Nodes are **disk-first** - they persist in embedded SQL databases and are loaded into memory only for active queries. This design enables ChromaCore to scale to millions of entries on commodity hardware.

**Integrated Memory System:** ChromaCore includes a sophisticated memory lifecycle engine (Mnemosyne) by default. This system tracks recency, strength, and decay for each node, enabling organic memory evolution. Users who want static knowledge bases can disable the memory system via configuration.

---

## Core Principles

1. **Disk-First Persistence:** Nodes live on disk by default, memory is for active operations only
2. **Coordinate Determinism:** Identical hashtag combinations always produce identical node positions
3. **Zero Collisions:** Multiple entries at the same coordinate are allowed and expected (k-NN retrieval handles this naturally)
4. **Transaction Safety:** All writes are atomic and isolated
5. **Organic Memory Evolution:** Nodes strengthen with use, decay with neglect, and can achieve permanence
6. **Horizontal Scalability:** Each backpack is independent and app-scoped.

---

## Node Schema

### Core Fields

Every node must contain these fields:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `entry_id` | TEXT | Unique identifier for this entry (UUID) | Yes |
| `node_id` | TEXT | ChromaCore node address (from Chromatic Gravity) | Yes |
| `color_L` | REAL | Lightness coordinate (0-100) | Yes |
| `color_a` | REAL | Green-red axis (-128 to +127) | Yes |
| `color_b` | REAL | Blue-yellow axis (-128 to +127) | Yes |
| `hashtags` | TEXT/JSON | Array of hashtag strings used to position this node | Yes |
| `label` | TEXT | Human-readable title/summary | Yes |
| `content` | TEXT | The actual data being stored | Yes |
| `created_at` | INTEGER | Unix timestamp (seconds) of creation | Yes |
| `last_accessed` | INTEGER | Unix timestamp (seconds) of last retrieval | Yes |
| `metadata` | TEXT/JSON | Extensible field for application-specific data | No |

---

### Memory System Fields (Mnemosyne)

**These fields are ALWAYS present** (memory system enabled by default):

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `strength_raw` | REAL | ≥ 0 | Cumulative use-based strength (grows unbounded) |
| `decay_health` | REAL | [0, 1] | Freshness indicator (1=fresh, 0=completely decayed) |
| `ascension` | INTEGER | 0/1 | Permanence flag (1=permanent, immune to decay/rot) |
| `rotten` | INTEGER | 0/1 | Rot flag (1=eligible for archival/deletion) |
| `decay_enabled` | INTEGER | 0/1 | Per-node decay override (0=frozen, 1=normal decay) |
| `mode_name` | TEXT | - | Memory mode: Sparse\|Adaptive\|Spacey\|Eidetic |
| `access_count` | INTEGER | ≥ 0 | Total number of retrievals (for analytics) |
| `version` | INTEGER | ≥ 0 | Optimistic concurrency control counter |

**Temporal Integration:**

All memory signals (recency, strength decay, health decay, rot detection) are interconnected through time:
- `created_at` defines the node's absolute age
- `last_accessed` drives recency calculations
- Time deltas between these timestamps feed into all decay curves
- Temporal proximity modulates strength reinforcement

---

### Storage Backend Specifications

ChromaCore v1.0 is **Python-only**. Future language ports are not in scope for this specification.

### Python Implementation (SQLite)

**Schema:**
```sql
CREATE TABLE nodes (
    -- Core Identity & Position
    entry_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    color_L REAL NOT NULL CHECK (color_L >= 0 AND color_L <= 100),
    color_a REAL NOT NULL CHECK (color_a >= -128 AND color_a <= 127),
    color_b REAL NOT NULL CHECK (color_b >= -128 AND color_b <= 127),
    
    -- Semantic & Content
    hashtags TEXT NOT NULL,  -- JSON array
    label TEXT NOT NULL,
    content TEXT NOT NULL,
    
    -- Temporal Foundation
    created_at INTEGER NOT NULL,
    last_accessed INTEGER NOT NULL,
    
    -- Memory System State
    strength_raw REAL NOT NULL DEFAULT 0.0,
    decay_health REAL NOT NULL DEFAULT 1.0 CHECK (decay_health >= 0 AND decay_health <= 1),
    ascension INTEGER NOT NULL DEFAULT 0,
    rotten INTEGER NOT NULL DEFAULT 0,
    decay_enabled INTEGER NOT NULL DEFAULT 1,
    mode_name TEXT NOT NULL DEFAULT 'Adaptive',
    access_count INTEGER NOT NULL DEFAULT 0,
    
    -- Extensibility & Concurrency
    metadata TEXT,  -- JSON object
    version INTEGER NOT NULL DEFAULT 0
);

-- Spatial index for k-NN queries
CREATE INDEX idx_color_space ON nodes(color_L, color_a, color_b);

-- Temporal indexes for memory system
CREATE INDEX idx_temporal_created ON nodes(created_at DESC);
CREATE INDEX idx_temporal_accessed ON nodes(last_accessed DESC);

-- Memory system indexes
CREATE INDEX idx_strength ON nodes(strength_raw DESC);
CREATE INDEX idx_decay_health ON nodes(decay_health DESC);
CREATE INDEX idx_ascension ON nodes(ascension);
CREATE INDEX idx_mode ON nodes(mode_name);

-- Composite index for rot detection
CREATE INDEX idx_rot_candidates ON nodes(rotten, ascension, decay_health)
    WHERE ascension = 0 AND rotten = 0;
```

**Connection Settings:**
```python
import sqlite3

conn = sqlite3.connect('chromacore.db')
conn.execute('PRAGMA journal_mode = WAL')        # Write-ahead logging
conn.execute('PRAGMA synchronous = NORMAL')      # Balance safety/speed
conn.execute('PRAGMA cache_size = -64000')       # 64MB cache
conn.execute('PRAGMA temp_store = MEMORY')       # Temp tables in RAM
conn.execute('PRAGMA foreign_keys = ON')         # Enforce relationships
```

---

---

## Memory System Integration

### Field Initialization

**On Node Creation:**
```python
def store_node(
    hashtags: list[str],
    label: str,
    content: str,
    mode_name: str = 'Adaptive',
    metadata: dict = None
) -> str:
    """
    Store a new node with memory system initialized.
    """
    # Validate and compute position
    validate_hashtags(hashtags)
    color = compute_node_color(hashtags)
    
    # Initialize node
    entry_id = str(uuid.uuid4())
    node_id = compute_node_id(color)  # Hash of coordinates
    now = int(time.time())
    
    cursor.execute("""
        INSERT INTO nodes (
            entry_id, node_id,
            color_L, color_a, color_b,
            hashtags, label, content,
            created_at, last_accessed,
            strength_raw, decay_health,
            ascension, rotten, decay_enabled,
            mode_name, access_count,
            metadata, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id, node_id,
        color[0], color[1], color[2],
        json.dumps(hashtags), label, content,
        now, now,                    # Both created and accessed = now
        0.0,                          # strength_raw starts at 0
        1.0,                          # decay_health starts fresh
        0,                            # not ascended
        0,                            # not rotten
        1,                            # decay enabled
        mode_name,
        0,                            # access_count starts at 0
        json.dumps(metadata) if metadata else None,
        0                             # version starts at 0
    ))
    
    conn.commit()
    return entry_id
```

---

### Temporal Calculations

**Time Deltas (in days):**
```python
def get_time_deltas(node: dict, now: int) -> dict:
    """
    Calculate all temporal metrics for a node.
    Returns dict with time-based signals.
    """
    created_at = node['created_at']
    last_accessed = node['last_accessed']
    
    # Time deltas in days (core unit for memory system)
    days_since_creation = (now - created_at) / 86400.0
    days_since_access = (now - last_accessed) / 86400.0
    
    # Derived temporal signals
    absolute_age = days_since_creation
    idle_duration = days_since_access
    
    return {
        'now': now,
        'days_since_creation': days_since_creation,
        'days_since_access': days_since_access,
        'absolute_age': absolute_age,
        'idle_duration': idle_duration
    }
```

---

### Access Pattern Updates

**On Query/Retrieval:**
```python
def update_access_state(entry_id: str, now: int) -> None:
    """
    Update temporal and access state when node is retrieved.
    Uses optimistic locking for concurrency safety.
    """
    # Read current state
    cursor.execute("""
        SELECT last_accessed, access_count, version
        FROM nodes
        WHERE entry_id = ?
    """, (entry_id,))
    
    row = cursor.fetchone()
    if not row:
        return
    
    old_version = row['version']
    
    # Update with optimistic lock
    cursor.execute("""
        UPDATE nodes
        SET 
            last_accessed = ?,
            access_count = access_count + 1,
            version = version + 1
        WHERE entry_id = ? AND version = ?
    """, (now, entry_id, old_version))
    
    if cursor.rowcount == 0:
        # Version conflict - retry
        update_access_state(entry_id, now)
    else:
        conn.commit()
```

---

## Memory Mode Presets

Four built-in modes tune the memory system behavior:

| Mode | Philosophy | Use Case |
|------|-----------|----------|
| **Sparse** | Aggressive pruning, high standards | Resource-constrained, focused knowledge |
| **Adaptive** | Balanced retention, dynamic thresholds | General-purpose, default mode |
| **Spacey** | Privacy-aware, moderate retention | Sensitive data, encryption support |
| **Eidetic** | Maximum retention, minimal decay | Comprehensive archives, research |

**Mode affects:**
- Decay rates (strength_decay_per_day, tau_decay_days)
- Ascension thresholds (permanence_norm)
- Rot criteria (rot_recency_min, rot_strength_min)
- Strength reinforcement rates (strength_hit)

Mode parameters are **not stored per-node** - they're loaded from configuration. The `mode_name` field indicates which parameter set to apply.

---

## Configuration Schema

**Mode Parameters Table:**
```sql
CREATE TABLE mode_params (
    param_name TEXT PRIMARY KEY,
    sparse_val REAL,
    adaptive_val REAL,
    spacey_val REAL,
    eidetic_val REAL,
    type_hint TEXT,       -- real|int|bool
    doc TEXT
);

-- Core temporal parameters
INSERT INTO mode_params(param_name, sparse_val, adaptive_val, spacey_val, eidetic_val, type_hint, doc)
VALUES
-- Time scales (days)
('tau_rec_days', 1.5, 3.0, 2.0, 7.0, 'real', 'Recency timescale in days'),
('tau_decay_days', 60, 90, 60, 120, 'real', 'Decay window for health'),

-- Strength dynamics
('strength_hit', 0.06, 0.10, 0.10, 0.12, 'real', 'Strength increment on use'),
('strength_decay_per_day', 0.15, 0.05, 0.08, 0.02, 'real', 'Idle strength decay rate per day'),

-- Lifecycle thresholds
('ascension_norm', 0.85, 0.80, 0.85, 0.90, 'real', 'Normalized strength for permanence'),
('rot_recency_min', 0.05, 0.03, 0.05, NULL, 'real', 'Min recency before rot eligible'),
('rot_strength_min', 0.20, 0.15, 0.25, NULL, 'real', 'Min normalized strength before rot'),

-- Decay protection
('relevance_decay_protect', 0.30, 0.20, 0.20, 0.10, 'real', 'How relevance slows decay');
```

**Global Configuration:**
```sql
CREATE TABLE engine_config (
    key TEXT PRIMARY KEY,
    val TEXT NOT NULL
);

INSERT INTO engine_config(key, val)
VALUES
('decay_enabled_global', '1'),  -- Master switch for decay system
('default_mode', 'Adaptive'),   -- Default mode for new nodes
('kS_normalization', '5.0');    -- Strength normalization constant
```

---

## CRUD Operations

### Create (Store Node)

Already shown above in "Memory System Integration" section.

---

### Read (Query Node)

**Primary Query Method:** k-Nearest Neighbors (k-NN)
```python
def query_knn(
    hashtags: list[str],
    k: int = 5,
    max_distance: float = None,
    include_rotten: bool = False
) -> list[dict]:
    """
    Query for k nearest neighbors.
    Automatically updates access timestamps.
    """
    # Compute query point
    query_color = compute_node_color(hashtags)
    now = int(time.time())
    
    # Build filter
    filters = []
    if not include_rotten:
        filters.append("rotten = 0")
    
    filter_clause = "WHERE " + " AND ".join(filters) if filters else ""
    
    # Fetch candidates
    cursor.execute(f"""
        SELECT 
            entry_id, node_id,
            color_L, color_a, color_b,
            hashtags, label, content, metadata,
            created_at, last_accessed,
            strength_raw, decay_health,
            ascension, rotten, mode_name,
            access_count
        FROM nodes
        {filter_clause}
    """)
    
    candidates = cursor.fetchall()
    
    # Calculate distances and prepare results
    results = []
    for row in candidates:
        dist = euclidean_distance(
            query_color,
            (row['color_L'], row['color_a'], row['color_b'])
        )
        
        if max_distance is None or dist <= max_distance:
            # Calculate temporal signals
            time_info = get_time_deltas(row, now)
            
            results.append({
                'entry_id': row['entry_id'],
                'node_id': row['node_id'],
                'distance': dist,
                'color': (row['color_L'], row['color_a'], row['color_b']),
                'hashtags': json.loads(row['hashtags']),
                'label': row['label'],
                'content': row['content'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                
                # Temporal data
                'created_at': row['created_at'],
                'last_accessed': row['last_accessed'],
                'days_since_creation': time_info['days_since_creation'],
                'days_since_access': time_info['days_since_access'],
                
                # Memory state
                'strength_raw': row['strength_raw'],
                'decay_health': row['decay_health'],
                'ascension': bool(row['ascension']),
                'rotten': bool(row['rotten']),
                'mode_name': row['mode_name'],
                'access_count': row['access_count']
            })
    
    # Sort by distance and limit
    results.sort(key=lambda x: x['distance'])
    top_k = results[:k]
    
    # Update access timestamps for retrieved nodes
    for result in top_k:
        update_access_state(result['entry_id'], now)
    
    return top_k
```

---

### Update (Modify Node)

**Allowed Updates:**

- `label` - Can be edited
- `content` - Can be edited
- `metadata` - Can be extended
- `last_accessed` - Updated automatically on read
- `access_count` - Updated automatically on read
- Memory system fields - Updated by memory engine algorithms

**Forbidden Updates:**

- `entry_id` - Immutable (primary key)
- `node_id` - Immutable (derived from coordinates)
- `color_L`, `color_a`, `color_b` - Immutable (determined by hashtags via Chromatic Gravity)
- `hashtags` - Immutable (changing tags = different semantic identity = different node)
- `created_at` - Immutable (historical record)

**Rationale for Coordinate Immutability:**

Coordinates are **outputs** of the Chromatic Gravity algorithm applied to a node's hashtags. They are not fields you set arbitrarily. If you want to change a node's position in semantic space, you must create a new node with different hashtags.

**What about hashtag migration?**

Hashtag migration (reassigning a hashtag to a different anchor in the semantic stack) is a **semantic stack operation**, not a node operation. When the semantic stack changes:

1. The ChromaCore migration system identifies all affected nodes
2. Recomputes coordinates using the new anchor positions
3. Updates nodes atomically in a transaction
4. This is a **core system operation**, not exposed to plugins or arbitrary modification
```python
def update_node_content(
    entry_id: str,
    label: str = None,
    content: str = None,
    metadata: dict = None
) -> bool:
    """
    Update mutable content fields.
    Returns True if updated, False if not found.
    """
    updates = []
    params = []
    
    if label is not None:
        updates.append("label = ?")
        params.append(label)
    
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    
    if metadata is not None:
        updates.append("metadata = ?")
        params.append(json.dumps(metadata))
    
    if not updates:
        return False
    
    # Increment version for concurrency
    updates.append("version = version + 1")
    params.append(entry_id)
    
    cursor.execute(f"""
        UPDATE nodes
        SET {', '.join(updates)}
        WHERE entry_id = ?
    """, params)
    
    conn.commit()
    return cursor.rowcount > 0
```

---

### Delete (Remove Node)
```python
def delete_node(entry_id: str) -> bool:
    """
    Permanently delete a node.
    Returns True if deleted, False if not found.
    """
    cursor.execute("""
        DELETE FROM nodes
        WHERE entry_id = ?
    """, (entry_id,))
    
    conn.commit()
    return cursor.rowcount > 0
```

**Soft Delete (Mark as Rotten):**
```python
def mark_rotten(entry_id: str) -> bool:
    """
    Mark node as rotten (eligible for pruning).
    Only affects non-permanent nodes.
    """
    cursor.execute("""
        UPDATE nodes
        SET 
            rotten = 1,
            version = version + 1
        WHERE entry_id = ? AND ascension = 0
    """, (entry_id,))
    
    conn.commit()
    return cursor.rowcount > 0
```

---

## Data Integrity

### Constraints
```sql
-- Coordinate range validation
CHECK (color_L >= 0 AND color_L <= 100)
CHECK (color_a >= -128 AND color_a <= 127)
CHECK (color_b >= -128 AND color_b <= 127)

-- Memory system bounds
CHECK (decay_health >= 0 AND decay_health <= 1)
CHECK (strength_raw >= 0)
CHECK (access_count >= 0)

-- Boolean flags
CHECK (ascension IN (0, 1))
CHECK (rotten IN (0, 1))
CHECK (decay_enabled IN (0, 1))

-- Valid modes
CHECK (mode_name IN ('Sparse', 'Adaptive', 'Spacey', 'Eidetic'))
```

---

### Invariants

**Temporal Consistency:**

- `last_accessed >= created_at` (can't access before creation)
- `created_at <= current_time` (can't create in future)

**Memory State Consistency:**

- If `ascension = 1`, then `rotten = 0` (permanent nodes can't rot)
- If `rotten = 1`, then `ascension = 0` (rotten nodes aren't permanent)

**Validation Function:**
```python
def validate_node_state(node: dict) -> None:
    """
    Validate node state invariants.
    Raises ValueError if invalid.
    """
    # Temporal
    if node['last_accessed'] < node['created_at']:
        raise ValueError("last_accessed before created_at")
    
    # Memory system
    if node['ascension'] and node['rotten']:
        raise ValueError("Node cannot be both ascended and rotten")
    
    if node['decay_health'] < 0 or node['decay_health'] > 1:
        raise ValueError("decay_health must be in [0, 1]")
    
    if node['strength_raw'] < 0:
        raise ValueError("strength_raw cannot be negative")
```

---

## Performance Characteristics

### Write Performance

| Operation | Target Latency | Notes |
|-----------|----------------|-------|
| Single insert | < 10ms | Using WAL mode |
| Batch insert (100) | < 500ms | Use transactions |
| Access update | < 5ms | Optimistic locking |

---

### Read Performance

| Operation | Target Latency | Notes |
|-----------|----------------|-------|
| k-NN query (k=5) | < 50ms | With spatial index |
| k-NN query (k=50) | < 200ms | With spatial index |
| Temporal range scan | < 100ms | With temporal indexes |

---

## Export/Import (Backpack Compatibility)

**Export Format:**
```json
{
  "version": "1.0.0",
  "exported_at": 1702857600,
  "nodes": [
    {
      "entry_id": "550e8400-e29b-41d4-a716-446655440000",
      "node_id": "node_a1b2c3",
      "color": [65.2, 12.8, -8.4],
      "hashtags": ["#python", "#async", "#v3.13"],
      "label": "Python 3.13 async changes",
      "content": "...",
      
      "created_at": 1702857600,
      "last_accessed": 1702944000,
      
      "strength_raw": 2.5,
      "decay_health": 0.87,
      "ascension": false,
      "rotten": false,
      "decay_enabled": true,
      "mode_name": "Adaptive",
      "access_count": 12,
      
      "metadata": {"source": "docs.python.org"}
    }
  ]
}
```

**Import Process:**

1. Validate schema version compatibility
2. Check for `entry_id` collisions
3. Preserve all temporal and memory state
4. Rebuild indexes after bulk import

---

## Configuration Parameters

**Via ChromaConfig:**
```toml
[chroma_nodes]
# Database
db_path = "chromacore.db"
wal_mode = true
cache_size_mb = 64

# Memory System
memory_enabled = true           # Master switch
default_mode = "Adaptive"       # Default for new nodes
kS_normalization = 5.0          # Strength normalization constant

# Content Limits
max_label_length = 500
max_content_size_mb = 1

# Performance
batch_size = 1000
use_rtree = true                # Spatial indexing
```

---

## Implementation Checklist

- [ ] Create database schema with all indexes
- [ ] Implement CRUD operations
- [ ] Add coordinate and memory state validation
- [ ] Implement k-NN query with temporal updates
- [ ] Add optimistic locking for concurrent access
- [ ] Implement mode parameter loading
- [ ] Add export/import with memory state preservation
- [ ] Write unit tests for all operations
- [ ] Benchmark performance (read/write/access updates)
- [ ] Document memory system field semantics

---

**End of Specification**