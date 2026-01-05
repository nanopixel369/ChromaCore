# scripts/builder.py

import argparse
import json
from pathlib import Path
from datetime import datetime, UTC

class ModuleRegistry:
    """Maps block codes to their module files and descriptions"""
    
    OS_MODULES = {
        'y': ('yaml.md', 'YAML frontmatter'),
        'ep': ('essential-principles.md', 'Essential principles'),
        'iv': ('intake-validation.md', 'Intake validation (when to use)'),
        'r': ('router.md', 'Router (intake + routing table)'),
        'ws': ('workflow-simple.md', 'Simple workflow'),
        'wc': ('workflow-complex.md', 'Complex workflow with references'),
        'cr': ('code-review.md', 'Code review workflow'),
        'api': ('api-integration.md', 'API integration workflow'),
        'bp': ('best-practices.md', 'Best practices workflow'),
        'esc': ('es-check.md', 'Evolution check'),
        'sc': ('success-criteria.md', 'Success criteria'),
    }
    
    ES_MODULES = {
        'y': ('yaml.md', 'YAML frontmatter'),
        'b': ('binding.md', 'Binding to OS'),
        'lb': ('l1-boundary.md', 'Layer 1/2 boundary map'),
        'ep': ('eval-python.md', 'Evaluation via Python script'),
        'ee': ('eval-embedded.md', 'Evaluation via embedded rubric'),
        'ef': ('eval-flexible.md', 'Flexible evaluation (tries Python, falls back)'),
        'ew': ('evolution-workflow.md', 'Evolution workflow (5 phases)'),
        'vp': ('val-python.md', 'Validation via Python tests'),
        'vm': ('val-mock.md', 'Validation via mock execution'),
        'vn': ('val-manual.md', 'Validation via manual checks'),
    }

class SkillBuilder:
    def __init__(self, modules_dir=None):
        if modules_dir is None:
            # Default to templates/modules relative to script location
            script_dir = Path(__file__).parent.parent
            modules_dir = script_dir / "templates" / "modules"
        self.modules_dir = Path(modules_dir)
        self.registry = ModuleRegistry()
        
    def build_os(self, blocks: str, skill_dir: Path, user_context: dict) -> str:
        """Build OS SKILL.md from blocks and context"""
        
        # Auto-fill common variables
        context = {
            **self._auto_context(skill_dir, "journeyman"),
            **user_context
        }
        
        return self._assemble_modules("os", blocks, context)
    
    def build_es(self, blocks: str, os_dir: Path, user_context: dict) -> str:
        """Build ES SKILL.md from blocks and context"""
        
        # Auto-fill ES-specific variables
        context = {
            **self._auto_context(os_dir / "evolution", None),
            "os-path": "../SKILL.md",
            "os-skill-name": os_dir.name,
            **user_context
        }
        
        return self._assemble_modules("es", blocks, context)
    
    def _auto_context(self, skill_dir: Path, tier: str = None) -> dict:
        """Generate auto-filled context variables"""
        ctx = {
            "skill-name": skill_dir.name,
            "timestamp": datetime.now(UTC).strftime("%m%d%Y %H%M"),
            "version": "0.1.0",
            "current-timestamp": datetime.now(UTC).strftime("%m%d%Y %H%M"),
        }
        
        if tier:
            ctx["tier"] = tier
            ctx["evo-pair-path"] = "evolution/SKILL.md"
            ctx["es-path"] = "evolution/SKILL.md"
        
        return ctx
    
    def _assemble_modules(self, skill_type: str, blocks: str, context: dict) -> str:
        """Assemble modules into complete SKILL.md"""
        module_dir = self.modules_dir / skill_type
        registry = getattr(self.registry, f"{skill_type.upper()}_MODULES")
        
        sections = []
        for code in blocks.split('-'):
            if code not in registry:
                raise ValueError(f"Unknown {skill_type.upper()} module: {code}")
            
            module_file, _ = registry[code]
            template = (module_dir / module_file).read_text()
            rendered = self._render(template, context)
            sections.append(rendered)
        
        return "\n\n".join(sections)
    
    def _render(self, template: str, context: dict) -> str:
        """Replace $variables with context values"""
        result = template
        for key, value in context.items():
            patterns = [
                f"${key}",
                f"${key.replace('_', '-')}",
            ]
            for pattern in patterns:
                result = result.replace(pattern, str(value))
        return result
    
    def extract_l1_map(self, os_path: Path) -> str:
        """Extract L1 boundary map from OS"""
        content = os_path.read_text()
        lines = content.split('\n')
        l1_sections = []
        in_l1 = False
        l1_start = 0
        
        for i, line in enumerate(lines, 1):
            if '<L1>' in line:
                in_l1 = True
                l1_start = i
            elif '</L1>' in line and in_l1:
                section_desc = self._get_section_desc(lines, l1_start, i)
                l1_sections.append(f"- SKILL.md lines {l1_start}-{i}: {section_desc}")
                in_l1 = False
        
        return '\n'.join(l1_sections) if l1_sections else "[No L1 sections detected]"
    
    def _get_section_desc(self, lines: list, start: int, end: int) -> str:
        """Get description from section headers"""
        for line in lines[start:end]:
            if line.startswith('#'):
                return line.lstrip('#').strip()
        return "Core workflow section"


def main():
    parser = argparse.ArgumentParser(description="Build skills from template modules")
    parser.add_argument("--type", choices=["os", "es"], required=True)
    parser.add_argument("--blocks", required=True, help="Block string (e.g. 'y-ep-iv-ws-esc-sc')")
    parser.add_argument("--skill-dir", type=Path, required=True, help="Skill directory path")
    parser.add_argument("--context", type=Path, help="JSON file with user context")
    parser.add_argument("--output", type=Path, required=True, help="Output SKILL.md path")
    
    args = parser.parse_args()
    
    # Load user context
    user_context = {}
    if args.context and args.context.exists():
        user_context = json.loads(args.context.read_text())
    
    # Build skill
    builder = SkillBuilder()
    
    if args.type == "os":
        content = builder.build_os(args.blocks, args.skill_dir, user_context)
    else:
        content = builder.build_es(args.blocks, args.skill_dir, user_context)
    
    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content)
    
    print(f"✓ Built {args.type.upper()} skill: {args.output}")


if __name__ == "__main__":
    main()
