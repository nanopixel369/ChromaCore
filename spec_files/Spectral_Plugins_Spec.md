# Spectral Plugins Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [SDK API Specification](./Chroma_Core_SDK_API.md) - Plugin registration
- [Chroma Nodes](./Chroma_Nodes_Specification.md) - Schema hooks

---

---

## Overview

Spectral Plugins are ChromaCore's **extension mechanism**. They allow developers to add domain-specific functionality, customize behavior, and integrate external systems without modifying ChromaCore's immutable core (Chromatic Gravity, Semantic Stack, Mnemosyne formulas).

Plugins operate via **hooks** - predefined injection points in the ChromaCore pipeline where custom logic can execute. All plugin operations go through ChromaCore's **Plugin API** rather than direct database access, ensuring safety, validation, and version compatibility.

**Core Principle:** Plugins add features **on top of** ChromaCore's foundation. They cannot modify core algorithms or data structures that affect backpack compatibility.

---

## Design Principles

### 1. Non-Invasive Extension

Plugins hook into ChromaCore's pipeline at defined extension points:

```
Core Operation (immutable)
  ↓
Plugin Hook (extension point)
  ↓
Core Operation continues
```

ChromaCore remains stable - plugin failures are isolated and logged, but don't crash the system.

### 2. API-Mediated Access

Plugins interact with ChromaCore through the **Plugin API**, not direct database access:

**Safe Pattern:**

```python
# Plugin uses API
existing = self.api.query(hashtags=['#python'], k=5)
self.api.update_metadata(entry_id, {'processed': True})
```

**Unsafe Pattern (blocked):**

```python
# Plugin cannot do this
cursor.execute("UPDATE nodes SET ...")  # ❌ No direct SQL access
```

**Why:** Safety, validation, version compatibility, security boundaries.

### 3. Coordinate Immutability

Plugins **cannot** modify (L, a, b) coordinates directly. Coordinates are deterministic outputs of Chromatic Gravity.

**Plugins cannot:**
- Set color_L, color_a, color_b fields arbitrarily
- Modify hashtags on existing nodes (which would change coordinates)

**Core ChromaCore can:**
- Recompute coordinates when the semantic stack is migrated (core operation, not plugin)

All plugin outputs are validated - coordinate modification attempts are rejected with `PluginError`.

### 4. Migration Transparency

When ChromaCore migrates a hashtag (user action, not plugin):

1. All affected entries are recalculated
2. Coordinates change
3. Entire rows (core fields + plugin columns) move atomically to new positions
4. Plugins don't need migration hooks - ChromaCore handles it

Plugin-added columns are migrated automatically alongside core columns.

### 5. Startup Validation

**One-time dependency check:**

- Plugins declare dependencies on other plugins
- ChromaCore validates at startup (all required plugins present, version compatible)
- If validation fails: System refuses to start, logs error
- If validation succeeds: Plugins activate, no further runtime checks

**After startup:** System assumes all dependencies satisfied.

---

## Plugin Types

Spectral Plugins are organized into **hook categories** based on extension points. All plugins inherit from `SpectralPlugin` base class but implement specific hook interfaces.

### 1. Schema Extensions

**Purpose:** Add application-specific columns to the nodes table.

**Lifecycle:**

- Runs once during ChromaCore initialization
- Columns are permanently added via `ALTER TABLE`
- Cannot be uninstalled (data exists in those columns)

**Hook Interface:**

```python
class SchemaExtension(SpectralPlugin):
    def extend_schema(self) -> dict:
        """
        Define additional columns and indexes.
        
        Returns:
            dict: {
                'columns': {column_name: SQL_type},
                'indexes': [CREATE INDEX statements]
            }
        """
```

**Constraints:**

- Cannot modify core ChromaCore columns
- Column names must not conflict with core schema
- Multiple schema plugins can coexist (additive, no conflicts if different names)

**Example Use Cases:**

- Add paradigm/subdomain hierarchy columns (ChromaBase)
- Add citation tracking columns
- Add version history columns

**Plugin Upgrade Path:**

