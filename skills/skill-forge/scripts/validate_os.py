#!/usr/bin/env python3
"""
Validates Operational Skill structure and integrity.

Checks:
- YAML frontmatter validity
- L1 tag pairing (<L1> has matching </L1>)
- Required sections present
- Evolution check step exists (for journeyman)
- File structure consistency
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import List, Tuple

class OSValidator:
    def __init__(self, skill_path: Path, tier: str = None):
        self.skill_path = skill_path
        self.tier = tier
        self.errors = []
        self.warnings = []
        
    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"Validating OS: {self.skill_path}")
        
        if not self.skill_path.exists():
            self.errors.append(f"Skill file not found: {self.skill_path}")
            return False
        
        content = self.skill_path.read_text()
        
        # Run checks
        self._check_yaml_frontmatter(content)
        self._check_l1_tags(content)
        self._check_evolution_check(content)
        self._check_required_sections(content)
        
        # Report results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_yaml_frontmatter(self, content: str):
        """Validate YAML frontmatter"""
        if not content.startswith('---'):
            self.errors.append("Missing YAML frontmatter (must start with '---')")
            return
        
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                self.errors.append("YAML frontmatter not properly closed")
                return
            
            frontmatter = yaml.safe_load(parts[1])
            
            # Check required fields
            required = ['name', 'tier', 'description', 'version', 'triggers']
            for field in required:
                if field not in frontmatter:
                    self.errors.append(f"Missing required YAML field: {field}")
            
            # Check tier
            if 'tier' in frontmatter:
                valid_tiers = ['grunt', 'journeyman', 'mastercraft']
                if frontmatter['tier'] not in valid_tiers:
                    self.errors.append(f"Invalid tier: {frontmatter['tier']} (must be grunt/journeyman/mastercraft)")
                
                # Store tier for later checks
                if self.tier is None:
                    self.tier = frontmatter['tier']
            
            # Check journeyman has evo_pair
            if self.tier == 'journeyman' and 'evo_pair' not in frontmatter:
                self.errors.append("Journeyman skill missing 'evo_pair' field in YAML")
                
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML: {e}")
    
    def _check_l1_tags(self, content: str):
        """Validate L1 tag pairing"""
        open_tags = content.count('<L1>')
        close_tags = content.count('</L1>')
        
        if open_tags != close_tags:
            self.errors.append(f"Mismatched L1 tags: {open_tags} opening, {close_tags} closing")
        
        # Check for nested L1 (not allowed)
        lines = content.split('\n')
        depth = 0
        for i, line in enumerate(lines, 1):
            if '<L1>' in line:
                depth += 1
                if depth > 1:
                    self.errors.append(f"Nested L1 tags not allowed (line {i})")
            if '</L1>' in line:
                depth -= 1
                if depth < 0:
                    self.errors.append(f"Closing L1 tag without opening (line {i})")
    
    def _check_evolution_check(self, content: str):
        """Check for evolution check step (journeyman only)"""
        if self.tier == 'grunt':
            # Grunt should NOT have evolution check
            if 'Evolution Check' in content or 'evolution/SKILL.md' in content:
                self.warnings.append("Grunt skill should not have evolution check")
        elif self.tier in ['journeyman', 'mastercraft']:
            # Journeyman/mastercraft should have evolution check (mastercraft might disable it)
            if 'Evolution Check' not in content:
                self.errors.append("Missing evolution check section")
    
    def _check_required_sections(self, content: str):
        """Check for required markdown sections"""
        # Most skills should have some workflow description
        has_workflow = any(marker in content for marker in [
            '## Core Workflow',
            '## Workflow',
            '<routing>',
            '### Step'
        ])
        
        if not has_workflow:
            self.warnings.append("No workflow section detected")
    
    def _print_results(self):
        """Print validation results"""
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ OS validation passed")
        elif not self.errors:
            print("\n✅ OS validation passed (with warnings)")


def main():
    parser = argparse.ArgumentParser(description="Validate Operational Skill")
    parser.add_argument("--skill-path", type=Path, required=True, help="Path to SKILL.md")
    parser.add_argument("--tier", choices=['grunt', 'journeyman', 'mastercraft'], help="Expected tier")
    
    args = parser.parse_args()
    
    validator = OSValidator(args.skill_path, args.tier)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
