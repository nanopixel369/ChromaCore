# ChromaCore

ChromaCore is a deterministic semantic memory engine where meaning is explicit and stable and memory is temporal. It is a Python 3.14 library (not a server) that maps hashtags to fixed L*a*b* coordinates, persists nodes in SQLite, and ranks results with an organic memory lifecycle.

## What It Is

- Deterministic storage of meaning via semantic hashtags (no embeddings)
- Disk-first persistence with SQLite-backed nodes
- Memory lifecycle modeling (strengthen, decay, permanence, rot)
- Extensible via safe, API-mediated plugins
- Portable, app-scoped data exchange via .bpack backpacks

## Core Components

- Semantic Stack: 10,000 fixed color anchors (hashtag -> coordinate)
- Chromatic Gravity: deterministic coordinate computation from hashtags
- Chroma Nodes: SQLite persistence schema + invariants
- Mnemosyne Engine: memory scoring, decay, ascension, rot
- ChromaQuery: k-NN retrieval in color space + Mnemosyne ranking
- Spectral Plugins: schema hooks, storage hooks, query profiles
- Chroma Packer: .bpack export/import and local incremental backups

## Key Invariants

- Identical hashtag sets always yield identical coordinates
- Semantic coordinates are immutable once created
- Memory lifecycle is directional (strengthen -> decay -> permanence/rot)
- Persistence is disk-first; memory is for active operations only
- Configuration is operational only (no core physics or math exposure)
- Plugins cannot mutate coordinates or bypass core constraints

## SDK Sketch

```python
from chromacore import ChromaCore

core = ChromaCore(db_path="chromacore.db", config_path=None, auto_init=True)

entry_id = core.store(
    hashtags=["#python", "#async", "#stdlib", "#typing", "#dataclass",
              "#enum", "#protocol", "#v3.13"],
    label="Python 3.13 async improvements",
    content="Details about new async features...",
    metadata={"source": "docs.python.org", "version": "3.13"}
)

results = core.query(
    hashtags=["#python", "#async", "#stdlib", "#typing", "#dataclass",
              "#enum", "#protocol", "#v3.13"],
    k=5
)
```

## Configuration

ChromaCore loads `chroma.toml` for operational settings (paths, logging, defaults). Core physics and memory math are intentionally not configurable to keep semantic meaning stable across machines.

## Backpacks

Backpacks are application-scoped exports of a knowledge graph. The `.bpack` format is a tar.zst bundle containing a manifest and a full payload snapshot. Imports enforce app compatibility.

## Specs (Source of Truth)

The component specifications in `spec_files/` define system contracts and invariants. Architecture summaries elsewhere are contextual only.

## Commands

- Build: `{{BUILD_CMD}}`
- Test: `{{TEST_CMD}}`
- Lint: `{{LINT_CMD}}`
- Typecheck: `{{TYPECHECK_CMD}}`
