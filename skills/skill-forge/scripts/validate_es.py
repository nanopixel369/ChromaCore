#!/usr/bin/env python3
"""
Validates Evolutionary Skill structure and binding to OS.

Checks:
- YAML frontmatter validity
- Binding to OS exists and is valid
- OS file exists at specified path
- Required ES sections present
- Evolution workflow structure
- Validation method present
"""

import argparse
import sys
import yaml
from pathlib import Path

class ESValidator:
    def __init__(self, es_path: Path):
        self.es_path = es_path
        self.errors = []
        self.warnings = []
        
    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"Validating ES: {self.es_path}")
        
        if not self.es_path.exists():
            self.errors.append(f"ES file not found: {self.es_path}")
            return False
        
        content = self.es_path.read_text()
        
        # Run checks
        os_path = self._check_yaml_frontmatter(content)
        if os_path:
            self._check_os_binding(os_path)
        self._check_required_sections(content)
        self._check_evolution_workflow(content)
        self._check_validation_method(content)
        
        # Report results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_yaml_frontmatter(self, content: str) -> Path:
        """Validate YAML frontmatter and return OS path"""
        if not content.startswith('---'):
            self.errors.append("Missing YAML frontmatter")
            return None
        
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                self.errors.append("YAML frontmatter not properly closed")
                return None
            
            frontmatter = yaml.safe_load(parts[1])
            
            # Check required fields
            required = ['name', 'tier', 'description', 'binding']
            for field in required:
                if field not in frontmatter:
                    self.errors.append(f"Missing required YAML field: {field}")
            
            # Check tier (ES should always be journeyman)
            if 'tier' in frontmatter and frontmatter['tier'] != 'journeyman':
                self.errors.append("ES must be journeyman tier")
            
            # Extract OS path from binding
            if 'binding' in frontmatter and isinstance(frontmatter['binding'], dict):
                if 'os_path' in frontmatter['binding']:
                    return Path(frontmatter['binding']['os_path'])
                else:
                    self.errors.append("Binding missing 'os_path' field")
            else:
                self.errors.append("Missing or invalid 'binding' field in YAML")
                
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML: {e}")
        
        return None
    
    def _check_os_binding(self, os_path: Path):
        """Check that OS exists at specified path"""
        # Resolve relative to ES file location
        full_path = (self.es_path.parent / os_path).resolve()
        
        if not full_path.exists():
            self.errors.append(f"OS not found at: {full_path}")
        else:
            # Check that OS references this ES
            os_content = full_path.read_text()
            if 'evolution/SKILL.md' not in os_content and 'evolutionary/SKILL.md' not in os_content:
                self.warnings.append("OS doesn't appear to reference this ES")
    
    def _check_required_sections(self, content: str):
        """Check for required ES sections"""
        required_markers = [
            ('## Binding Information', 'binding section'),
            ('## Layer 1/Layer 2', 'layer boundary definition'),
        ]
        
        for marker, description in required_markers:
            if marker not in content:
                self.errors.append(f"Missing {description}")
    
    def _check_evolution_workflow(self, content: str):
        """Check for 5-phase evolution workflow"""
        phases = [
            'Phase 1: Context',
            'Phase 2: Generate',
            'Phase 3: Apply 1/8',
            'Phase 4: Apply Modifications',
            'Phase 5:',  # Either "Post-Modification" or "Validation"
        ]
        
        found_phases = 0
        for phase in phases:
            if phase in content:
                found_phases += 1
        
        if found_phases < 4:
            self.warnings.append(f"Evolution workflow incomplete (found {found_phases}/5 phases)")
    
    def _check_validation_method(self, content: str):
        """Check that a validation method is present"""
        validation_methods = [
            'python ../evolutionary/scripts/test_os.py',  # Python tests
            'Execute a mock run',  # Mock execution
            'Validation Checklist',  # Manual checks
        ]
        
        has_validation = any(method in content for method in validation_methods)
        
        if not has_validation:
            self.warnings.append("No validation method detected")
    
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
            print("\n✅ ES validation passed")
        elif not self.errors:
            print("\n✅ ES validation passed (with warnings)")


def main():
    parser = argparse.ArgumentParser(description="Validate Evolutionary Skill")
    parser.add_argument("--es-path", type=Path, required=True, help="Path to ES SKILL.md")
    
    args = parser.parse_args()
    
    validator = ESValidator(args.es_path)
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
