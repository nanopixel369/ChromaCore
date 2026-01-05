# SYSTEM_ARCHITECTURE.md

## Overview

**ChromaCore** is a pure Python 3.14 library providing a semantic memory engine for AI applications. It implements a deterministic, physics-based memory storage system where information is clustered by meaning (hashtags) rather than arbitrary keys.

**Primary Responsibilities:**
- **Deterministic Storage:** Mapping semantic tags to fixed L*a*b* color coordinates using "Chromatic Gravity".
- **Organic Memory:** Simulating memory decay, strengthening, and rot via the "Mnemosyne Engine".
- **Spatial Retrieval:** Retrieving content via k-Nearest Neighbors (k-NN) in semantic space.
- **Extensible Architecture:** Supporting domain-specific schema and logic via "Spectral Plugins".
- **Portability:** Encapsulating memory graphs into application-scoped "Backpacks" (`.bpack`).

**Non-Goals:**
- It is **not** a standalone server (it is an embedded library).
- It is **not** a vector embedding database (it uses explicit semantic tags).
- It does **not** process binary blobs (text and metadata only).

## Architecture Summary

ChromaCore follows a layered architecture designed for integration into host applications (Agents, CLIs, Web Services).

**Key Components:**
- **Core Engine (Internal):** Implements immutable physics (Gravity, Orbit, Decay).
- **Semantic Stack (Data):** A fixed vocabulary of 10,000 spatial anchors providing the coordinate system.
- **Chroma Nodes (Persistence):** A SQLite-based storage layer for the memory graph.
- **Chroma Packer (Distribution):** Manages `.bpack` export/import and local backups.
- **Spectral Plugins (Extension):** standardized hooks for Schema, Storage, and Query customization.
- **Public SDK (API):** The surface area for developer interaction.

**Control Flow:**
- **Write:** `SDK` -> `Plugin (Pre-Storage)` -> `Gravity` (Compute Coords) -> `Nodes` (Persist) -> `Plugin (Post-Storage)`.
- **Read:** `SDK` -> `Query Profile` (Parse) -> `Gravity` (Compute Query Coords) -> `Nodes` (k-NN) -> `Mnemosyne` (Score) -> `Profile` (Post-Process).

## Modules and Packages

### `chromacore` (Top-level Package)
- **`chromacore.api`**: Public-facing SDK functions (`ChromaCore` class).
- **`chromacore.exceptions`**: Custom exception hierarchy (`ChromaError`, `ValidationError`, `PluginError`).

### `chromacore.gravity`
- **Purpose:** Implements the "Chromatic Gravity" physics engine.
- **Responsibility:** Calculates (L, a, b) coordinates from hashtag combinations.
- **Concurrency:** CPU-bound. Optimized for Python 3.14 Free-Threading (No-GIL) to allow parallel coordinate computation.

### `chromacore.stack`
- **Purpose:** Manages the Semantic Stack (10,000 anchor points).
- **Responsibility:** Fast O(1) lookups of anchors by hashtag.
- **Implementation:** In-memory `dict` loaded from `semantic_stack_v1.msgpack`.

### `chromacore.mnemosyne`
- **Purpose:** Implements memory lifecycle logic (Decay, Rot, Ascension).
- **Responsibility:** Scoring nodes based on Recency, Relevance, and Strength.
- **Logic:** Stateless functions that compute scores based on Node state.

### `chromacore.nodes`
- **Purpose:** Persistence layer.
- **Responsibility:** SQLite database management (`nodes.db`), schema migration, and transaction handling.
- **Key Tech:** SQLite 3.45+ (WAL mode), PEP 750 (T-Strings) for SQL safety.

### `chromacore.plugins`
- **Purpose:** Extension machinery.
- **Responsibility:** Plugin discovery, dependency validation, and hook execution.
- **Safety:** Sandboxed `PluginAPI` to prevent direct DB corruption.

### `chromacore.packer`
- **Purpose:** Backpack lifecycle management.
- **Responsibility:** Exporting/Importing `.bpack` (tar.zst) artifacts, managing local incremental backups.

## Public Python API Specification

### `chromacore.api.ChromaCore`

The main entry point class.

```python
class ChromaCore:
    def __init__(self, db_path: str = "chromacore.db", config_path: str | None = None) -> None:
        """Initialize the engine with database and configuration."""
        ...

    def store(
        self, 
        hashtags: list[str], 
        label: str, 
        content: str, 
        metadata: dict | None = None,
        mode_name: str = "Adaptive"
    ) -> str:
        """
        Store a new memory entry.
        
        Args:
            hashtags: List of 8+ semantic tags (must satisfy Zone rules).
            label: Human-readable title.
            content: Text content.
            metadata: Application-specific JSON data.
            mode_name: Mnemosyne lifecycle mode ("Sparse", "Adaptive", "Eidetic").
            
        Returns:
            UUID string of the new entry.
        """
        ...

    def query(
        self,
        hashtags: list[str],
        k: int = 5,
        max_distance: float | None = None,
        temporal_range: tuple[int, int] | None = None,
        include_rotten: bool = False,
        score_weights: dict | None = None,
        profile: str = "default"
    ) -> list[dict]:
        """
        Retrieve memories semantically related to the hashtags.
        
        Args:
            hashtags: Query context.
            k: Result count.
            score_weights: Mnemosyne weight overrides.
            profile: Query Profile name (plugin) to use.
            
        Returns:
            List of node dictionaries sorted by Score.
        """
        ...
    
    def suggest_hashtags(self, content: str) -> list[str]:
        """Scan content for Semantic Stack matches."""
        ...

    def register_plugin(self, plugin: SpectralPlugin) -> None:
        """Register a new plugin instance."""
        ...
```

