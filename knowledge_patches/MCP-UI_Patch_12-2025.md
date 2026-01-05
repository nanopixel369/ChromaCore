# MCP-UI / MCP Apps: Knowledge Patch

**Status:** Post-Knowledge Cutoff Update (Nov 2024 → Dec 2025)  
**Topic:** Interactive UI Extensions for Model Context Protocol  
**Relevance:** ChromaCore will use MCP-UI for its 3D visualization interface

---

## What is MCP-UI?

**MCP-UI** (now standardized as **MCP Apps Extension, SEP-1865**) is an official extension to the Model Context Protocol that enables MCP servers to deliver **interactive user interfaces** alongside their tool responses.

Instead of returning only JSON data that the client must interpret and render, MCP servers can now return fully-functional UI components that render directly in the host application.

**Key Point:** UI is **server-initiated** - when an AI calls a tool, the server can optionally include UI in its response. The client detects support via capability negotiation.

---

## The Problem It Solves

**Before MCP-UI:**

- AI assistants could only return text responses
- Complex data (charts, maps, product galleries) required client-side rendering logic
- Every MCP client had to build custom UI handlers for every type of data
- User interactions (forms, selectors, buttons) were awkward text-based exchanges

**After MCP-UI:**

- Servers deliver pre-built, interactive UI components
- Clients render these in sandboxed iframes
- Users interact with visual interfaces (click buttons, select options, view charts)
- Server maintains control through intent-based messaging

---

## How It Works: Complete Flow

### 1. Capability Negotiation (Initialization)

When client connects to server, they exchange capabilities:

```json
// Client announces UI support
{
  "method": "initialize",
  "params": {
    "capabilities": {
      "experimental": {
        "ui": {
          "supported": true,
          "mimeTypes": ["text/html", "text/uri-list"]
        }
      }
    }
  }
}

// Server confirms
{
  "capabilities": {
    "experimental": {
      "ui": {
        "supported": true
      }
    }
  }
}
```

**Fallback:** If client doesn't support UI, server returns text-only response.

---

### 2. Tool Invocation (User Action)

User says: *"Show me the ChromaCore semantic stack visualization"*

AI calls tool:

```json
{
  "method": "tools/call",
  "params": {
    "name": "view_semantic_stack"
  }
}
```

---

### 3. Server Response (With UI)

Server returns **both** text content **and** UI resource:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Semantic stack has 10,000 anchors. Opening 3D visualizer..."
    }
  ],
  "_meta": {
    "ui": [
      {
        "type": "resource",
        "resource": {
          "uri": "ui://chromacore/stack-viz",
          "mimeType": "text/html",
          "text": "<!DOCTYPE html><html><!-- Full 3D viz app --></html>"
        }
      }
    ]
  }
}
```

**Key:** UI is in `_meta.ui` field, separate from text content.

---

### 4. Client Rendering

Client sees `_meta.ui` and:

1. Creates sandboxed iframe
2. Injects HTML from `text` field (or loads from URL if `mimeType: text/uri-list`)
3. Renders in chat interface
4. Sets up postMessage bridge for communication

---

### 5. User Interaction → Intent Messages

User clicks button in UI: *"Assign #python to Mid zone"*

UI sends intent via postMessage:

```javascript
// Inside iframe (UI code)
window.parent.postMessage({
  jsonrpc: "2.0",
  method: "mcp/intent",
  params: {
    action: "assign_hashtag",
    data: {
      hashtag: "python",
      zone: "Mid"
    }
  }
}, "*");
```

---

### 6. Host Handles Intent

Client receives intent, AI decides action:

- Could call another tool: `assign_hashtag(hashtag="python", zone="Mid")`
- Could ask user for confirmation
- Could update UI state

---

### 7. Detection and Fallback Strategy

**Server-side code:**

```python
def view_semantic_stack(context):
    # Check if client supports UI
    if context.client_capabilities.get("ui", {}).get("supported"):
        # Return UI version
        return {
            "content": [{"type": "text", "text": "Opening visualizer..."}],
            "_meta": {
                "ui": [create_ui_resource(...)]
            }
        }
    else:
        # Fallback: text-only
        return {
            "content": [
                {"type": "text", "text": "Semantic Stack:\n- 1000 Core anchors\n- 6500 Mid anchors\n- 2500 Outer anchors"}
            ]
        }
