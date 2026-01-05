# ChromaConfig Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [Mnemosyne Engine](./Mnemosyne_Engine_Spec.md) - Global memory toggles
- [SDK API Specification](./Chroma_Core_SDK_API.md) - Initialization

---

## Overview

ChromaConfig provides the **user-facing settings** for the ChromaCore environment. It is restricted to **operational concerns** (where files live, how much RAM to use, logging levels) and **high-level feature toggles**.

**Strict Prohibition:**
The Configuration system **DOES NOT** expose:

* **Chromatic Gravity constants** (epsilon, tag ratios, mass gradients).
* **Mnemosyne math** (decay curves, normalization constants).
* **Structural logic** (node schemas, zone definitions).

These core behaviors are immutable to guarantee that a backpack created on one machine behaves exactly the same on another.

---

## Configuration Hierarchy

1. **Framework Hardcoded Defaults** (The immutable baseline)
2. **`chroma.toml`** (User settings)
3. **Environment Variables** (Runtime overrides)

---

## The Configuration File (`chroma.toml`)

### Section 1: System

Controls the application wrapper, not the logic.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `system.environment` | string | "production" | "development" enables verbose logging. |
| `system.log_level` | string | "INFO" | Levels: DEBUG, INFO, WARN, ERROR. |

### Section 2: Storage (Database)

Tuning for the SQLite engine performance. ChromaCore v1.0 is Python-only and uses SQLite exclusively (libSQL for Python is a supported future upgrade path).

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `storage.db_path` | string | "chromacore.db" | File path for the main database. |
| `storage.cache_size_mb` | int | 64 | RAM limit for the database page cache. |
| `storage.wal_mode` | bool | true | Write-Ahead Logging (performance/concurrency). |

### Section 3: Memory (Mnemosyne)

High-level toggles for the memory system.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `memory.enabled` | bool | true | Master switch. If false, all memory scoring is skipped. |
| `memory.default_mode` | string | "Adaptive" | The default lifecycle mode for new nodes. |
| `memory.decay_enabled` | bool | true | If false, background decay is paused globally. |

### Section 4: Query Defaults

Sets **default values** for optional API parameters. Does not change search logic.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `query.default_k` | int | 5 | Default results to return if `k` is unspecified. |
| `query.default_profile` | string | "default" | Default profile if none specified. |
| `query.include_rotten` | bool | false | Default visibility of rotten nodes. |

### Section 5: Backups (Packer)

Operational settings for local data safety.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `backup.enabled` | bool | true | Master switch for local snapshots. |
| `backup.path` | string | "backups/" | Directory for local snapshots. |
| `backup.schedule` | string | "daily" | Simple frequency keyword (daily, hourly, weekly). |
| `backup.retention_count` | int | 3 | How many rolling restore points to keep. |

### Section 6: Plugins

Safety gates for external code.

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `plugins.directory` | string | "plugins/" | Folder to scan for `.py` plugin files. |
| `plugins.load_on_startup` | bool | true | Master switch to enable/disable extension loading. |

---

## Environment Variable Overrides

Standardized overrides using `CHROMA_<SECTION>_<KEY>`.

* `CHROMA_SYSTEM_LOG_LEVEL`
* `CHROMA_STORAGE_DB_PATH`
* `CHROMA_MEMORY_ENABLED`

---

## Appendix: Default `chroma.toml`

The standard file generated on install. Note the absence of any physics/math parameters.

```toml
# ChromaCore Configuration v1.0
# Operational settings only. Core physics are immutable.

[system]
environment = "production"
log_level = "INFO"

[storage]
db_path = "chromacore.db"
cache_size_mb = 64
wal_mode = true

[memory]
enabled = true
default_mode = "Adaptive"     # Options: Sparse, Adaptive, Spacey, Eidetic
decay_enabled = true

[query]
default_k = 5
default_profile = "default"
include_rotten = false

[backup]
enabled = true
path = "backups/"
schedule = "daily"
retention_count = 3

[plugins]
directory = "plugins/"
load_on_startup = true

```

---

## Configuration Validation

ChromaCore validates configuration on load using a schema-based approach (e.g., Pydantic).

```python
from pydantic import BaseModel, Field, validator

class StorageConfig(BaseModel):
    db_path: str = Field(default="chromacore.db")
    cache_size_mb: int = Field(default=64, ge=8, le=1024)
    wal_mode: bool = Field(default=True)
    
    @validator('db_path')
    def validate_db_path(cls, v):
        if not v.endswith('.db'):
            raise ValueError("db_path must end with .db")
        return v

class MemoryConfig(BaseModel):
    enabled: bool = Field(default=True)
    default_mode: str = Field(default="Adaptive")
    decay_enabled: bool = Field(default=True)

    @validator('default_mode')
    def validate_mode(cls, v):
        valid = ["Sparse", "Adaptive", "Spacey", "Eidetic"]
        if v not in valid:
            raise ValueError(f"Invalid mode. Must be one of {valid}")
        return v
```

## Invalid Configuration Examples

### Invalid Mode
```toml
[memory]
default_mode = "SuperMode"  # ❌ Invalid - must be Sparse|Adaptive|Spacey|Eidetic
```
**Error:** `ConfigurationError: Invalid memory.default_mode: "SuperMode". Must be one of: ['Sparse', 'Adaptive', 'Spacey', 'Eidetic']`

### Invalid Cache Size
```toml
[storage]
cache_size_mb = 10000  # ❌ Too large (max 1024)
```
**Error:** `ConfigurationError: storage.cache_size_mb must be less than or equal to 1024`

---

**End of Specification**