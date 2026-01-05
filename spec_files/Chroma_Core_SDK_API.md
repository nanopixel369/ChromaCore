# ChromaCore SDK API Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [ChromaQuery](./Chroma_Query_Spec.md)
- [Spectral Plugins](./Spectral_Plugins_Spec.md)

---

## Installation

```bash
pip install chromacore
```

## Core Class: ChromaCore

### Initialization

```python
from chromacore import ChromaCore

core = ChromaCore(
    db_path: str = "chromacore.db",
    config_path: str | None = None,
    auto_init: bool = True
)
```

**Parameters:**
- `db_path`: Path to SQLite database file (created if it doesn't exist).
- `config_path`: Path to `chroma.toml` (optional, uses defaults if `None`).
- `auto_init`: Run initialization (schema setup, plugin loading) on instantiation.

**Returns:** `ChromaCore` instance.

---

## Storage Operations

### store()

```python
def store(
    hashtags: list[str],
    label: str,
    content: str,
    metadata: dict | None = None,
    mode_name: str = "Adaptive"
) -> str
```

**Parameters:**
- `hashtags`: List of hashtag strings (must pass Chromatic Gravity validation).
- `label`: Human-readable title/summary.
- `content`: The actual data being stored.
- `metadata`: Optional JSON-serializable dict for application data.
- `mode_name`: Memory mode (`Sparse`|`Adaptive`|`Spacey`|`Eidetic`).

**Returns:** `entry_id` (UUID string).

**Raises:**
- `ValidationError`: Hashtag validation failed (e.g., missing Core tag).
- `StorageError`: Database operation failed.

**Example:**
```python
entry_id = core.store(
    hashtags=["#python", "#async", "#stdlib", "#typing", 
              "#dataclass", "#enum", "#protocol", "#v3.13"],
    label="Python 3.13 async improvements",
    content="Details about new async features...",
    metadata={"source": "docs.python.org", "version": "3.13"}
)
```

### update_node()

```python
def update_node(
    entry_id: str,
    label: str | None = None,
    content: str | None = None,
    metadata: dict | None = None
) -> bool
```

**Returns:** `True` if the node was found and updated.

### get_node()

```python
def get_node(
    entry_id: str
) -> dict | None
```

**Parameters:**
- `entry_id`: UUID of the node to retrieve

**Returns:** 
- Node dictionary with all fields if found
- `None` if entry_id doesn't exist

**Raises:**
- `QueryError`: Database access failed

**Example:**
```python
node = core.get_node("550e8400-e29b-41d4-a716-446655440000")
if node:
    print(f"Label: {node['label']}")
    print(f"Content: {node['content']}")
```

### delete_node()

```python
def delete_node(
    entry_id: str
) -> bool
```

**Parameters:**
- `entry_id`: UUID of the node to delete

**Returns:** 
- `True` if node was found and deleted
- `False` if entry_id didn't exist

**Raises:**
- `StorageError`: Database operation failed

**Example:**
```python
deleted = core.delete_node("550e8400-e29b-41d4-a716-446655440000")
if deleted:
    print("Node successfully removed")
```

**Note:** Deletion is permanent. Deleted nodes do not appear in queries and cannot be recovered unless you restore from a backpack snapshot.

---

### suggest_hashtags()

```python
def suggest_hashtags(self, content: str) -> list[str]:
    """
    Scan content for words matching Semantic Stack hashtags.
    Case-insensitive, ignores punctuation.
    """
```

**Parameters:**
- `content`: The text content to scan.

**Returns:**
- List of matching hashtags (e.g., `["#python", "#async"]`) found in the content. Matches are exact (case-insensitive) against the defined Semantic Stack.

**Note:** This method is a helper for client-side suggestions. It does not modify internal state or automatically apply tags.

---


## Retrieval Operations

### query()

```python
def query(
    hashtags: list[str],
    k: int = 5,
    max_distance: float | None = None,
    temporal_range: tuple[int, int] | None = None,
    metadata_filters: dict | None = None,
    include_rotten: bool = False,
    score_weights: dict | None = None,
    profile: str = "default"
) -> list[dict]
```

**Parameters:**
- `hashtags`: Query tags for semantic positioning.
- `k`: Number of results.
- `score_weights`: Optional override for Mnemosyne weights (e.g., `{"relevance": 0.8, "recency": 0.1, "strength": 0.1}`).

**Returns:** List of node dictionaries ordered by score.

---

## Plugin System

### register_plugin()

```python
def register_plugin(plugin: SpectralPlugin) -> None
```

**Example:**
```python
from my_plugins import MySchemaPlugin

core.register_plugin(MySchemaPlugin(config={"threshold": 0.9}))
core.register_plugin(MyQueryProfile())
```

---

## Backpack Management

### export_backpack()

```python
def export_backpack(
    backpack_id: str,
    output_path: str,
    app_metadata: dict
) -> None
```

**Parameters:**
- `backpack_id`: ID of the backpack to export.
- `output_path`: Filename for the `.bpack` artifact.
- `app_metadata`: Metadata including `app_id` and `app_version` for compatibility gating.

### import_backpack()

```python
def import_backpack(
    bpack_path: str,
    collision_policy: str = "AUTO_SUFFIX",
    target_app_id: str | None = None
) -> str
```

**Returns:** The `backpack_id` of the newly imported backpack.

### list_backpacks()

```python
def list_backpacks() -> list[dict]
```

**Returns:** List of backpack metadata dictionaries

**Example:**
```python
backpacks = core.list_backpacks()
for bp in backpacks:
    print(f"{bp['id']}: {bp['display_name']} ({bp['node_count']} nodes)")
```

**Returns structure:**
```python
[
    {
        "id": "dev-patch_bpack",
        "display_name": "Dev Patch",
        "node_count": 1523,
        "created_at": "2025-12-01T10:30:00Z",
        "last_modified": "2025-12-20T15:45:00Z"
    },
    ...
]
```

---

## Exceptions

- **`ValidationError`**: Raised when inputs (hashtags, schema data) fail validation rules.
- **`StorageError`**: Raised on database failures or integrity violations.
- **`QueryError`**: Raised when retrieval fails or profile is invalid.
- **`PluginError`**: Raised on plugin registration, dependency, or hook failures.
- **`BackpackError`**: Raised on import/export failures (e.g., app compatibility mismatch).

---

## Type Definitions

### QueryResult

```python
from typing import TypedDict, NotRequired

class QueryResult(TypedDict):
    # Core fields
    entry_id: str
    node_id: str
    label: str
    content: str
    hashtags: list[str]
    
    # Coordinate fields
    color_L: int
    color_a: int
    color_b: int
    
    # Temporal fields
    created_at: int  # Unix timestamp
    last_accessed: int  # Unix timestamp
    access_count: int
    
    # Memory scoring
    score: float  # Combined score (0.0-1.0)
    relevance: float  # Distance-based (0.0-1.0)
    recency: float  # Time-based (0.0-1.0)
    strength_norm: float  # Access-based (0.0-1.0)
    
    # Lifecycle
    state: str  # "ACTIVE" | "ASCENDED" | "ROTTEN"
    decay_enabled: int  # 1 or 0
    
    # Metadata
    metadata: dict  # Application-specific JSON
    
    # Plugin fields (if plugins add columns)
    # These are NotRequired since they depend on installed plugins
    # Example: author: NotRequired[str]
```

**Plugin-Added Fields:**

If your application has plugins that extend the schema (via `SchemaExtension`), those fields will also appear in query results. For example, if you have an `AuthorPlugin` that adds an `author` column, results will include:

```python
{
    "entry_id": "...",
    "label": "...",
    "author": "Jane Developer",  # Plugin-added field
    ...
}
```