When a developer wants to upgrade their schema plugin:

```python
class MySchemaPlugin(SchemaExtension):
    VERSION = "2.0.0"
    
    def extend_schema(self) -> dict:
        return {
            'columns': {'new_field': 'TEXT'},
            'indexes': []
        }
    
    def migrate_from(self, old_version: str) -> list[str]:
        """
        Provide migration SQL for upgrades.
        
        Args:
            old_version: Previously installed version
        
        Returns:
            List of SQL statements to execute
        """
        if old_version == "1.0.0":
            return ["ALTER TABLE nodes ADD COLUMN new_field TEXT"]
        return []
```

ChromaCore detects version mismatch on startup and runs migration SQL.

---

### 2. Storage Hooks

**Purpose:** Transform or validate data before/after storage operations.

**Lifecycle:** Runs during every storage operation (insert, update).

**Hook Interface:**

```python
class StorageHook(SpectralPlugin):
    def pre_storage_filter(self, entry: dict) -> dict:
        """
        Transform entry before storage.
        
        Hook: Runs AFTER Chromatic Gravity, BEFORE database insert.
        
        Args:
            entry: Node data (core fields + plugin fields)
        
        Returns:
            Modified entry (coordinates must remain unchanged)
        """
    
    def post_storage(self, entry: dict) -> None:
        """
        Trigger side effects after storage.
        
        Hook: Runs AFTER database insert (read-only).
        
        Args:
            entry: Stored node data
        """
```

**Execution Semantics:**

**pre_storage_filter:**

- **Sequential pipeline** - plugins execute in registration order
- Each plugin receives output of previous plugin
- Order matters - documented behavior

**post_storage:**

- **Parallel execution** - plugins run independently
- Order irrelevant
- Side effects only (cannot modify data)

**Example Use Cases:**

- PII redaction from content
- Data normalization (lowercase hashtags, trim whitespace)
- Duplicate detection
- Webhook notifications after storage
- Backup triggers

---

### 3. Query Profiles

**Purpose:** Customize query interface - parse domain-specific input and transform results.

**Lifecycle:** Runs during query operations when explicitly selected via `profile="name"` parameter.

**Hook Interface:**

```python
class QueryProfile(SpectralPlugin):
    def parse_input(self, user_input: str) -> QueryParams:
        """
        Parse domain-specific query format.
        
        Hook: Runs BEFORE Chromatic Gravity calculation.
        
        Args:
            user_input: Raw query string from user
        
        Returns:
            QueryParams: Validated parameters for ChromaQuery
        """
    
    def post_process(self, results: list[dict]) -> list[dict]:
        """
        Transform results after core query.
        
        Hook: Runs AFTER Mnemosyne scoring, BEFORE returning to user.
        
        Args:
            results: Nodes returned from ChromaQuery
        
        Returns:
            Filtered/transformed results
        """
    
    def custom_scoring(self, entry: dict, query: dict) -> float:
        """
        Add domain-specific relevance score.
        
        Hook: Runs DURING ChromaQuery scoring.
        
        Args:
            entry: Node being scored
            query: Query parameters
        
        Returns:
            Additional score [0, 1] - blended with Mnemosyne
        """
```

**Execution Semantics:**

- **Exclusive** - only one Query Profile active per query (specified via `profile="name"`)
- Default profile ships with ChromaCore (simple natural language parsing)
- Applications register custom profiles for domain-specific query syntax

**Example Use Cases:**

- Structured query parsing (paradigm|subdomain|date format)
- Domain-specific filtering (release status, exact path matching)
- Result aggregation (layout traits, hashtag distributions)
- Custom ranking (boost by source authority, freshness)

---

### 4. Temporal Processors

**Purpose:** Automate lifecycle operations based on temporal patterns (scheduled background tasks).

**Lifecycle:** Runs on background schedule (cron expression).

**Hook Interface:**

