# ChromaQuery Specification

**Version:** 1.0.0  
**Status:** Final Specification  
**Last Updated:** 2025-12-21

---

## Related Specifications

- [Chromatic Gravity](./Chromatic_Gravity_Spec.md) - Coordinate calculation
- [Mnemosyne Engine](./Mnemosyne_Engine_Spec.md) - Memory ranking
- [Chroma Nodes](./Chroma_Nodes_Specification.md) - Storage backend

---

## Overview

ChromaQuery is ChromaCore's **retrieval engine**. It translates semantic queries (expressed as hashtag combinations) into spatial coordinates via Chromatic Gravity, performs k-nearest neighbor searches in L\*a\*b\* color space, and ranks results using Mnemosyne memory signals.

ChromaCore v1.0 is **Python-only**. Future language ports are not in scope for this specification.

ChromaQuery operates in two modes:

1. **Direct API** - Developers call `query()` with explicit parameters
2. **Query Profiles** - Domain-specific query interfaces that parse user input and transform results

The core query algorithm is **immutable** - it's the geometric foundation of ChromaCore. Query Profiles provide **extensibility** without modifying the underlying physics.

---

## Core Responsibilities

1. **Coordinate Calculation:** Convert hashtag sets to (L, a, b) coordinates via Chromatic Gravity
2. **Spatial Search:** Find k-nearest neighbors in color space
3. **Memory Scoring:** Rank results by recency, relevance, and strength (Mnemosyne)
4. **Temporal Filtering:** Filter by creation/access timestamps
5. **Metadata Filtering:** Filter by arbitrary JSON fields
6. **Result Assembly:** Return ordered list of matching nodes

---

## Core Query API

### Function Signature

```python
def query(
    hashtags: list[str],
    k: int = 5,
    max_distance: float = None,
    temporal_range: tuple[int, int] = None,
    metadata_filters: dict = None,
    include_rotten: bool = False,
    score_weights: dict = None,
    profile: str = "default"
) -> list[dict]:
    """
    Semantic search via color space proximity.

    Args:
        hashtags: List of hashtag strings to compute query coordinate
        k: Number of results to return
        max_distance: Maximum Euclidean distance in L*a*b* space (None = unlimited)
        temporal_range: (start_timestamp, end_timestamp) for filtering
        metadata_filters: Dict of JSON field queries (e.g., {"paradigm": "ai_tools"})
        include_rotten: Include rotten nodes in results (default: False)
        score_weights: Override Mnemosyne weights (e.g., {"relevance": 0.6, "recency": 0.2, "strength": 0.2})
        profile: Query Profile to use (default: "default")

    Returns:
        List of node dicts ordered by score (highest first)
    """
```

### Parameters Explained

**hashtags** (required)

- Must pass Chromatic Gravity validation rules
- Minimum 1 Core hashtag, 1 Outer hashtag, 65% Mid hashtags (typically 8+ total)
- Example: `["#python", "#async", "#stdlib", "#typing", "#dataclass", "#enum", "#protocol", "#v3.13"]`

**k** (default: 5)

- Number of results to return
- Typical values: 5-50
- Higher k = broader semantic neighborhood

**max_distance** (default: None)

- Maximum Euclidean distance from query coordinate
- None = no distance limit (rely on k only)
- Typical values: 20-100 (depends on semantic spread)
- Distance formula: `sqrt((L1-L2)² + (a1-a2)² + (b1-b2)²)`

**temporal_range** (default: None)

- Tuple of (start, end) Unix timestamps
- Filters nodes by `created_at` or `last_accessed`
- None = no temporal filtering
- Example: `(1704067200, 1735689600)` = Jan 1, 2024 to Dec 31, 2024

**metadata_filters** (default: None)

- Dict of JSON field queries
- Supports exact match, range queries, substring matching
- Example: `{"paradigm": "ai_tools", "release_status": ["public", "lts"]}`
- Depends on schema plugins (e.g., ChromaBase adds these fields)