## Data Models and Schemas

### `chromacore.models.Node`

Represents a single memory unit.

```python
from typing import TypedDict, Any

class Node(TypedDict):
    # Core Identity & Position
    entry_id: str               # UUIDv4
    node_id: str                # Hash of coordinates
    color_L: float              # 0-100
    color_a: float              # -128 to +127
    color_b: float              # -128 to +127
    
    # Semantic Content
    hashtags: list[str]
    label: str
    content: str
    metadata: dict[str, Any]    # JSON
    
    # Temporal & Memory State
    created_at: int             # Unix timestamp
    last_accessed: int          # Unix timestamp
    access_count: int
    strength_raw: float         # Unbounded growth
    decay_health: float         # 0.0-1.0
    ascension: bool             # Permanence flag
    rotten: bool                # Rot flag
    decay_enabled: bool         # Toggle
    mode_name: str              # "Adaptive", etc.
    version: int                # Optimistic lock
```

## Workflows and Control Flow

### 1. Store Operation Pipeline
1.  **Validation:** `Gravity` checks hashtag constraints (Zones).
2.  **Plugin Pre-Hook:** Sequential execution of `StorageHook.pre_storage_filter`.
3.  **Coordinate Calc:** `Gravity` computes (L, a, b).
4.  **Transaction:** `Nodes` module performs atomic INSERT into SQLite.
5.  **Plugin Post-Hook:** Parallel execution of `StorageHook.post_storage` (side effects).

### 2. Query Operation Pipeline
1.  **Profile Parsing:** `QueryProfile.parse_input` transforms raw input (if using profile).
2.  **Coordinate Calc:** `Gravity` computes query origin.
3.  **Spatial Search:** SQL R-Tree query for candidates within `max_distance`.
4.  **Mnemosyne Scoring:**
    - Calculate `Recency` (Exponential decay).
    - Calculate `Relevance` (Distance-based).
    - Calculate `Strength` (Normalized).
    - Compute `Weighted Score`.
5.  **Plugin Scoring:** `QueryProfile.custom_scoring` adds domain signals.
6.  **Ranking:** Sort candidates by total score.
7.  **Access Update:** Update `last_accessed` and `strength` for returned nodes.
8.  **Profile Post-Processing:** `QueryProfile.post_process` formats results.

### 3. Backpack Export Pipeline
1.  **Inventory:** Scan `backpacks/<id>/` recursively.
2.  **Manifest:** Generate `bpack.manifest.json` with Blake3 hashes.
3.  **Compress:** Create `payload/` structure -> `tar` -> `zstd`.
4.  **Output:** Write `<id>.bpack`.

## Configuration and Environment

### `chroma.toml`
User-facing configuration file. Validated on load.

```toml
[storage]
db_path = "chromacore.db"
wal_mode = true

[memory]
enabled = true
default_mode = "Adaptive"

[backup]
enabled = true
retention_count = 3
```

### Environment Variables
- `CHROMA_STORAGE_DB_PATH`: Override DB location.
- `CHROMA_SYSTEM_LOG_LEVEL`: Set logging verbosity.

## Plugin Ecosystem

Plugins interact via the safe `PluginAPI`.

### Hook Types
- **SchemaExtension:** Add columns to `nodes` table (One-time, permanent).
- **StorageHook:** Intercept/Transform data during `store()`.
- **QueryProfile:** Customize query parsing, ranking, and formatting.
- **TemporalProcessor:** Scheduled background tasks (maintenance, archiving).

## Storage & Persistence

### SQLite Schema (`nodes` table)
| Column | Type | Description |
|--------|------|-------------|
| `entry_id` | TEXT PK | UUID |
| `node_id` | TEXT | Coordinate Hash |
| `color_L/a/b` | REAL | Position |
| `hashtags` | TEXT | JSON Array |
| `strength_raw` | REAL | Mnemosyne State |
| `decay_health` | REAL | Mnemosyne State |
| `ascension` | INTEGER | Bool |
| `rotten` | INTEGER | Bool |

### Indexes
- Spatial: `(color_L, color_a, color_b)` (R-Tree preferred).
- Temporal: `created_at`, `last_accessed`.
- Lifecycle: `(rotten, ascension, decay_health)` for pruning.

## Error Handling

- **`ChromaError`**: Base class.
- **`ValidationError`**: Invalid hashtags or inputs.
- **`StorageError`**: DB corruption or constraints.
- **`PluginError`**: Hook failure (isolated, does not crash Core).
- **`BackpackError`**: Import/Export compatibility failures.

## Testing and Validation

- **Determinism:** `Gravity` algorithm verified against "Test Vectors" (Fixed Inputs -> Fixed Outputs).
- **Backpack Compatibility:** Verify `export -> import` cycle preserves exact byte hashes.
- **Memory Math:** Unit tests for Decay/Strengthening curves.
- **Concurrency:** Thread-safety verification for Free-Threaded usage.