```python
class TemporalProcessor(SpectralPlugin):
    def process_entries(self, entries: list[dict]) -> None:
        """
        Process entries on schedule.
        
        Hook: Runs on background schedule (uses Plugin API for modifications).
        
        Args:
            entries: Nodes fetched for processing (defined by plugin's query)
        """
    
    def schedule(self) -> str:
        """
        Define execution schedule.
        
        Returns:
            Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
        """
    
    def get_candidate_query(self) -> dict:
        """
        Define which nodes to process.
        
        Returns:
            Query parameters for ChromaCore to fetch candidates
        """
```

**Execution Semantics:**

- **Parallel** - multiple temporal processors run independently
- **Non-blocking** - runs in background, doesn't block user operations
- Uses ChromaCore's internal batching for efficiency

**Example Use Cases:**

- Auto-archiving old entries
- Version lifecycle (promote beta → public after X days)
- Freshness checks (trigger re-scraping for stale data)
- Backup scheduling

---

## Plugin API

The **Plugin API** is the safe interface plugins use to interact with ChromaCore. It provides validated access to storage, queries, and semantic stack without direct database access.

### Core Operations

```python
class PluginAPI:
    """Safe API for plugin-ChromaCore interaction."""
    
    # Storage
    def store_node(self, hashtags: list[str], content: str, **plugin_fields) -> str:
        """Store node with plugin-specific fields."""
    
    def update_metadata(self, entry_id: str, metadata: dict) -> bool:
        """Update node metadata (plugin-namespaced)."""
    
    def delete_node(self, entry_id: str) -> bool:
        """Delete node."""
    
    # Queries
    def query(self, hashtags: list[str], k: int = 5, **filters) -> list[dict]:
        """Query nodes via ChromaQuery."""
    
    def get_node(self, entry_id: str) -> dict:
        """Fetch single node by ID."""
    
    # Semantic Stack
    def resolve_hashtag(self, hashtag: str) -> dict:
        """Get anchor data for hashtag."""
    
    def list_hashtags(self, zone: str = None) -> list[str]:
        """List assigned hashtags (optionally filter by zone)."""
    
    # Plugin Schema Fields
    def read_field(self, entry_id: str, field_name: str) -> Any:
        """Read plugin-added column value."""
    
    def write_field(self, entry_id: str, field_name: str, value: Any) -> bool:
        """Write plugin-added column value."""
```

### Validation & Safety

All API operations:

1. **Validate inputs** - reject invalid parameters
2. **Enforce immutability** - prevent coordinate modification
3. **Namespace metadata** - plugin metadata prefixed with plugin name
4. **Handle errors** - return error codes, don't crash

**Example validation:**

```python
# Plugin tries to modify core field
api.update_metadata(entry_id, {'color_L': 50})
# Raises: PluginError("Cannot modify core field 'color_L'")

# Plugin provides invalid hashtags
api.store_node(hashtags=['#only_one_tag'], content='...')
# Raises: ValidationError("Insufficient hashtags (need 8+ with zone distribution)")
```

---

# Plugin Protocol Specifications

### Base Class

```python
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

class SpectralPlugin(ABC):
    """Base class for all ChromaCore plugins."""
    
    # Metadata
    NAME: str = "plugin_name"
    VERSION: str = "1.0.0"
    REQUIRES: list[str] = []  # ["OtherPlugin >= 1.0.0"]
    
    def __init__(self, api: PluginAPI, config: dict):
        """
        Initialize plugin.
        
        Args:
            api: Safe ChromaCore API interface
            config: Plugin-specific configuration
        """
        self.api = api
        self.config = config
```

### Schema Extension Protocol

```python
@runtime_checkable
class SchemaExtension(Protocol):
    def extend_schema(self) -> dict[str, Any]:
        """
        Define additional columns and indexes.
        
        Returns:
            {
                'columns': {
                    'column_name': 'SQL_TYPE',
                    ...
                },
                'indexes': [
                    'CREATE INDEX idx_name ON nodes(column_name)',
                    ...
                ]
            }
        """
        ...
```

### Storage Hook Protocol