**include_rotten** (default: False)

- Whether to include nodes marked as rotten (Mnemosyne lifecycle)
- False = exclude rotten nodes (typical)
- True = include all nodes regardless of rot status

**score_weights** (default: None)

- Override Mnemosyne scoring weights
- None = use mode defaults (e.g., Adaptive: {relevance: 0.5, recency: 0.3, strength: 0.2})
- Must sum to 1.0
- Example: `{"relevance": 0.7, "recency": 0.2, "strength": 0.1}` (emphasize semantic match)

**profile** (default: "default")

- Which Query Profile to use
- "default" = built-in natural language profile
- Custom profiles registered via Spectral Plugin system
- Example: "knowledge_patch" (parses structured queries)

---

## Query Pipeline

### Phase 1: Input Processing

**If using Query Profile:**

```python
# Query Profile hook: parse_input()
query_params = profile.parse_input(user_input)
# Returns: QueryParams(hashtags, k, filters, etc.)
```

**If using Direct API:**

```python
# Developer provides explicit parameters
query_params = QueryParams(
    hashtags=["#python", "#async", ...],
    k=10,
    temporal_range=(start, end),
    metadata_filters={"paradigm": "programming_languages"}
)
```

### Phase 2: Hashtag Validation

**Validate via Chromatic Gravity rules:**

```python
validate_hashtags(query_params.hashtags)
# Checks:
# - Minimum 1 Core hashtag
# - Minimum 1 Outer hashtag
# - Minimum 65% Mid hashtags
# - Minimum 8 total hashtags (derived from above)

# If invalid:
raise ValidationError("Insufficient Mid hashtags (need 65%)")
```

### Phase 3: Coordinate Calculation

**Compute query coordinate via Chromatic Gravity:**

```python
query_color = compute_node_color(query_params.hashtags)
# Returns: (L, a, b) tuple
# Example: (52.3, 18.4, -22.1)
```

**This is the immutable core** - same algorithm used for storage.

### Phase 4: Spatial Search (k-NN)

**Fetch candidate nodes from color space:**

```python
# SQL-based spatial query
SELECT 
    entry_id, node_id,
    color_L, color_a, color_b,
    hashtags, label, content, metadata,
    created_at, last_accessed,
    strength_raw, decay_health, ascension, rotten,
    mode_name, access_count
FROM nodes
WHERE 
    -- Bounding box pre-filter (optimization)
    color_L BETWEEN (query_L - max_distance) AND (query_L + max_distance)
    AND color_a BETWEEN (query_a - max_distance) AND (query_a + max_distance)
    AND color_b BETWEEN (query_b - max_distance) AND (query_b + max_distance)

    -- Rotten filter
    AND (rotten = 0 OR include_rotten = TRUE)
```

**Calculate exact distances:**

```python
candidates = []
for row in results:
    distance = sqrt(
        (row.color_L - query_color.L) ** 2 +
        (row.color_a - query_color.a) ** 2 +
        (row.color_b - query_color.b) ** 2
    )

    if max_distance is None or distance <= max_distance:
        candidates.append({
            **row,
            'distance': distance
        })
```

**Typical candidate set size:** 100-500 nodes (before filtering/scoring)

### Phase 5: Temporal Filtering

**If temporal_range specified:**

```python
if temporal_range:
    start, end = temporal_range
    candidates = [
        c for c in candidates
        if start <= c['created_at'] <= end
        or start <= c['last_accessed'] <= end
    ]
```

**Typical reduction:** 50-200 nodes remain

### Phase 6: Metadata Filtering

**If metadata_filters specified:**

```python
if metadata_filters:
    for key, value in metadata_filters.items():
        candidates = [
            c for c in candidates
            if match_metadata(c['metadata'], key, value)
        ]
```

**Typical reduction:** 20-100 nodes remain

