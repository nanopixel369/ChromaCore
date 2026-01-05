# AGENTS.md Specification Knowledge Patch (2025)

## Overview

AGENTS.md is an open, standardized Markdown format that emerged in 2025 as a unified way to provide AI coding agents with project-specific instructions, build commands, conventions, and context. Think of it as "README.md for machines"—a dedicated, predictable location for agent-focused guidance that complements human-facing documentation.

**Origin:** Collaborative effort across AI development ecosystem (OpenAI, Google, Cursor, Factory, Amp)
**Current Status:** Active standard, 20,000+ GitHub repos adopted
**Stewardship:** Agentic AI Foundation under Linux Foundation
**Key Date:** Widely adopted throughout 2025

## Core Purpose

### The Problem It Solves

Before AGENTS.md, every AI coding tool used proprietary configuration:
- `.cursor/rules`
- `claude.md`
- Tool-specific config files
- Scattered, inconsistent formats

This created:
- Configuration sprawl across projects
- Tool lock-in
- Duplication of context across files
- Friction when switching AI tools

### The Solution

AGENTS.md provides:
- **Single, predictable location** for agent instructions
- **Tool-agnostic format** (standard Markdown)
- **Cross-ecosystem compatibility** across 20+ AI tools
- **Complement to README** without cluttering human docs

## Specification Details

### File Format

- **Format:** Standard Markdown (no rigid schema required)
- **Location:** Repository root or nested in subdirectories
- **Name:** `AGENTS.md` (case-sensitive)
- **Override:** `AGENTS.override.md` for specialized contexts
- **Fallbacks:** Configurable alternative names (tool-specific)

### Discovery & Precedence

AI agents discover instructions through a hierarchical search:

1. **Global Scope:** Check Codex home directory (`~/.codex` or custom `CODEX_HOME`)
   - `AGENTS.override.md` wins if present
   - Otherwise `AGENTS.md`

2. **Project Scope:** Walk from repository root down to current directory
   - Check each directory for `AGENTS.override.md` or `AGENTS.md`
   - Check configured fallback filenames

3. **Merge Order:** Files concatenate from root down (closer files take precedence)

4. **Override Pattern:** Closest file to edited file wins; explicit user prompts override everything

### Multiple AGENTS.md Files

Projects can nest AGENTS.md files for package-level instructions:

```
project-root/
├── AGENTS.md                    # Root instructions
├── packages/
│   ├── frontend/
│   │   └── AGENTS.md           # Frontend-specific
│   └── services/
│       ├── payments/
│       │   └── AGENTS.override.md  # Override for sensitive code
│       └── auth/
│           └── AGENTS.md       # Auth-specific
```

Example: OpenAI organization repos currently maintain ~88 AGENTS.md files across subcomponents.

## Typical Content Structure

### Six Core Areas (Recommended)

Hitting these areas places you in the top tier of AGENTS.md quality:

1. **Commands**
   - Build, test, lint, typecheck commands
   - Development workflow commands
   - Explicit command strings, not descriptions

2. **Testing**
   - Testing frameworks used
   - How to run tests
   - Test file patterns
   - Specific testing requirements

3. **Project Structure**
   - Directory layout
   - File organization conventions
   - Where different types of code live
   - Module boundaries

4. **Code Style**
   - Formatting rules
   - Naming conventions
   - Line length limits
   - Indentation style
   - Language-specific preferences

5. **Git Workflow**
   - Branch naming conventions
   - Commit message format
   - PR requirements
   - Review process

6. **Boundaries**
   - Files agents should NEVER touch
   - Operations agents cannot perform
   - Security-sensitive areas
   - External dependencies to avoid modifying

### Additional Common Sections

- **Tech Stack:** Specific versions and key dependencies
- **Environment Setup:** Configuration requirements
- **Security:** Auth flows, API keys, sensitive data handling
- **Deployment:** Release process, deployment commands
- **Domain Knowledge:** Business logic, domain vocabulary
- **Gotchas:** Common pitfalls and edge cases

## Usage Examples

### Minimal Example

```markdown
# MyProject

## Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Code Style
- TypeScript strict mode
- 2-space indentation
- Single quotes

## Boundaries
- Never modify `./config/production.yaml`
- Never touch files in `./vendor/`
```

### Comprehensive Example

