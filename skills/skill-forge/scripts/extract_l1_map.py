#!/usr/bin/env python3
"""
Extracts Layer 1 boundary map from an Operational Skill.

Parses <L1></L1> tags and generates a map showing:
- Line ranges for each L1 section
- Description of what's protected
- Total L1 content percentage

Used by skill-forge to generate l1-boundary-map for ES.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

class L1Extractor:
    def __init__(self, os_path: Path):
        self.os_path = os_path
        self.sections = []
        
    def extract(self) -> str:
        """Extract L1 boundary map"""
        if not self.os_path.exists():
            print(f"Error: OS file not found: {self.os_path}", file=sys.stderr)
            sys.exit(1)
        
        content = self.os_path.read_text()
        lines = content.split('\n')
        
        # Find all L1 sections
        in_l1 = False
        l1_start = 0
        
        for i, line in enumerate(lines, 1):
            if '<L1>' in line:
                in_l1 = True
                l1_start = i
            elif '</L1>' in line and in_l1:
                description = self._extract_description(lines, l1_start, i)
                self.sections.append((l1_start, i, description))
                in_l1 = False
        
        # Generate map
        return self._format_map(len(lines))
    
    def _extract_description(self, lines: List[str], start: int, end: int) -> str:
        """Extract description from section content"""
        # Look for headers in the L1 section
        for line in lines[start:end]:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Extract header text
                return stripped.lstrip('#').strip()
        
        # No header found, generate generic description
        return "Core workflow section"
    
    def _format_map(self, total_lines: int) -> str:
        """Format the boundary map for ES"""
        if not self.sections:
            return "[No L1 sections detected - skill may need L1 tags added]"
        
        map_lines = []
        total_l1_lines = 0
        
        for start, end, desc in self.sections:
            section_lines = end - start + 1
            total_l1_lines += section_lines
            map_lines.append(f"- SKILL.md lines {start}-{end}: {desc}")
        
        # Add summary
        l1_percentage = (total_l1_lines / total_lines) * 100
        
        result = "\n".join(map_lines)
        result += f"\n\n**L1 Coverage:** {total_l1_lines}/{total_lines} lines ({l1_percentage:.1f}%)"
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Extract L1 boundary map from OS")
    parser.add_argument("--os-path", type=Path, required=True, help="Path to OS SKILL.md")
    parser.add_argument("--output", type=Path, help="Output file (default: print to stdout)")
    
    args = parser.parse_args()
    
    extractor = L1Extractor(args.os_path)
    boundary_map = extractor.extract()
    
    if args.output:
        args.output.write_text(boundary_map)
        print(f"✓ L1 boundary map written to: {args.output}")
    else:
        print(boundary_map)


if __name__ == "__main__":
    main()