### Phase 7: Memory Scoring (Mnemosyne Integration)

**For each candidate, calculate memory signals:**

```python
now = int(time.time())
config = load_mode_config(candidate['mode_name'])

# Recency
delta_days = (now - candidate['last_accessed']) / 86400.0
recency = exp(-delta_days / config['tau_rec_days'])

# Relevance (from distance)
relevance = exp(-candidate['distance'] / sigma)

# Strength (normalized)
strength_norm = candidate['strength_raw'] / (candidate['strength_raw'] + kS)

# Combined score
score = (
    score_weights['relevance'] * relevance +
    score_weights['recency'] * recency +
    score_weights['strength'] * strength_norm
)

candidate['score'] = score
candidate['recency'] = recency
candidate['relevance'] = relevance
candidate['strength_norm'] = strength_norm
```

**Score range:** [0, 1]

### Phase 8: Ranking & Limiting

**Sort by score, take top k:**

```python
candidates.sort(key=lambda x: x['score'], reverse=True)
results = candidates[:k]
```

### Phase 9: Access State Update

**Update last_accessed for returned nodes:**

```python
for result in results:
    update_access_state(result['entry_id'], now)
    # Updates:
    # - last_accessed = now
    # - access_count += 1
    # - strength_raw += alpha_hit (if not permanent)
```

### Phase 10: Post-Processing (Query Profile Hook)

**If using Query Profile:**

```python
# Query Profile hook: post_process()
results = profile.post_process(results)
# Can filter, re-rank, aggregate, transform format, etc.
```

### Phase 11: Return Results

**Final output:**

```python
return results
# List of node dicts with all fields + score/relevance/recency/strength_norm
```

---

## Output Format

### Result Structure

Each result is a dict containing:

**Core Node Fields:**

```python
{
    'entry_id': 'uuid-string',
    'node_id': 'hash-of-coordinates',
    'color_L': 52.3,
    'color_a': 18.4,
    'color_b': -22.1,
    'hashtags': ['#python', '#async', ...],
    'label': 'Python 3.14 async changes',
    'content': '...',
    'metadata': {...},
    'created_at': 1702857600,
    'last_accessed': 1702944000,
}
```

**Memory System Fields:**

```python
{
    'strength_raw': 2.5,
    'decay_health': 0.87,
    'ascension': False,
    'rotten': False,
    'mode_name': 'Adaptive',
    'access_count': 12,
}
```

**Query-Computed Fields:**

```python
{
    'distance': 8.4,           # Euclidean distance from query coordinate
    'relevance': 0.68,         # Mnemosyne relevance signal
    'recency': 0.92,           # Mnemosyne recency signal
    'strength_norm': 0.33,     # Mnemosyne normalized strength
    'score': 0.73,             # Combined Mnemosyne score
}
```

**Plugin-Added Fields (if schema plugins installed):**

```python
{
    'paradigm': 'programming_languages',
    'subdomain_path': 'programming_languages:python:language',
    'release_status': 'public',
    'relevance_date': '2025-11-20',
    'source_url': 'https://docs.python.org/3.14/whatsnew/3.14.html',
    'layout_traits': {'header_body': 0.6, 'list_format': 0.4},
}
```

---

## Query Profiles

### Purpose

Query Profiles are **Spectral Plugins** that extend ChromaQuery's interface without modifying its core algorithm. They allow developers to:

1. Parse domain-specific input formats
2. Apply custom pre-filtering logic
3. Transform results after core query
4. Add domain-specific ranking signals

### Base Class Interface

