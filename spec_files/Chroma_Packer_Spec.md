# Chroma Packer Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Architecture Overview](./Chroma_Core_Architecture_Overview.md)
- [Chroma Nodes](./Chroma_Nodes_Specification.md) - Payload contents
- [Spectral Plugins](./Spectral_Plugins_Spec.md) - Plugin bundling rules

---

## Overview

Chroma Packer is the subsystem responsible for:
* Exporting an **installed backpack folder** into a single portable `.bpack` package suitable for distribution.
* Importing a `.bpack` package into the MCP server’s `backpacks/` directory (new install or replacement).
* Maintaining a **local incremental backup chain** per backpack using **baseline + N diffs**, with automatic merge/rotation.
The packer operates on **unpacked backpack folders** stored inside the MCP server filesystem.

---

## Backpack Scope and Portability

### App-Scoped Artifacts

.bpack files are **application-scoped packages**, not universal interchange formats. They are designed to:

- Share data within a single application's ecosystem
- Allow users of the same app to exchange knowledge
- Support version upgrades within that app's lifecycle

### NOT Designed For

.bpack files are **not** designed to work across different applications that happen to use ChromaCore. A backpack created in "Patch#Craft" will not work in "Memex" even though both use ChromaCore internally.

### Why This Design?

Applications extend ChromaCore with app-specific:
- Schema columns (via plugins)
- Metadata fields
- Query profiles
- Business logic assumptions

A .bpack from one app contains these app-specific extensions. Attempting to import into a different app would cause schema mismatches and broken assumptions.

### Compatibility Gating

The `app_compat` section in `bpack.manifest.json` enforces this:
- `app_id` must match exactly
- `app_version` must be within specified range
- Import fails immediately if apps don't match

---

## Responsibilities

1. **Portable Export:** Snapshot a backpack folder into a `.bpack` artifact.
2. **Portable Import:** Validate and unpack `.bpack` into `backpacks/` under explicit collision rules.
3. **App-Layer Compatibility Gate:** Ensure `.bpack` is installed only into the **same App Layer** that created it.
4. **Integrity Verification:** Hash inventory + verification on import/restore.
5. **Local Incremental Backup:** Create and manage baseline + rolling diffs for restore points.
6. **Restore:** Reconstruct a backpack state and atomically replace the active folder.

---

## Backpack Folder Model

A backpack is an unpacked directory:

```text
CHROMACORE_ROOT/
  backpacks/
    <backpack_id>/
      nodes.db
      semantic_stack.json
      config.toml
      metadata.json
      plugins/
        ...
      ...
```

The packer treats **all files** under `<backpack_id>/` as part of the backpack state, including plugins and any auxiliary files created by the App Layer.

---

## Portable Package Format (.bpack)

### Container Encoding

`.bpack` is a **tar archive compressed with Zstandard**:
* Extension: `*.bpack`
* Encoding: `tar.zst`
The packer MUST be able to read and write this encoding.

### Internal Layout (Contract)

A `.bpack` archive MUST contain:

```text
/bpack.manifest.json        (required)
/payload/                   (required)
/payload/**                 (required)  # full backpack folder snapshot
```

No filtering is permitted. The `/payload/**` subtree MUST be a byte-accurate snapshot of the source backpack directory contents at export time.

### Manifest

`bpack.manifest.json` defines identity, compatibility gating, and payload inventory.

Required structure:

```json
{
  "bpack_version": "1.0.0",
  "created_at_utc": "2025-12-21T09:13:00Z",

  "backpack": {
    "id": "dev-patch_bpack",
    "display_name": "Dev Patch",
    "description": "Developer knowledge patch",
    "source_instance_id": null
  },

  "app_compat": {
    "app_id": "com.thotemic.devpatcher",
    "app_name": "Dev Knowledge Patch App",
    "app_version": "2.3.1",
    "min_app_version": "2.3.0",
    "max_app_version": null,
    "compat_mode": "STRICT"
  },

  "chromacore_compat": {
    "chromacore_version": "1.0.0",
    "min_chromacore_version": "1.0.0"
  },

  "payload": {
    "root": "payload/",
    "hash_algo": "blake3",
    "file_count": 183,
    "total_bytes": 104857600,
    "files": {
      "payload/nodes.db": {
        "bytes": 52428800,
        "hash": "…"
      },
      "payload/config.toml": {
        "bytes": 2048,
        "hash": "…"
      }
    }
  }
}
```

### Plugin Inclusion in .bpack Files

The `/payload/` directory in a .bpack archive MUST include:
```
/payload/
  nodes.db
  semantic_stack.json
  config.toml
  plugins/
    my_schema_plugin.py
    my_query_profile.py
    __init__.py
```

**All plugins used by the backpack are bundled.** This ensures that when Developer B imports a .bpack from Developer A (both using the same app), the plugins are available and the backpack is fully functional.

**Plugin Resolution on Import:**

