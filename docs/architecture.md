# Architecture Overview

ChromaCore is a Python 3.14 library for deterministic semantic memory. Meaning is explicit and stable (semantic hashtags), while memory is temporal (strengthen, decay, permanence, rot). It is designed to be embedded in applications rather than deployed as a standalone service.

## Core Principles

- Deterministic meaning -> coordinate mapping
- Semantic coordinates are immutable once created
- Memory lifecycle is directional (strengthen, decay, permanence, rot)
- Persistence is disk-first; memory is for active operations only
- Configuration is operational only; core physics and memory math are not configurable
- Plugins cannot mutate coordinates or bypass invariants

## Component Map

- Semantic Stack: fixed 10,000 anchors in L*a*b* space (hashtag -> anchor)
- Chromatic Gravity: deterministic coordinate computation from hashtags
- Chroma Nodes: SQLite persistence schema and invariants
- Mnemosyne Engine: memory scoring and lifecycle
- ChromaQuery: k-NN retrieval in color space + Mnemosyne ranking
- Spectral Plugins: schema hooks, storage hooks, query profiles, temporal processors
- Chroma Packer: .bpack export/import and local backups

## Data Flow

Store path:
1) Validate hashtags (zone rules)
2) Compute coordinates (Chromatic Gravity)
3) Run pre-storage plugin hooks
4) Persist node (SQLite)
5) Run post-storage hooks

Query path:
1) Parse input (query profile if provided)
2) Compute query coordinates
3) k-NN spatial search
4) Mnemosyne scoring and ranking
5) Run post-process profile hook
6) Update access state

## Storage Model (SQLite)

Nodes are stored disk-first in a single SQLite database with spatial and temporal indexes. Core fields include coordinates, hashtags, content, and temporal state. Memory fields track strength, decay health, ascension, and rot status.

## Extensibility

Plugins extend behavior through well-defined hooks. They interact via a safe Plugin API and cannot alter coordinates or core fields. Schema extensions are additive and permanent.

## Portability

Backpacks (.bpack) are app-scoped exports containing a manifest and full payload snapshot. Imports enforce app compatibility (app id + version gates).

## Source of Truth

Component specifications in `spec_files/` define the authoritative contracts and invariants. This document summarizes architecture only.