```python
@runtime_checkable
class StorageHook(Protocol):
    def pre_storage_filter(self, entry: dict[str, Any]) -> dict[str, Any]:
        """
        Modify or validate node data before database insert.
        """
        ...

    def post_storage(self, entry: dict[str, Any]) -> None:
        """
        Side effects after storage.
        """
        ...
```

### Query Profile Protocol

```python
@runtime_checkable
class QueryProfile(Protocol):
    def parse_input(self, user_input: str) -> QueryParams:
        """Translate raw input to internal query parameters."""
        ...

    def post_process(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Refine or reformat query results."""
        ...
```

### Plugin Discovery

ChromaCore discovers plugins via:

1. **Explicit registration:**
```python
core.register_plugin(MyPlugin(config={...}))
```

2. **Directory scanning** (if enabled in config):
Scans the directory specified in `plugins.directory` for `.py` files. It attempts to load classes that implement the `SpectralPlugin` protocol.

---

## Plugin Registration & Lifecycle

### Registration

```python
# ChromaCore initialization
chromacore = ChromaCore(db_path="app.db")

# Register plugins
chromacore.register_plugin(MySchemaPlugin())
chromacore.register_plugin(MyStorageHook())
chromacore.register_plugin(MyQueryProfile())

# ChromaCore validates and activates plugins
chromacore.start()
```

### Startup Sequence

```
1. Plugin Registration Phase (developer code)
   → Plugins register themselves
   → ChromaCore collects all registered plugins
   
2. Dependency Validation Phase
   → For each plugin, check declared dependencies
   → Verify required plugins present
   → Verify version compatibility
   → If validation fails: ABORT startup, log error
   
3. Schema Extension Phase
   → Schema plugins execute extend_schema()
   → ChromaCore applies ALTER TABLE statements
   → Indexes created
   → Schema frozen
   
4. Activation Phase
   → Plugins activated
   → Hook handlers registered
   → Temporal processors scheduled
   
5. System Ready
   → ChromaCore operational
   → Plugins active
```

### Dependency Declaration

Plugins declare dependencies on other plugins:

```python
class MyQueryProfile(QueryProfile):
    REQUIRES = [
        "MySchemaPlugin >= 1.0.0"  # Name and minimum version
    ]
```

ChromaCore validates at startup:

- Plugin "MySchemaPlugin" is registered
- Version is >= 1.0.0
- If not: `StartupError("MyQueryProfile requires MySchemaPlugin >= 1.0.0")`

### Error Handling

**During startup:**

- Validation errors abort startup
- Missing dependencies abort startup
- Schema conflicts abort startup

**During operation:**