1. Extract plugins from .bpack to `backpacks/<id>/plugins/`
2. Load plugins from that directory
3. Verify plugin versions match manifest declarations
4. If plugin version mismatch: warn or fail based on compatibility mode

### App-Layer Compatibility Enforcement

Import MUST evaluate the manifest before unpacking payload.
Rules (STRICT mode):
* Import MUST fail if `target_app_id != manifest.app_compat.app_id`.
* Import MUST fail if `target_app_version < manifest.app_compat.min_app_version`.
* Import MUST fail if `manifest.app_compat.max_app_version != null` and `target_app_version > max_app_version`.
**Source of `target_app_id` and `target_app_version`:** provided by the App Layer invoking import (CLI / UI / API wrapper). ChromaCore does not infer it.

### Integrity

`payload.files[*].hash` is authoritative. Import MUST verify hashes after extraction.
Hashing requirements:
* `hash_algo` MUST be `blake3` for v1.0.
* Hash input MUST be the raw file bytes exactly as stored on disk.

---

## Export (.bpack)

### Export Input/Output

Input:
* `CHROMACORE_ROOT/backpacks/<backpack_id>/`

Output:
* `<backpack_id>.bpack`

### Export Procedure

1. Enumerate all files under `<backpack_id>/` recursively.
2. Create canonical archive paths as `payload/<relative_path>`.
3. Compute `bytes` and `blake3` hash per file; populate manifest inventory.
4. Write `bpack.manifest.json`.
5. Create `tar` containing:
   * `bpack.manifest.json`
   * full `payload/**`
6. Compress with Zstandard.
7. Output filename MUST end with `.bpack`.

### Canonicalization Rules

* Path separators inside the archive MUST be `/`.
* Relative paths MUST NOT contain `..`.
* Archive entries MUST be ordered lexicographically by canonical path to stabilize output.
* File timestamps MAY be normalized (recommended) to improve deterministic builds; integrity is based on file bytes, not metadata.

---

## Import (.bpack)

### Import Targets

Target root:
* `CHROMACORE_ROOT/backpacks/`

A `.bpack` is imported into:
* `CHROMACORE_ROOT/backpacks/<target_backpack_id>/`

### Collision Policies

Import MUST implement the following collision modes:
* `AUTO_SUFFIX` (default): `<id>`, `<id>_2`, `<id>_3`, …
* `OVERWRITE`: delete existing target folder, then extract
* `FAIL`: error on collision

### Import Procedure

1. Open `.bpack` and read `bpack.manifest.json` only.
2. Enforce `app_compat` (STRICT) and `chromacore_compat`.
3. Resolve `<target_backpack_id>` using collision policy.
4. Extract `payload/**` into a staging directory:
   * `CHROMACORE_ROOT/backpacks/.staging/<target_backpack_id>/`
5. Verify all hashes from manifest inventory against extracted bytes.
6. Atomically install:
   * If target exists and policy is `OVERWRITE`: replace via rename swap.
   * If target does not exist: move staging into place.
7. Trigger backpack index refresh (implementation-defined hook).

### Extraction Safety

Import MUST prevent path traversal and unsafe writes:
* Reject any archive entry with:
  * absolute paths
  * `..` segments
  * paths not rooted under `payload/`
* Reject symlinks by default (v1.0). Only regular files and directories are supported.

---

## Local Incremental Backup/Restore

### Purpose

Maintain a local restore history per backpack using:
* 1 baseline snapshot
* N diff snapshots (rolling window)
* When creating diff N+1: merge oldest diff into baseline, rotate window, append new diff
Backups are local-only and do not use `.bpack`.

---

## Backup Storage Layout

```
CHROMACORE_ROOT/
  backups/
    <backpack_id>/
      baseline/
        snapshot.tar.zst
        baseline.meta.json
      diffs/
        diff_001/
          files.diff.tar.zst
          diff.meta.json
        diff_002/
          ...
```

### Baseline Snapshot

`baseline/snapshot.tar.zst` is a tar.zst of the entire backpack folder, stored under `payload/**` inside the snapshot archive.

`baseline.meta.json`:

```json
{
  "created_at_utc": "2025-12-21T09:13:00Z",
  "hash_algo": "blake3",
  "file_count": 183,
  "total_bytes": 104857600,
  "baseline_version": 1
}
```

---

## Diff Snapshot

Each `diff_k` represents changes from the prior restore point (baseline or diff_{k-1}).

### Diff Archive

`files.diff.tar.zst` contains only **added and modified** files, stored under `payload/**` paths.

### Diff Metadata

`diff.meta.json`:

```json
{
  "diff_index": 1,
  "created_at_utc": "2025-12-22T09:13:00Z",

  "added": ["payload/new_file.json"],
  "modified": ["payload/config.toml", "payload/nodes.db"],
  "deleted": ["payload/old_notes.txt"],

  "hash_algo": "blake3",
  "hashes": {
    "payload/new_file.json": "…",
    "payload/config.toml": "…",
    "payload/nodes.db": "…"
  }
}
```