```python
class QueryProfile:
    """
    Base class for custom Query Profiles.
    Implements Spectral Plugin hooks for query extension.
    """

    def parse_input(self, user_input: str) -> QueryParams:
        """
        Convert domain-specific input to ChromaQuery parameters.

        Hook: Runs BEFORE core query.

        Args:
            user_input: Raw user query (format depends on profile)

        Returns:
            QueryParams: Validated parameters for core query
        """
        raise NotImplementedError

    def post_process(self, results: list[dict]) -> list[dict]:
        """
        Filter, rank, or transform results after core query.

        Hook: Runs AFTER core query, BEFORE returning to user.

        Args:
            results: Results from core ChromaQuery

        Returns:
            list[dict]: Transformed results
        """
        return results  # Default: no transformation

    def custom_scoring(self, entry: dict, query: dict) -> float:
        """
        Optional: Add domain-specific relevance scoring.

        Hook: Runs DURING core query, blended with Mnemosyne score.

        Args:
            entry: Node being scored
            query: Query parameters

        Returns:
            float: Additional score component (0-1 range)
        """
        return 0.0  # Default: no additional scoring
```

### Default Profile (Built-in)

**Ships with ChromaCore:**

```python
class DefaultQueryProfile(QueryProfile):
    """
    Simple natural language query parser.
    No external dependencies, no schema assumptions.
    """

    def parse_input(self, user_input: str) -> QueryParams:
        """
        Parse queries like:
        - "recent Python async entries"
        - "find code snippets about dictionary comprehension"
        - "documents from last month about climate change"
        """
        # Extract hashtags from natural language
        hashtags = self._extract_hashtags(user_input)

        # Detect temporal keywords
        temporal_range = self._parse_temporal(user_input)

        # Detect result count hints
        k = self._parse_count(user_input) or 5

        return QueryParams(
            hashtags=hashtags,
            k=k,
            temporal_range=temporal_range
        )

    def _extract_hashtags(self, text: str) -> list[str]:
        """
        Extract semantic concepts from natural language.
        Uses simple keyword matching against semantic stack.
        """
        # Example: "Python async" → ["#python", "#async", "#programming"]
        # Implementation: match words against semantic stack tags
        pass

    def _parse_temporal(self, text: str) -> tuple[int, int]:
        """
        Parse temporal expressions.
        Examples: "recent", "last month", "from 2024"
        """
        # Example: "recent" → (now - 7_days, now)
        pass

    def _parse_count(self, text: str) -> int:
        """
        Parse result count hints.
        Examples: "top 10", "5 results"
        """
        # Example: "top 10" → k=10
        pass
```

### Profile Registration

```python
# Register custom profile
chromacore.register_query_profile("my_profile", MyCustomProfile())

# Use it
results = chromacore.query(
    "custom input format",
    profile="my_profile"
)

# Or set as default
chromacore.set_default_query_profile("my_profile")
```

---

## Configuration

### Global Query Defaults

**Set at ChromaCore initialization:**

```python
chromacore = ChromaCore(
    query_config={
        'default_k': 10,
        'default_max_distance': 50.0,
        'default_score_weights': {
            'relevance': 0.6,
            'recency': 0.2,
            'strength': 0.2
        },
        'default_profile': 'default',
        'include_rotten': False
    }
)
```

### Per-Query Overrides

**Every parameter can be overridden per query:**

```python
# Use global defaults
results = chromacore.query(["#python", "#async", ...])

# Override specific parameters
results = chromacore.query(
    ["#python", "#async", ...],
    k=20,  # Override default_k
    score_weights={'relevance': 0.8, 'recency': 0.1, 'strength': 0.1}  # Override weights
)
```

### Mnemosyne Integration

**Query inherits Mnemosyne mode from nodes:**

```python
# Each node has mode_name field (Sparse, Adaptive, Spacey, Eidetic)
# ChromaQuery loads that mode's parameters when scoring
config = load_mode_config(node['mode_name'])
recency = exp(-delta_days / config['tau_rec_days'])
```

**Override weights globally:**

```python
# Force all queries to use custom weights (ignore node modes)
results = chromacore.query(
    ["#python", ...],
    score_weights={'relevance': 0.7, 'recency': 0.2, 'strength': 0.1}
)
```