```markdown
# MyProject

Full-stack app with React frontend and Node.js backend.

## Tech Stack
- React 18 with TypeScript
- Node.js 20+
- Vite
- Tailwind CSS v3.4
- Vitest for testing

## Commands
- Dev server: `pnpm dev`
- Build: `pnpm build`
- Test: `pnpm test --run --no-color`
- Test single file: `pnpm test --run src/path.test.ts`
- Lint: `pnpm lint`
- Type check: `pnpm check`

## Project Structure
- `src/client/` — React frontend (write UI code here)
- `src/server/` — Express backend (write API code here)
- `src/shared/` — Shared utilities
- `tests/` — Test files mirror src structure

## Code Style
- TypeScript strict mode enabled
- Single quotes, trailing commas, no semicolons
- 100-character line limit
- Use `const` and `let` (never `var`)
- Prefer functional components and hooks

## Testing
- Use Vitest for all tests
- Test files: `*.test.ts` or `*.spec.ts`
- Run tests before committing
- Coverage threshold: 80%

## Git Workflow
- Branch format: `feature/description` or `fix/description`
- Commit format: `type(scope): description`
- Always run `pnpm lint && pnpm test` before PR
- Squash commits on merge

## Boundaries
- Never modify `package-lock.json` directly
- Never touch files in `node_modules/`
- Never change database migrations in `migrations/`
- Don't add new dependencies without discussion

## Security
- API keys in `.env` (never commit)
- Use environment variables for secrets
- Validate all user input
- Sanitize database queries

## Domain Knowledge
- "User" refers to authenticated account
- "Session" expires after 24h of inactivity
- Payment processing happens via Stripe webhook
```

## Persona-Specific AGENTS.md

Advanced pattern: Create specialized agent personas in `.github/agents/`

### Example: Documentation Agent

```markdown
--- 
name: docs_agent
description: Expert technical writer for this project
---

You are an expert technical writer for this project.

## Your Role
- Fluent in Markdown and TypeScript
- Write for developer audience
- Focus on clarity and practical examples
- Read code from `src/`, write docs to `docs/`

## Tech Stack
- React 18, TypeScript, Vite, Tailwind CSS

## File Structure
- `src/` — Source code (READ from here)
- `docs/` — Documentation (WRITE to here)
- `tests/` — Unit/integration tests (REFERENCE)

## Commands
- Build docs: `pnpm docs:build`
- Preview: `pnpm docs:dev`

## Style Guide
- Use active voice
- Code examples for every feature
- Include both success and error cases
- Link to related docs with [[wikilinks]]

## Boundaries
- NEVER modify source code in `src/`
- NEVER delete existing documentation
- ALWAYS preserve existing links
```

## Tool Integration

### Supported Tools (20+ as of 2025)

**Major Players:**
- OpenAI Codex (native support + custom instructions)
- Google's Jules & Gemini CLI
- Cursor
- GitHub Copilot
- Amp (native support since May 2025, multiple files since July 2025)
- Factory Droid
- Aider
- RooCode
- Windsurf
- Replit
- Claude Code
- Firebase Studio
- OpenCode

**Integration Patterns:**
- **Native:** Tool directly reads AGENTS.md
- **Symbolic Link:** Create symlink from tool's config to AGENTS.md
- **Wrapper:** Tool wraps AGENTS.md into its format

### Codex-Specific Features

OpenAI Codex has enhanced AGENTS.md support:

**Configuration:** `project_doc_fallback_filenames` in config
**Override Pattern:** `AGENTS.override.md` beats `AGENTS.md`
**Verification:** `codex status` shows discovered files
**Max Size:** `project_doc_max_bytes` config setting

**Troubleshooting:**
- Empty files ignored
- Case-sensitive filenames
- Check `CODEX_HOME` environment variable for unexpected profiles

### Aider Integration

Configure Aider to read AGENTS.md:

```bash
aider --read agents.md
```

Or in `.aider.conf.yml`:
```yaml
read: agents.md
```

### Gemini CLI Integration

Configure Gemini CLI in `.gemini_config`:
```
project_docs = ["agents.md"]
```

## Best Practices from 2,500+ Repos Analysis

### Be Specific About Stack

❌ Bad: "React project"
✅ Good: "React 18 with TypeScript, Vite, and Tailwind CSS v3.4"

### Provide Exact Commands

❌ Bad: "Run tests"
✅ Good: "`pnpm test --run --no-color`"

### Show Code Examples

Don't just list rules—show what good code looks like:

```markdown
## Naming Conventions
Components use PascalCase:
```typescript
// ✅ Good
export function UserProfile() { }

