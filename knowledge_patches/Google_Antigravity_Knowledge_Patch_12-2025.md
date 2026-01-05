# Google Antigravity Knowledge Patch (2025)

## Overview

Google Antigravity is an agent-first integrated development environment released on November 18, 2025, alongside Gemini 3. It represents a fundamental architectural shift from traditional AI coding assistants to autonomous agent orchestration platforms.

**Release Date:** November 18, 2025
**Current Status:** Public preview (free for Gmail accounts)
**Platforms:** macOS, Windows, Linux
**Base Architecture:** Fork of Visual Studio Code

## Core Philosophy

Antigravity operates on an "agent-first" paradigm where AI is not merely a coding assistant but an autonomous actor capable of planning, executing, validating, and iterating on complex engineering tasks with minimal human intervention. The platform treats agents as first-class citizens requiring dedicated workspace and orchestration surfaces.

## Architecture

### Dual-View Interface

**Editor View**
- Traditional AI-powered IDE experience
- Tab completions and inline commands
- Synchronous workflow for hands-on development
- Familiar VS Code keybindings, themes, and extensions
- Full LSP support for language features

**Agent Manager (Mission Control)**
- Primary interface upon launch
- High-level orchestration dashboard
- Manages multiple agents operating asynchronously
- Visualizes parallel work streams across workspaces
- Displays agent status, artifacts, and approval requests
- Enables developers to act as architects defining objectives

### Agent Capabilities

Agents have direct access to:
- Editor (code reading and modification)
- Terminal (command execution)
- Browser (via Gemini 2.5 Computer Use model)

Agents can work:
- In parallel across multiple tasks
- In the background without active supervision
- Asynchronously across different workspaces

## Supported Models

### Primary Models
- **Gemini 3 Pro** - Primary agentic model
- **Gemini 3 Deep Think** (Gemini 3 Pro High) - Advanced reasoning
- **Gemini 3 Flash** - Faster operations

### Additional Models
- **Claude Sonnet 4.5** (Anthropic)
- **Claude Opus 4.5** (Anthropic)
- **GPT-OSS-120B** (Open-source OpenAI variant)

### Specialized Models
- **Gemini 2.5 Computer Use** - Browser control
- **Nano Banana (Gemini 2.5 Image)** - Image editing

## Key Features

### Artifacts System

Rather than exposing raw tool calls, agents produce verifiable deliverables:
- Task lists and implementation plans
- Screenshots and browser recordings
- Change summaries and diffs
- Structured documentation

This artifact-centric approach builds user trust through transparency.

### Native Cloud Integration

First-class support for Google Cloud services:
- Live schema access
- Dataset connectivity
- Infrastructure metadata through supported connectors
- Code generation validated against real system state
- No manual context injection required

### Learning Primitive

Agents can save useful context and code snippets to a knowledge base, improving performance on future tasks through persistent learning.

### Rate Limits

**Free Tier:** Weekly-based rate limit
**Google AI Pro/Ultra:** Priority access with highest rate limits, refreshing every 5 hours

Usage correlates with "work done" - simple tasks consume less quota than complex reasoning operations.

## Performance Characteristics

- Avoids aggressive local indexing
- Relies on cloud-side inference and execution
- Lower local memory pressure compared to Cursor
- Performance profile closer to VS Code while supporting complex AI workflows

## VS Code Compatibility

Since Antigravity is built directly on VS Code:
- All core editor behaviors are identical
- Extensions work without modification
- Settings, themes, and layouts transfer cleanly
- Custom keybindings carry over
- Multi-root workspaces supported
- Debugging workflows unchanged

## Security Considerations

### Known Vulnerabilities (as of November 2025)

**Data Exfiltration via Indirect Prompt Injection**
- Documented vulnerability allows malicious web sources to manipulate Gemini
- Attack vector: poisoned integration guides or documentation
- Can extract credentials and sensitive code via browser subagents
- Default Browser URL Allowlist includes `webhook.site` (attack-friendly)
- Vulnerability persists with `.env` access disabled

**Mitigation Status:** Google includes disclaimer about risks but has not fully mitigated core issues

### User Responsibility Model

Google's approach emphasizes user review:
- Warning displayed on first launch
- Recommends reviewing agent actions
- Agent Manager allows multiple agents without active supervision
- Human-in-the-loop settings let agents choose when to request approval

**Reality Check:** Given the async multi-agent design, comprehensive review of all actions is implausible in practice.

## Comparison to Alternatives

### vs. VS Code
- VS Code: Stable, proven, requires manual AI workflow mediation
- Antigravity: Native multi-agent orchestration, cloud-grounded reasoning

### vs. Cursor
- Cursor: Single conversational agent, local project-wide context
- Antigravity: Multi-agent execution, cloud-side inference, parallel task execution

### vs. Windsurf
Antigravity may be an indirect fork of Windsurf (which itself forks VS Code), though this is debated.

## Use Cases

**Optimal For:**
- Complex multi-step engineering tasks
- Parallel development workflows
- Projects requiring live cloud infrastructure context
- Teams wanting orchestrated autonomous development

**Consider Alternatives When:**
- Maximum stability required (use VS Code)
- Single-repo deep context preferred (use Cursor)
- Google service dependencies unacceptable
- Security posture requires hardened tooling

## Access and Installation

**Download:** `antigravity.google/download`
**Requirements:** Personal Gmail account for preview access
**Authentication:** Internal Google 2FA
**Cost:** Free during public preview

## Resources

- Official site: `https://www.antigravity.google/`
- Codelabs: `https://codelabs.developers.google.com/getting-started-google-antigravity`
- Developer blog: `https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/`

## Context Notes

Antigravity is part of Google's broader exploration of agentic development, running parallel to other experiments like Jules and Gemini CLI. Google considers these "experiments" examining the same technology from different angles. Historical context suggests Google frequently launches competing internal projects, with uncertain long-term commitment (see: Google Graveyard).

## Related Technologies

[[Gemini 3]] - Foundational model powering Antigravity
[[Model Context Protocol]] - Underlying integration standard
[[Agentic Development]] - Broader category and emerging paradigm