**Disable Mnemosyne entirely:**

```python
# Pure spatial search (no recency/strength scoring)
results = chromacore.query(
    ["#python", ...],
    score_weights={'relevance': 1.0, 'recency': 0.0, 'strength': 0.0}
)
```

---

## Performance Characteristics

### Time Complexity

| Operation                     | Complexity   | Notes                                         |
| ----------------------------- | ------------ | --------------------------------------------- |
| Coordinate calculation        | O(n × i)     | n = hashtag count, i = gravity iterations (3) |
| Spatial search (brute force)  | O(N)         | N = total nodes in database                   |
| Spatial search (R-tree index) | O(log N + k) | With spatial index                            |
| Distance calculation          | O(1)         | Per candidate                                 |
| Mnemosyne scoring             | O(1)         | Per candidate                                 |
| Sorting                       | O(m log m)   | m = candidate set size                        |

### Typical Latencies

**With 100K nodes, R-tree spatial index:**

| Operation              | Latency       |
| ---------------------- | ------------- |
| Coordinate calculation | 1-2 ms        |
| Spatial search (k=5)   | 10-20 ms      |
| Spatial search (k=50)  | 50-100 ms     |
| Mnemosyne scoring      | 5-10 ms       |
| Access state updates   | 10-20 ms      |
| **Total (k=5)**        | **30-50 ms**  |
| **Total (k=50)**       | **80-150 ms** |

**With 1M nodes:**

| Operation             | Latency        |
| --------------------- | -------------- |
| Spatial search (k=5)  | 50-100 ms      |
| Spatial search (k=50) | 200-400 ms     |
| **Total (k=5)**       | **80-150 ms**  |
| **Total (k=50)**      | **250-500 ms** |

### Optimization Strategies

**1. Spatial Indexing**

Use R-tree spatial index for L\*a\*b\* coordinates:

```sql
-- Create spatial index (implementation-dependent)
CREATE INDEX idx_color_rtree ON nodes 
USING rtree(color_L, color_a, color_b);
```

**2. Candidate Set Limiting**

Fetch larger candidate set initially, filter aggressively:

```python
# Fetch 3x more candidates than needed
candidates = spatial_search(query_color, k=requested_k * 3)

# Apply filters
candidates = temporal_filter(candidates)
candidates = metadata_filter(candidates)

# Score and take top k
results = score_and_rank(candidates)[:requested_k]
```

**3. Caching**

Cache Chromatic Gravity coordinates for common hashtag combinations:

```python
@lru_cache(maxsize=1000)
def compute_node_color(hashtags: tuple[str]) -> tuple[float, float, float]:
    # Expensive gravity calculation
    pass
```

**4. Batch Queries**

Process multiple queries in parallel:

```python
results = chromacore.batch_query([
    {"hashtags": ["#python", ...], "k": 5},
    {"hashtags": ["#python", ...], "k": 10},
    {"hashtags": ["#asyncio", ...], "k": 5}
])
# Returns list of result lists
```

**5. Incremental Access Updates**

Batch access state updates:

```python
# Queue updates instead of writing immediately
access_queue.append((entry_id, timestamp))

# Flush periodically (every 100 queries or 1 second)
if len(access_queue) >= 100 or time_since_flush > 1.0:
    batch_update_access_states(access_queue)
    access_queue.clear()
```

---

## Error Handling

### Validation Errors

**Invalid hashtag combinations:**

```python
try:
    results = chromacore.query(["#python"])  # Only 1 tag, needs 8+
except ValidationError as e:
    print(e)
    # "Insufficient tags: need minimum 8 (1 Core, 1 Outer, 65% Mid)"
```

**Resolution:** Use `suggest_hashtags()` to find relevant tags in content

```python
# Use the suggest_hashtags() SDK method to find more tags
suggestions = chromacore.suggest_hashtags(content)
# User confirms suggestions...
results = chromacore.query(
    ["#python"] + confirmed_suggestions
)
```