// ❌ Bad
export function userProfile() { }
```

### Set Clear Boundaries

Be explicit about what agents cannot do:

```markdown
## Boundaries
- NEVER modify database schema files
- NEVER change API route definitions without approval
- NEVER remove existing tests
- NEVER add dependencies without discussion
```

### Iterative Improvement

1. Start simple
2. Test with real agent tasks
3. Add detail where agent makes mistakes
4. Don't write everything upfront

### Focus on What's Different

Don't document standard practices—focus on:
- Project-specific conventions
- Unusual patterns
- Gotchas and edge cases
- Domain-specific vocabulary

## Common Patterns

### Monorepo Pattern

Root AGENTS.md for global rules, package-specific for local:

```markdown
# Root AGENTS.md
All packages use pnpm workspaces.
Global commands:
- `pnpm build` — Build all packages
- `pnpm test` — Test all packages

See each package's AGENTS.md for package-specific rules.
```

### Security-Sensitive Areas

Use AGENTS.override.md for sensitive code:

```markdown
# services/payments/AGENTS.override.md

## High-Security Zone
This service handles payment processing.

## Extra Rules
- Run `make test-payments` instead of global test
- Never log credit card data
- Never rotate API keys without security team approval
- All changes require security review

## Verification
- Run PCI compliance check: `make pci-check`
- Security scan: `make security-scan`
```

### Legacy Codebase Pattern

Guidance for working with older code:

```markdown
## Legacy Code Guidelines
- `src/legacy/` contains old PHP code (v5.6)
- Don't refactor unless specifically asked
- Maintain existing patterns even if not ideal
- Tests may be missing—add them when touching code
```

## AGENTS.md vs. Other Files

### vs. README.md

| README.md | AGENTS.md |
|-----------|-----------|
| For humans | For AI agents |
| Quick start | Detailed commands |
| Contribution guide | Exact conventions |
| Project overview | Build/test specifics |
| Intentionally concise | Can be comprehensive |

### vs. Tool-Specific Config

| Tool Config | AGENTS.md |
|-------------|-----------|
| Tool-locked | Tool-agnostic |
| Proprietary format | Standard Markdown |
| Must learn per-tool | Learn once |
| Hard to maintain | Single source of truth |

### vs. Spec-Driven Development

AGENTS.md complements SDD:
- **SDD Specs:** What to build (features, requirements)
- **AGENTS.md:** How to build it (commands, conventions, boundaries)

Together: Specs + AGENTS.md = complete context for agents

## Adoption Metrics (2025)

- **20,000+ repos** on GitHub have adopted
- **Major projects:** OpenAI (88 files), many OSS frameworks
- **Enterprise:** Uber, Databricks using in internal tooling
- **Tool support:** 20+ AI coding tools
- **Community:** Active GitHub org at `github.com/agentsmd/agents.md`

## Future Evolution

Expected developments as standard matures:

### Schema Formalization

While no rigid schema exists now, patterns emerging:
- Section naming conventions
- Command format standards
- Boundary declaration syntax

### Persona System

Growing use of specialized agent personas:
- Test agents
- Documentation agents
- Security review agents
- Each with own `.github/agents/*.md` file

### Integration Deepening

- IDE plugins for AGENTS.md authoring
- Linting/validation tools
- Auto-generation from project analysis
- Templates for common project types

## Critical Success Factors

For AGENTS.md to remain valuable:

1. **Stay Simple:** Markdown only, no complex schemas
2. **Tool Independence:** Never favor one AI tool
3. **Community Driven:** Open governance under Linux Foundation
4. **Backward Compatible:** Don't break existing files
5. **Clear Value:** Save developers time, reduce friction

## Common Mistakes to Avoid

### Over-Documentation

Don't replicate entire project docs—focus on agent-specific needs.

### Vague Commands

❌ "Run the tests somehow"
✅ "`pnpm test --run`"

### Assuming Knowledge

Don't assume agent knows your framework's conventions—spell them out.

### Forgetting to Update

Keep AGENTS.md in sync with actual project conventions.

### No Boundaries

Always include boundaries—what agents should never do.

## Resources

- Official Website: `https://agents.md`
- GitHub Organization: `https://github.com/agentsmd/agents.md`
- Specification Repository: `https://github.com/agentmd/agent.md`
- GitHub Blog Post: `https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/`
- Factory Documentation: `https://docs.factory.ai/cli/configuration/agents-md`
- OpenAI Codex Guide: `https://developers.openai.com/codex/guides/agents-md/`

## Related Concepts

[[Spec-Driven Development]] - Complementary methodology
[[Context Engineering]] - Underlying principle
[[Vibe Coding]] - Contrast methodology
[[Agentic Development]] - Broader category