```

**Headless mode:** User can disable UI in client settings → server detects and skips UI.

---

## Building UI: Server-Side Code Examples

### Python (ChromaCore Example)

```python
from mcp_ui_server import create_ui_resource

@server.tool()
async def view_semantic_stack(zone: str = "all"):
    """Display 3D visualization of semantic stack"""

    # Check client capability
    if not context.supports_ui():
        return text_fallback_response()

    # Read HTML template
    with open("ui/stack_visualizer.html") as f:
        html_content = f.read()

    # Create UI resource
    ui = create_ui_resource({
        "uri": f"ui://chromacore/stack/{zone}",
        "content": {
            "type": "inline",  # or "externalUrl" for hosted UI
            "html": html_content
        },
        "encoding": "text"
    })

    return {
        "content": [
            {"type": "text", "text": f"Displaying {zone} zone..."}
        ],
        "_meta": {
            "ui": [ui]
        }
    }
```

### TypeScript (MCP Server)

```typescript
import { createUIResource } from '@mcp-ui/server';

server.tool('view_semantic_stack', async (args, context) => {
  if (!context.clientCapabilities?.ui?.supported) {
    return { content: [{ type: 'text', text: 'UI not supported' }] };
  }

  const ui = createUIResource({
    uri: 'ui://chromacore/stack-viz',
    content: {
      type: 'externalUrl',
      iframeUrl: 'https://chromacore.dev/viz.html'  // Hosted UI
    },
    encoding: 'text'
  });

  return {
    content: [{ type: 'text', text: 'Opening visualizer...' }],
    _meta: { ui: [ui] }
  };
});
```

### Inline vs External URLs

**Inline HTML (`text/html`):**

- Pros: Self-contained, works offline, no hosting needed
- Cons: Limited size, harder to update
- Use for: Small widgets, forms, simple visualizations

**External URL (`text/uri-list`):**

- Pros: No size limit, can update independently, CDN-hosted
- Cons: Requires network, server hosting
- Use for: Complex apps, 3D visualizations, large libraries

**ChromaCore recommendation:** External URL for 3D viz (Three.js is big), inline for simple forms.

---

## Core Architecture

### UI Resource Schema

MCP servers return a `UIResource` object:

```typescript
interface UIResource {
  type: 'resource';
  resource: {
    uri: string;                    // e.g., "ui://component/id"
    mimeType: string;                // Content type (see below)
    text?: string;                   // Inline content
    blob?: string;                   // Base64-encoded content
  };
}
```

### Supported MIME Types

| MIME Type                           | Description                 | Use Case                                   |
| ----------------------------------- | --------------------------- | ------------------------------------------ |
| `text/html`                         | Inline HTML or external URL | Self-contained UIs, embedded apps          |
| `text/uri-list`                     | External URL to load        | Hosting UI on external server              |
| `application/vnd.mcp-ui.remote-dom` | Remote DOM (Shopify)        | Framework-agnostic, host-styled components |

### Communication Protocol

UI components communicate with the host using **standard MCP JSON-RPC over postMessage**:

- UI uses `@modelcontextprotocol/sdk` to send messages
- All communication is loggable and auditable
- No custom protocols needed

---

## Security Model

MCP Apps are sandboxed with multiple layers:

1. **Iframe Sandboxing** - All UI runs in restricted iframes
2. **Predeclared Templates** - Hosts can review HTML before rendering
3. **Auditable Messages** - All UI-to-host communication logged via JSON-RPC
4. **No Direct State Mutation** - Components send intents, host decides actions

---

## Example: Product Search with UI

**Traditional MCP (text-only):**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 3 products: Widget A ($10), Widget B ($15), Widget C ($20)"
    }
  ]
}
```

**MCP-UI (interactive):**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 3 products"
    }
  ],
  "ui": {
    "type": "resource",
    "resource": {
      "uri": "ui://products/search-results",
      "mimeType": "text/html",
      "text": "<html><!-- Product cards with images, variant selectors, add-to-cart buttons --></html>"
    }
  }
}
```

**User Experience:**

- Sees visual product cards with images
- Clicks variant selector to change size/color
- Clicks "Add to Cart" button
- Component sends intent: `{"action": "add_to_cart", "product_id": "123", "variant": "large-blue"}`
- Host (AI assistant) receives intent and executes MCP tool call

---

## Intent-Based Messaging

Components don't modify state directly. They bubble up **intents** the host interprets:

```typescript
// Component sends intent
{
  "action": "add_to_cart",
  "product_id": "widget-a",
  "quantity": 2
}