### Empty Results

**No nodes within max_distance:**

```python
results = chromacore.query(
    ["#obscure", "#niche", "#rare", ...],
    max_distance=10.0
)

if not results:
    print("No results found within distance threshold")
    # Retry with larger radius or broader hashtags
```

### Plugin Errors

**Query Profile parse failure:**

```python
try:
    results = chromacore.query(
        "malformed input",
        profile="strict_structured"
    )
except QueryProfileError as e:
    print(e)
    # "Failed to parse structured query: missing paradigm component"
```

**Resolution:** Fallback to default profile

```python
try:
    results = chromacore.query(input, profile="custom")
except QueryProfileError:
    results = chromacore.query(input, profile="default")
```

### Database Errors

**Connection failures, transaction conflicts:**

```python
try:
    results = chromacore.query([...])
except DatabaseError as e:
    # Retry with exponential backoff
    pass
```

---

## Advanced Example: Knowledge Patch Query Profile

### Overview

This Query Profile implements the structured query format from the Patch#Craft knowledge patching system. It parses queries like:

```
ai_tools | claude:tools:claude_code:updates | 2025-06-01 | latest | xml
```

Into ChromaCore query parameters, then applies domain-specific filtering.

**Requires:** ChromaBase schema plugin (adds paradigm, subdomain_path, release_status, relevance_date fields)

### Implementation

```python
class KnowledgePatchQueryProfile(QueryProfile):
    """
    Query Profile for Patch#Craft knowledge patching system.

    Query Format:
        Paradigm | Subdomains | Knowledge_Cutoff | UpTo_Release | Format

    Example:
        ai_tools | claude:tools:claude_code:updates | 2025-06-01 | latest | xml
    """

    def parse_input(self, user_input: str) -> QueryParams:
        """
        Parse structured or natural language query.
        """
        # Try structured format first
        parts = user_input.split('|')

        if len(parts) >= 3:
            return self._parse_structured(parts)
        else:
            return self._parse_natural(user_input)

    def _parse_structured(self, parts: list[str]) -> QueryParams:
        """
        Parse structured format:
        paradigm | subdomain | cutoff | release | format
        """
        paradigm = parts[0].strip()
        subdomain_path = parts[1].strip()
        knowledge_cutoff = parts[2].strip() if len(parts) > 2 else "1 year ago"
        upto_release = parts[3].strip() if len(parts) > 3 else "latest"

        # Resolve paradigm to hashtags
        hashtags = self._resolve_tags(paradigm, subdomain_path)

        # Parse temporal filter
        cutoff_timestamp = self._parse_date(knowledge_cutoff)

        # Build metadata filters
        metadata_filters = {
            'paradigm': paradigm,
            'subdomain_path': subdomain_path,
            'release_status': self._resolve_release(upto_release)
        }

        return QueryParams(
            hashtags=hashtags,
            k=100,  # Large candidate set for filtering
            temporal_range=(cutoff_timestamp, int(time.time())),
            metadata_filters=metadata_filters
        )

    def _resolve_tags(self, paradigm: str, subdomain_path: str) -> list[str]:
        """
        Convert paradigm + subdomain path to hashtag list.

        Example:
            paradigm: "ai_tools"
            subdomain_path: "ai_tools:claude:tools:claude_code:updates"

            Returns: ["#ai_tools", "#claude", "#tools", "#claude_code", "#updates"]
        """
        # Split subdomain path
        parts = subdomain_path.split(':')

        # Ensure paradigm is included
        if parts[0] != paradigm:
            parts.insert(0, paradigm)

        # Convert to hashtags
        hashtags = [f"#{part}" for part in parts]

        # Validate (need 8+ tags with 65% Mid)
        if len(hashtags) < 8:
            # Auto-pad with implicit tags
            hashtags.extend(self._get_implicit_tags(paradigm))

        return hashtags

    def _resolve_release(self, upto_release: str) -> list[str]:
        """
        Convert release specifier to status list.

        Examples:
            "latest" → ["public", "lts", "latest"]
            "beta" → ["beta", "public", "lts"]
            "v3.14" → version-specific filtering
        """
        if upto_release == "latest":
            return ["public", "lts", "latest"]
        elif upto_release == "beta":
            return ["beta", "public", "lts"]
        elif upto_release.startswith("v"):
            # Version-specific (requires additional logic)
            return ["public"]  # Simplified
        else:
            return ["public"]

    def post_process(self, results: list[dict]) -> list[dict]:
        """
        Apply domain-specific filtering after core query.
        """
        # Filter by exact subdomain match
        # (Core query gives semantic neighborhood, this narrows to exact path)
        filtered = [
            r for r in results
            if r.get('subdomain_path') == self.query_params['subdomain_path']
        ]

        # Aggregate layout traits for Document Fabricator
        layout_traits = self._aggregate_layout_traits(filtered)

        # Attach aggregated traits to results
        for r in filtered:
            r['_aggregated_layout_traits'] = layout_traits

        return filtered

    def _aggregate_layout_traits(self, results: list[dict]) -> dict:
        """
        Aggregate layout_traits across all results.
        Used by Genetic Templater to determine document structure.
        """
        trait_sums = {}

        for r in results:
            traits = r.get('layout_traits', {})
            for key, value in traits.items():
                trait_sums[key] = trait_sums.get(key, 0) + value

        # Normalize
        total = sum(trait_sums.values())
        if total > 0:
            return {k: v / total for k, v in trait_sums.items()}
        else:
            return {}
```