- Plugin hook failures are caught and logged
- Core continues operating
- Partial results returned (skip failed plugin's contribution)

**Example:**

```
[ERROR] StorageHook "PIIRedactionPlugin" failed in pre_storage_filter:
  AttributeError: 'NoneType' object has no attribute 'strip'
  
  Traceback:
    File "pii_plugin.py", line 42, in pre_storage_filter
      content = entry['content'].strip()
  
  Entry skipped. Core system continues.
```

### Retry Logic

ChromaCore automatically retries transient failures:

```
Plugin hook fails
  → Retry 1 (immediate)
  → Retry 2 (100ms delay)
  → Retry 3 (500ms delay)
  → If still failing: Log error, skip plugin, continue
```

Applies to: Storage hooks, query hooks (not schema extensions - those run once).

---

## Hook Execution Order

### Storage Pipeline

```
User: store_node(hashtags, content)
  ↓
1. Chromatic Gravity: compute coordinates
  ↓
2. Hook: pre_storage_filter (SEQUENTIAL - registration order)
   PluginA modifies entry
   PluginB receives PluginA's output
   PluginC receives PluginB's output
  ↓
3. ChromaCore validates (coordinates unchanged, fields valid)
  ↓
4. Database: INSERT INTO nodes
  ↓
5. Hook: post_storage (PARALLEL - order irrelevant)
   PluginA triggers webhook
   PluginB updates external index
   PluginC sends notification
  ↓
6. Return entry_id to user
```

### Query Pipeline

```
User: query(input, profile="custom")
  ↓
1. Hook: parse_input (EXCLUSIVE - only selected profile)
   CustomProfile parses input → QueryParams
  ↓
2. Chromatic Gravity: compute query coordinate
  ↓
3. Spatial Search: k-NN
  ↓
4. Mnemosyne Scoring: recency, relevance, strength
  ↓
5. Hook: custom_scoring (PARALLEL - all plugins)
   PluginA returns authority score: 0.8
   PluginB returns freshness score: 0.6
   Scores blended: 0.7 * mnemosyne + 0.3 * plugin_avg
  ↓
6. Sort by score, limit to k
  ↓
7. Update access states
  ↓
8. Hook: post_process (EXCLUSIVE - only selected profile)
   CustomProfile filters/transforms results
  ↓
9. Return results to user
```

### Background Processing

```
Cron triggers at scheduled time
  ↓
1. Temporal Processor: get_candidate_query()
   Returns: {hashtags: [...], temporal_range: (start, end)}
  ↓
2. ChromaCore fetches candidates via query
  ↓
3. Hook: process_entries(candidates)
   Plugin processes entries using Plugin API
  ↓
4. ChromaCore commits changes (uses internal batching)
```

---

## Configuration

Plugins accept configuration at registration:

```python
class MyPlugin(StorageHook):
    def __init__(self, config: dict):
        self.threshold = config.get('threshold', 0.8)
        self.enable_feature = config.get('enable_feature', True)

# Register with config
chromacore.register_plugin(MyPlugin({
    'threshold': 0.9,
    'enable_feature': True
}))
```

**Schema plugin config is frozen in backpack manifest:**

When exporting a backpack, ChromaCore saves:

```json
{
  "chromacore_version": "1.0.0",
  "plugins": [
    {
      "name": "MySchemaPlugin",
      "version": "2.0.0",
      "config": {
        "threshold": 0.9
      },
      "schema": {
        "columns": ["custom_field", "another_field"],
        "indexes": ["idx_custom"]
      }
    }
  ]
}
```

When importing, ChromaCore validates:

- Plugin name/version compatible
- Schema columns present
- Config compatible (or adaptable)

---

## Security

### Threat Model

**Assumptions:**

- Plugins are written by application developers (trusted)
- Main risks: bugs, not malicious code
- ChromaCore runs in controlled environments (servers, developer machines)

**Protections:**

- Coordinate immutability enforced (prevents backpack corruption)
- Plugin API validates all operations
- Plugin failures isolated (don't crash core)
- No direct database access (prevents accidental corruption)

### Plugin API Boundaries

**Plugins CAN:**

- Store/query nodes via API
- Modify plugin-added columns
- Read/write plugin-namespaced metadata
- Access semantic stack (read-only)

**Plugins CANNOT:**

- Modify coordinates (validated)
- Modify core ChromaCore columns (rejected)
- Access ChromaCore's internal state directly
- Execute arbitrary SQL (no raw database access)

### Advanced Plugin Escape Hatch (Optional)

For rare cases requiring raw database access:

```python
class AdvancedPlugin(StorageHook):
    REQUIRES_RAW_SQL = True  # Explicit declaration
    
    def __init__(self, api: PluginAPI):
        self.db = api.unsafe_database_access()  # Granted only if declared
```

ChromaCore warns on startup:

```
⚠️  WARNING: AdvancedPlugin requests raw database access
   This plugin can potentially corrupt data.
   Only install from trusted sources.
```

**Default:** 99% of plugins use safe Plugin API.

---

## Performance

### Overhead

**Schema Extensions:**

- One-time cost at startup (ALTER TABLE)
- Storage: ~50-300 bytes per node per column
- Query: Minimal (indexes optimize filtering)

**Storage Hooks:**

- Per-node latency: ~1-10ms (depends on hook complexity)
- Sequential pipeline: latencies add up
- Recommendation: Keep hooks lightweight

**Query Hooks:**

- parse_input: ~1-5ms
- custom_scoring: ~0.1ms per node
- post_process: ~1-10ms

**Temporal Processors:**

- Background only (no impact on interactive operations)
- Uses ChromaCore's internal batching (efficient for large datasets)

### Optimization

**ChromaCore provides:**

- Internal batching for bulk operations
- Retry logic for transient failures
- Parallel execution where possible (post_storage, custom_scoring)

**Plugin developers should:**

- Keep hooks lightweight
- Use Plugin API (optimized paths)
- Avoid expensive operations in hot paths (pre_storage_filter)
- Offload heavy work to temporal processors (background)

---

## Testing

### Unit Tests

Test plugin hooks in isolation:

```python
def test_plugin_hook():
    plugin = MyPlugin(config={})
    
    entry = {'content': 'test', 'hashtags': [...]}
    result = plugin.pre_storage_filter(entry)
    
    assert result['metadata']['processed'] == True
```

### Integration Tests

Test plugin with ChromaCore:

```python
def test_plugin_integration():
    chromacore = ChromaCore(':memory:')
    chromacore.register_plugin(MyPlugin())
    chromacore.start()
    
    entry_id = chromacore.store_node(hashtags=[...], content='test')
    result = chromacore.get_node(entry_id)
    
    assert result['metadata']['processed'] == True
```

### Backpack Compatibility

Test that plugin schemas are preserved:

```python
def test_backpack_export_import():
    db1 = ChromaCore('test1.db')
    db1.register_plugin(MySchemaPlugin())
    db1.start()
    db1.store_node(hashtags=[...], content='...')
    
    backpack = db1.export_backpack()
    
    db2 = ChromaCore('test2.db')
    db2.register_plugin(MySchemaPlugin())
    db2.import_backpack(backpack)
    
    # Verify plugin columns preserved
    assert db2.query([...])[0]['custom_field'] == expected_value
```

---

## Best Practices

### 1. Single Responsibility

One plugin = one focused responsibility.

**Good:** PIIRedactionPlugin, AutoArchivePlugin **Bad:** MegaPlugin (does everything)

### 2. Namespace Metadata

Avoid conflicts with other plugins:

```python
entry['metadata']['my_plugin:processed'] = True
entry['metadata']['my_plugin:version'] = '1.0.0'
```

### 3. Graceful Degradation

Check for dependencies at runtime (in addition to startup declaration):

```python
def pre_storage_filter(self, entry: dict) -> dict:
    if 'custom_field' not in entry:
        # Missing field from dependency - skip processing
        return entry
    
    # Process normally
    entry['metadata']['processed'] = True
    return entry
```

### 4. Version Plugin Schemas

```python
class MySchemaPlugin(SchemaExtension):
    VERSION = "2.0.0"
```

Include version in plugin class for backpack compatibility tracking.

### 5. Document Schema Extensions

```python
class MySchemaPlugin(SchemaExtension):
    """
    Adds application-specific columns.
    
    Columns:
        custom_field (TEXT): Description
        another_field (INTEGER): Description
    
    Indexes:
        idx_custom: Optimizes queries on custom_field
    """
```

---

## Implementation Checklist

- [ ] Create `SpectralPlugin` base class
- [ ] Create hook interface classes (SchemaExtension, StorageHook, QueryProfile, TemporalProcessor)
- [ ] Implement `PluginAPI` with safe access methods
- [ ] Implement plugin registration system
- [ ] Implement startup validation (dependencies, versions)
- [ ] Implement hook execution engine (sequential/parallel/exclusive semantics)
- [ ] Implement coordinate immutability validation
- [ ] Implement schema extension system (ALTER TABLE)
- [ ] Implement plugin configuration system
- [ ] Implement retry logic for transient failures
- [ ] Implement error isolation (plugin crash doesn't crash core)
- [ ] Implement backpack manifest plugin metadata
- [ ] Implement migration support for plugin schema upgrades
- [ ] Create plugin developer documentation
- [ ] Write unit tests for plugin system
- [ ] Write integration tests for each hook type
- [ ] Write backpack compatibility tests
- [ ] Create plugin template/boilerplate

---

**End of Specification**