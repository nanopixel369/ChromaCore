## Knowledge Patch: Agent Skills and Claude Skills
**Patch ID:** AGENT\_SKILLS\_2025Q4\_2026Q1
**Baseline cutoff:** Aug 2025
**Paradigm update window:** Oct 16, 2025 → Dec 18, 2025 (standardization) → Dec 17, 2025 (VS Code docs)
**What changed:** “Skills” became a filesystem-native, cross-agent packaging format for procedural knowledge plus optional executable utilities, using progressive disclosure so agents load only what they need.

---

### 1) Core concept
**Agent Skills** are modular capability packages stored as folders on disk. Each skill is anchored by a required `SKILL.md` file that starts with YAML frontmatter. Agents preload only `name` and `description` for discovery, then load the full instructions only when the skill is selected. This design is explicitly about **progressive disclosure** to avoid bloating the context window while allowing “effectively unbounded” supporting material via linked files and scripts.

Practical intent:

* Encode repeatable workflows, standards, and “how we do things here.”
* Make activation _model-invoked_ (implicit) instead of always-on.
* Bundle deterministic code when prose would be fragile or expensive.

---

### 2) Skill anatomy
A skill is a directory with this minimum:

* `SKILL.md` (required)
	
	* YAML frontmatter: **`name`**, **`description`** required.
	* Markdown body: instructions, examples, navigation links to supporting files.

Optional, common substructure:

* `scripts/` for executable helpers (agent runs them; output is what consumes context)
* `references/` for docs the agent reads when needed
* `assets/` for templates, forms, fixtures, examples

**Claude Code-specific constraint:** keep `SKILL.md` under ~500 lines and link out to references; keep references “one level deep” (avoid chains of links that cause partial reads).

---

### 3) Activation lifecycle (how agents actually use skills)
Across implementations, the operational loop is consistent:

1. **Discovery at startup**
	
	* Agent loads only `name` and `description` for all installed skills.
2. **Selection**
	
	* Implicit: model selects by semantic match against `description`.
	* Explicit (Codex): user selects via `/skills` or `$skill-name` mention.
3. **Load + execute**
	
	* Agent reads full `SKILL.md` and any linked files it decides are needed.
	* Agent may execute scripts in the skill directory without loading script contents. 

Key design lever: the **description is the routing surface**. It is both a semantic trigger and a scope declaration for when the skill should be applied.

---

### 4) Scope and precedence (where skills live)
Different runtimes define different search paths and precedence. The common pattern is layered overrides: higher-scope wins on name collisions.

#### Claude Code locations
* Personal: `~/.claude/skills/` (applies across your projects)
* Project: `.claude/skills/` (committable, shared with repo collaborators)
* Enterprise and plugin layers also exist; higher precedence overrides lower on name collisions.

#### VS Code (GitHub Copilot) locations
* Recommended shared location: `.github/skills/`
* Legacy supported location: `.claude/skills/

#### OpenAI Codex locations
Codex loads skills from multiple scopes, including:

* Repo-scoped: `$CWD/.codex/skills`, `$REPO_ROOT/.codex/skills`, plus a parent-folder repo scope
* User-scoped: `~/.codex/skills` (default on macOS and Linux)
* Admin-scoped: `/etc/codex/skills`
* System-bundled skills (lowest precedence)

---

### 5) Metadata fields and validation surface
Minimum cross-agent contract:

* `name`: lowercase, hyphenated identifier
* `description`: single-line, selection-oriented capability statement

Claude Code documents additional frontmatter fields:

* `allowed-tools` (Claude Code only): restrict which tools can run without additional permission prompts while the skill is active
* `model`: specify a model override for when the skill is active

OpenAI Codex documents an optional `metadata` section, e.g. `short-description`, and states extra keys are ignored.

---

### 6) Tooling model: scripts as “zero-context execution”
A central shift versus older “prompt bundles” is that skills formalize **deterministic compute as part of the capability**:

* Scripts can be executed directly.
* The agent can use script output as authoritative computed artifacts.
* This improves repeatability and cost profile versus token-based simulation of computation.

This is why skills pair naturally with MCP:

* MCP provides external tools and data connections.
* Skills provide procedural playbooks for when and how to use those tools.

---

### 7) Interaction with “agents” and “instructions” files
In Claude Code, Skills sit alongside other control surfaces:

* Skills: model-invoked, task-scoped guidance packages
* `CLAUDE.md`: always-on, project-wide instruction layer
* Slash commands: explicitly invoked prompt macros
* Subagents: separate contexts with their own tool access

Subagent coupling detail (Claude Code):

* Subagents do not inherit skills by default.
* A custom subagent can preload skills via a `skills:` field in its `.claude/agents/<agent>/AGENT.md`.

---

### 8) The “open standard” moment
Agent Skills were published as an **open standard** to enable portability across vendors and runtimes, explicitly called out as an update on Dec 18, 2025. Practically, that is why you now see compatible implementations across Claude, VS Code Copilot, and OpenAI Codex documentation.

---

### 9) Security model and threat surface
Skills expand capability via:

* Instructions that can steer tool use.
* Bundled scripts and dependencies.
* Optional links to external resources.

The primary security guidance from the originating authors:

* Install only from trusted sources.
* Audit bundled files and scripts before use.
* Pay close attention to network access, dependencies, and any instructions that could cause data exfiltration or unsafe actions.

---

### 10) Minimal, canonical template (portable)

```markdown
---
name: your-skill-name
description: What it does, and the user-intent phrases that should trigger it.
---

# Your Skill Name

## Intent
State the exact situations where this skill should be applied.

## Procedure
Step-by-step, deterministic when possible.

## Decision points
List the forks Claude must choose between and the conditions.

## Resources
- If you need deeper docs, link to local files: [REFERENCE.md](REFERENCE.md)

## Scripts
Prefer “run this script” over “read this script” when the content is only useful as execution.
```

---