### Usage

```python
# Register profile
chromacore.register_query_profile("knowledge_patch", KnowledgePatchQueryProfile())

# Query with structured format
results = chromacore.query(
    "ai_tools | claude:tools:claude_code:updates | 2025-06-01 | latest | xml",
    profile="knowledge_patch"
)

# Results include:
# - Nodes matching semantic neighborhood (from Chromatic Gravity)
# - Filtered by paradigm/subdomain (exact match)
# - Filtered by knowledge_cutoff (after 2025-06-01)
# - Filtered by release_status (public, lts, latest)
# - Ranked by Mnemosyne score
# - Aggregated layout_traits attached
```

---

## Integration Points

**ChromaQuery integrates with:**

1. **Chromatic Gravity** - Coordinate calculation
2. **Semantic Stack** - Hashtag resolution
3. **Chroma Nodes** - Database queries
4. **Mnemosyne Engine** - Memory scoring
5. **Spectral Plugins** - Query Profile system

**ChromaQuery is called by:**

1. **MCP Server** - Via tool calls from AI models
2. **API Endpoints** - Via HTTP/REST
3. **CLI Tools** - Via command-line interface
4. **Application Layer** - Direct Python API

---

## Implementation Checklist

- [ ] Implement core `query()` function
- [ ] Integrate Chromatic Gravity for coordinate calculation
- [ ] Implement k-NN spatial search (brute force)
- [ ] Add R-tree spatial indexing (optimization)
- [ ] Integrate Mnemosyne scoring
- [ ] Implement temporal filtering
- [ ] Implement metadata filtering
- [ ] Implement access state updates
- [ ] Create QueryProfile base class
- [ ] Implement DefaultQueryProfile
- [ ] Add profile registration mechanism
- [ ] Add query parameter validation
- [ ] Add error handling (ValidationError, QueryProfileError, etc.)
- [ ] Implement batch query support
- [ ] Add query result caching
- [ ] Write unit tests for all query paths
- [ ] Write integration tests with Mnemosyne
- [ ] Benchmark performance (100K, 1M nodes)
- [ ] Document Query Profile creation guide
- [ ] Create example Query Profiles (knowledge patch, code search, etc.)

---

**End of Specification**