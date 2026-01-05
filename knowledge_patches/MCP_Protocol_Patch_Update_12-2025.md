# MCP Protocol Updates: Knowledge Patch

**Status:** Post-Knowledge Cutoff Update (Nov 2024 → Dec 2025)  
**Topic:** Model Context Protocol Specification Changes  
**Relevance:** ChromaCore MCP server implementation must follow latest spec

---

## Specification Version Timeline

| Version        | Release Date | Key Focus                                               |
| -------------- | ------------ | ------------------------------------------------------- |
| **2024-11-05** | Nov 5, 2024  | Initial public release                                  |
| **2025-03-26** | Mar 26, 2025 | OAuth 2.1, Streamable HTTP, Tool Annotations            |
| **2025-06-18** | Jun 18, 2025 | OAuth Resource Servers, Elicitation, Security hardening |
| **2025-11-25** | Nov 25, 2025 | Tasks (async ops), Icons, Incremental auth, Enums       |

MCP follows **backwards-compatible versioning** - SDKs adopt at their own pace.

---

## Major Changes Since Nov 2024

### 1. Authorization Framework (OAuth 2.1)

**Added:** Comprehensive OAuth 2.1-based authorization (PR #133, Mar 2025)

**What Changed:**

- MCP servers now classified as **OAuth Resource Servers**
- Servers expose protected resource metadata for authorization server discovery
- Clients **must** implement **Resource Indicators (RFC 8707)** to prevent malicious servers from stealing access tokens
- Support for OpenID Connect Discovery 1.0 (Nov 2025)
- Incremental scope consent via `WWW-Authenticate` header (Nov 2025)

**Security Implications:**

- Prevents token leakage to untrusted servers
- Enables fine-grained permissions per MCP server
- Aligns with OAuth 2.1 best practices

**ChromaCore Impact:** If ChromaCore MCP server accesses protected resources (e.g., user's Google Drive), it must implement OAuth Resource Server spec.

---

### 2. Streamable HTTP Transport

**Replaced:** HTTP+SSE transport → **Streamable HTTP** (PR #206, Mar 2025)

**What Changed:**

- More flexible bidirectional communication
- Supports polling SSE streams (server can disconnect at will)
- GET streams support resumption regardless of origin
- Requires `MCP-Protocol-Version` header in subsequent requests

**Benefits:**

- Works in more network environments (firewalls, proxies)
- Better mobile/edge device support
- Polling fallback for unreliable connections

**ChromaCore Impact:** Use Streamable HTTP for remote deployments (browser-based clients, cloud hosting).

---

### 3. Tool Annotations

**Added:** Comprehensive tool metadata (PR #185, Mar 2025)

**New Fields:**

```typescript
{
  "name": "delete_file",
  "description": "Deletes a file",
  "annotations": {
    "readOnly": false,      // Does this mutate state?
    "destructive": true,    // Can this cause data loss?
    "idempotent": false     // Safe to retry?
  }
}
```

**Use Cases:**

- AI models can assess risk before calling tools
- Clients can warn users about destructive operations
- Retry logic for idempotent operations

**ChromaCore Tools:**

```python
# Example: ChromaCore tool annotations
{
  "name": "store_node",
  "annotations": {
    "readOnly": false,
    "destructive": false,  # Adds data, doesn't delete
    "idempotent": True     # Same input = same result
  }
}

{
  "name": "delete_backpack",
  "annotations": {
    "readOnly": false,
    "destructive": true,   # PERMANENT DATA LOSS
    "idempotent": False
  }
}
```

---

### 4. Elicitation (Server-Initiated User Input)

**Added:** Servers can request additional info from users (PR #382, Jun 2025)

**Flow:**

1. AI calls MCP tool
2. Server realizes it needs user input (e.g., "Which variant?")
3. Server returns `ElicitationRequest`
4. Client prompts user
5. User provides input
6. Request continues with additional context

**Practical Example:**

```python
# Server-side tool
@server.tool()
async def assign_hashtag(hashtag: str, zone: str = None):
    if not zone:
        # Request elicitation
        return {
            "elicit": {
                "prompt": "Which zone should this hashtag be assigned to?",
                "enum": ["Core", "Mid", "Outer"]
            }
        }

    # Zone provided, complete the assignment
    result = semantic_stack.assign(hashtag, zone)
    return {"content": [{"type": "text", "text": f"Assigned #{hashtag} to {zone}"}]}
```

**User Experience:**

```
User: "Add Python to my semantic stack"
AI: [Calls assign_hashtag(hashtag="python")]
Server: [Returns elicitation request]
Client: [Prompts user with dropdown]
User: [Selects "Mid"]
AI: [Recalls assign_hashtag(hashtag="python", zone="Mid")]
Server: [Completes assignment]
Response: "Assigned #python to Mid"
```

**ChromaCore Impact:** Can make interactive tool calls without failing on missing params.

---

### 5. JSON-RPC Batching

**Added:** Support for batching multiple requests (PR #228, Mar 2025)

**Benefit:**

- Reduce round-trips for bulk operations
- Query multiple resources in one request

**Practical Example:**

```python
# Client sends batch request
batch = [
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "query_knn", "arguments": {"tags": ["python", "async"]}}, "id": 1},
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "query_knn", "arguments": {"tags": ["rust", "async"]}}, "id": 2},
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "query_knn", "arguments": {"tags": ["go", "concurrency"]}}, "id": 3}
]

# Server returns batch response
[
    {"jsonrpc": "2.0", "result": {...}, "id": 1},
    {"jsonrpc": "2.0", "result": {...}, "id": 2},
    {"jsonrpc": "2.0", "result": {...}, "id": 3}
]
```

**Performance Impact:**

- Single request: 3 × 50ms latency = 150ms total
- Batched: 1 × 50ms latency = 50ms total
- **3x faster** for multi-query operations

**ChromaCore Impact:** Batch `query_knn` requests for multiple hashtag combinations.

---

### 6. Progress Notifications

**Enhanced:** Added `message` field to `ProgressNotification`

**Before:**

```json
{
  "progressToken": "task-123",
  "progress": 0.5,
  "total": 1.0
}
```

**After:**

```json
{
  "progressToken": "task-123",
  "progress": 0.5,
  "total": 1.0,
  "message": "Processing 5000/10000 nodes..."
}
```

**ChromaCore Impact:** Show descriptive progress for expensive operations (bulk node import, backpack export).

---

### 7. Audio Content Type

**Added:** Support for audio data alongside text/image (Mar 2025)

**Not directly relevant to ChromaCore** unless building audio-annotated knowledge bases.

---

### 8. Resource Links in Tool Results

**Added:** Tools can return links to additional resources (PR #603, Jun 2025)

**Example:**

```json
{
  "content": [{"type": "text", "text": "Node created"}],
  "links": [
    {"uri": "resource://nodes/42", "type": "related"}
  ]
}
```

**ChromaCore Impact:** After `store_node`, return link to the created node resource.

---

### 9. Icons for Tools/Resources/Prompts

**Added:** Metadata field for icons (SEP-973, Nov 2025)

**Example:**

```json
{
  "name": "store_node",
  "description": "Store a new node",
  "icon": "https://chromacore.dev/icons/store.svg"
}
```

**ChromaCore Impact:** Can provide visual icons in MCP-UI interface.

---

### 10. Tasks (Async Operations)

**Added:** Experimental support for long-running operations (SEP-1686, Nov 2025)

**Problem:** MCP is synchronous - everything waits for completion. Bad for operations taking minutes/hours.

**Solution:** Tasks with polling and deferred result retrieval.

**Flow:**

1. Client calls tool
2. Server returns `TaskCreated` with task ID
3. Client polls for status
4. Server returns progress updates
5. Eventually returns final result

**ChromaCore Impact:** Use for expensive operations:

- Large backpack import/export
- Bulk node recalculation
- Multi-backpack mesh queries

---

### 11. Enhanced Enum Support

**Improved:** Standardized enum handling (SEP-1330, Nov 2025)

**Supports:**

- Titled enums (display names)
- Untitled enums (value-only)
- Single-select vs multi-select
- Follows JSON Schema standards

**ChromaCore Impact:** Better tool param validation for zone selection, query modes, etc.

---

### 12. Security Best Practices

**Enhanced:** Comprehensive security guidance (Jun 2025)

**Key Principles:**

1. **Explicit User Consent** - Tools must request permission for sensitive actions
2. **Data Privacy** - No PII leakage in logs/telemetry
3. **Tool Execution Safety** - Validate inputs, prevent injection
4. **Transport Security** - TLS for all remote connections

**ChromaCore Impact:** Follow security checklist for MCP server implementation.

---

### 13. Completions Capability

**Added:** Argument autocompletion for tool inputs (Mar 2025)

**Example:**
User types: `assign_hashtag(zone="M`
Server suggests: `["Mid", "Mid Zone"]`

**ChromaCore Impact:** Can autocomplete hashtag names from semantic stack.

---

## Governance & Ecosystem Changes

### MCP Governance Model (SEP-932, Jun 2025)

- Formalized roles and decision-making
- Specification Enhancement Proposal (SEP) process
- Working Groups and Interest Groups
- SDK tiering system (compliance levels)

### MCP Registry (Sep 2025)

- **Official catalog of MCP servers:** https://registry.modelcontextprotocol.io
- Public and private sub-registries
- API for discovery
- ChromaCore can publish server to registry

### SDK Tiering System (SEP-1730, Nov 2025)

**Tiers:**

- **Tier 1:** Full spec compliance, fast updates, official support
- **Tier 2:** Core features, community-maintained
- **Tier 3:** Experimental, partial compliance

**ChromaCore SDKs:**

- Python: Use official `@modelcontextprotocol/sdk` (Tier 1)
- TypeScript: Use official `@modelcontextprotocol/sdk` (Tier 1)
- Rust: Use official Rust SDK (Tier 1, maintained with collaboration)

---

## Breaking Changes

**None.** MCP follows strict backwards compatibility. Clients/servers negotiate protocol version at connection time.

**Version Negotiation:**

```
Client: "I support 2024-11-05, 2025-03-26"
Server: "I support 2025-03-26, 2025-06-18"
→ They agree on 2025-03-26
```

---

## ChromaCore Implementation Checklist

- [ ] Use Streamable HTTP transport for remote deployments
- [ ] Implement OAuth 2.1 if accessing protected resources
- [ ] Add tool annotations (readOnly, destructive, idempotent)
- [ ] Support elicitation for interactive params
- [ ] Use JSON-RPC batching for bulk operations
- [ ] Implement progress notifications for long-running ops
- [ ] Consider Tasks for async operations (backpack export, etc.)
- [ ] Add icons for tools/resources
- [ ] Support completions for hashtag autocomplete
- [ ] Follow security best practices doc
- [ ] Register in MCP Registry once stable

---

## Official Resources

- **Specification:** https://modelcontextprotocol.io/specification/
- **Changelog:** https://modelcontextprotocol.io/specification/2025-11-25/changelog
- **GitHub:** https://github.com/modelcontextprotocol
- **Blog:** https://blog.modelcontextprotocol.io
- **Registry:** https://registry.modelcontextprotocol.io
- **Discord:** Official MCP community server

---

**End of Knowledge Patch**