### File Change Detection

Change detection is based on a file manifest computed at backup time:
* Relative path
* byte length
* blake3 hash
A file is `modified` if hashes differ.

---

## nodes.db Handling

In v1.0 local backups, `nodes.db` is treated as a file in the diff system:
* If `nodes.db` hash changes, it is included in `modified` and stored as a full replacement blob in `files.diff.tar.zst`.
This yields deterministic restores and keeps the diff machinery uniform across file types.

---

## Backup Creation

### Create Baseline (first backup)

1. Snapshot entire backpack folder into `baseline/snapshot.tar.zst`.
2. Write `baseline.meta.json`.
3. Ensure `diffs/` is empty.

### Create Diff (scheduled/manual)

1. Compute current manifest of backpack folder.
2. Compute manifest of last restore point:
   * if no diffs exist: baseline materialized manifest
   * else: last diff materialized manifest
3. Determine `added/modified/deleted` via hash comparisons.
4. Write `files.diff.tar.zst` containing added+modified file bytes.
5. Write `diff.meta.json` including hashes and tombstones.
Empty diffs are valid (all lists empty); they still create a restore point.

---

## Retention, Merge, Rotation

Let `retention_count = N` (default 3).
If creating a new diff would exceed N:

### Merge Oldest Diff Into Baseline

1. Materialize baseline snapshot to a temp directory.
2. Apply `diff_001`:
   * overlay added+modified files from `files.diff.tar.zst`
   * delete tombstoned paths
3. Rebuild baseline snapshot from the updated temp directory.
4. Increment `baseline_version` and update baseline meta.

### Rotate Diffs

* Delete `diff_001`
* Rename `diff_002 → diff_001`, `diff_003 → diff_002`, …
* Write the new diff as `diff_N`

---

## Restore

Restore targets a restore point `k`:
* `k = 0` means baseline
* `k = 1..N` means baseline + diffs up to `diff_k`

Procedure:
1. Extract baseline snapshot into a temp working directory.
2. For i in `1..k`:
   * extract `diff_i/files.diff.tar.zst` overlaying files
   * delete each tombstoned file in `diff_i/diff.meta.json`
1. Verify hashes:
   * baseline may be verified at creation time
   * diffs MUST be verified during restore before final install
1. Atomically replace active backpack folder with the restored directory.
Atomic install uses staging + rename swap to avoid partial state.

---

## Configuration Management

Chroma Packer reads configuration from the ChromaCore global config (specified elsewhere). Required keys for this subsystem:

* `packer.export.compression_level` (zstd level)
* `packer.import.collision_policy` (AUTO_SUFFIX/OVERWRITE/FAIL default)
* `backup.enabled`
* `backup.retention_count`
* `backup.schedule` (cron or interval; App Layer-defined scheduling mechanism)
* `backup.root_dir` (default `CHROMACORE_ROOT/backups/`)

---

## Statistics & Monitoring

The packer SHOULD expose counters:
* Export count, import count
* Import failures by reason (compat mismatch, hash mismatch, collision)
* Backup baseline count, diff count
* Restore count, restore failures
* Total bytes stored per backpack (baseline + diffs)

---

## Performance Considerations

* Hashing cost scales with total file bytes; blake3 is expected to be fast enough for frequent diffs.
* Large `nodes.db` files will dominate diff size if frequently modified; this is expected in v1.0 due to full-file replacement semantics.
* Staging directories and atomic rename swaps reduce corruption risk at the cost of temporary disk usage.

---

## Implementation Checklist

* `.bpack` read/write (tar + zstd)
* Canonical path generation + lexicographic entry ordering
* blake3 hashing + inventory in `bpack.manifest.json`
* STRICT App Layer gating enforced before extraction
* Safe extraction (no traversal, no symlinks)
* Collision policies implemented
* Local baseline snapshot + diff snapshot creation
* Merge oldest diff into baseline + rotation
* Restore pipeline + atomic folder swap
* Minimal stats surface (counters + last-error reason)

---

## Appendix: Reference Pseudocode

```python
def hash_file(path) -> str:
    # blake3 over bytes
    ...

def build_inventory(root_dir) -> dict[str, dict]:
    # returns {"payload/relpath": {"bytes": n, "hash": h}}
    ...

def export_bpack(backpack_dir, out_path, app_meta, chromacore_meta):
    inv = build_inventory(backpack_dir)
    manifest = make_manifest(inv, app_meta, chromacore_meta)
    write_tar_zst(out_path, manifest, backpack_dir, payload_root="payload/")

def import_bpack(bpack_path, target_root, target_app_meta):
    manifest = read_manifest_only(bpack_path)
    enforce_app_compat(manifest, target_app_meta)
    staging = extract_payload_to_staging(bpack_path, target_root)
    verify_hashes(manifest, staging)
    install_atomically(staging, target_root)
```