// Host receives intent, decides action
// Could call MCP tool, ask for confirmation, etc.
```

This preserves agent control while enabling rich UX.

---

## Remote DOM Pattern (Shopify)

**Remote DOM** allows components to match the host's look and feel:

1. Server sends JavaScript describing UI structure and events
2. Client renders using its own component library (React, Vue, etc.)
3. Visual appearance matches host app
4. Interactions still use intent-based messaging

**Benefit:** No jarring iframe-in-app experience, native look and feel.

---

## SDK Support

### Server SDKs (Create UI Resources)

**TypeScript:**

```typescript
import { createUIResource } from '@mcp-ui/server';

const ui = createUIResource({
  uri: 'ui://chart/sales-data',
  content: {
    type: 'externalUrl',
    iframeUrl: 'https://charts.example.com/sales'
  },
  encoding: 'text'
});
```

**Python:**

```python
from mcp_ui_server import create_ui_resource

ui = create_ui_resource({
    "uri": "ui://chart/sales-data",
    "content": {
        "type": "externalUrl",
        "iframeUrl": "https://charts.example.com/sales"
    },
    "encoding": "text"
})
```

**Ruby:**

```ruby
require 'mcp_ui_server'

ui = McpUiServer.create_ui_resource(
  uri: 'ui://chart/sales-data',
  content: {
    type: :external_url,
    iframeUrl: 'https://charts.example.com/sales'
  },
  encoding: :text
)
```

### Client SDKs (Render UI Resources)

**React:**

```tsx
import { UIResourceRenderer } from '@mcp-ui/client';

function MyApp({ mcpResource }) {
  return (
    <UIResourceRenderer
      resource={mcpResource.resource}
      onUIAction={(action) => {
        console.log('User action:', action);
        // Handle intent
      }}
    />
  );
}
```

**Web Components (Vanilla JS):**

```html
<ui-resource-renderer id="renderer"></ui-resource-renderer>

<script type="module">
  import '@mcp-ui/client/ui-resource-renderer.wc.js';

  const renderer = document.getElementById('renderer');
  renderer.setAttribute('resource', JSON.stringify(mcpResource.resource));
</script>
```

---

## Adoption

**Major Companies Using MCP-UI:**

- **Shopify** - Product cards, cart flows, checkout components
- **Postman** - API testing interfaces
- **Hugging Face** - Model/dataset browsers
- **ElevenLabs** - Audio player components
- **Material-UI** - Component documentation browser

---

## Standardization Timeline

| Date         | Event                                                                                       |
| ------------ | ------------------------------------------------------------------------------------------- |
| **2024**     | MCP-UI created by Ido Salomon and Liad Yosef (community project)                            |
| **Nov 2025** | MCP Apps Extension (SEP-1865) proposed jointly by Anthropic, OpenAI, and MCP-UI maintainers |
| **Dec 2025** | Official extension, standardized in MCP spec                                                |

---

## ChromaCore Implications

**For ChromaCore MCP Server:**

1. The 3D semantic stack visualizer can be delivered as an MCP-UI component
2. Users interact with the visualization through intents:
   - Click node → send `{"action": "select_anchor", "index": 42}`
   - Submit hashtag → send `{"action": "assign_hashtag", "zone": "Mid", "hashtag": "#python"}`
3. Host receives intents and calls ChromaCore tools
4. No need for separate desktop app - runs in any MCP-UI compatible client

**Supported Clients:**

- Claude.ai (supports MCP Apps)
- Claude Desktop
- Cursor
- Windsurf
- VS Code (with MCP extension)
- Any client implementing SEP-1865

---

## Resources

- **MCP Apps Announcement:** https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/
- **MCP-UI GitHub:** https://github.com/MCP-UI-Org/mcp-ui
- **MCP-UI Website:** https://mcpui.dev/
- **Specification (SEP-1865):** Standardized in MCP spec 2025-11-25

---

**End of Knowledge Patch**
