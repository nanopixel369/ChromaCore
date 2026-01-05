#!/usr/bin/env python3
"""
Context builder for skill-forge.
Prompts user for all variables needed by chosen composition blocks.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Set


# Variable requirements for each module
MODULE_VARIABLES = {
    # OS Modules
    'y': {
        'skill-description': 'Brief description of what the skill does',
        'author-name': 'Your name or organization',
        'created-date': 'Creation date (MMDDYYYY HHMM)',
    },
    'ep': {
        'skill-overview': 'High-level overview of the skill purpose',
        'core-concepts-explanation': 'Key concepts the skill relies on',
        'key-terminology': 'Important terms to understand (format: **Term:** definition)',
    },
    'iv': {
        'when-to-use-guidance': 'When should this skill be invoked?',
        'quality-standards': 'What defines success for this skill?',
        'use-cases': 'Bullet list of example scenarios',
        'input-requirements': 'What inputs does the skill need?',
        'prerequisites': 'Required tools, knowledge, or setup',
        'not-suitable-for': 'When NOT to use this skill',
    },
    'ws': {
        'step1-name': 'Name of first workflow step',
        'step1-description': 'What this step accomplishes',
        'step1-input': 'Input for step 1',
        'step1-output': 'Output from step 1',
        'step1-implementation': 'How to execute step 1',
        'step2-name': 'Name of second workflow step',
        'step2-description': 'What this step accomplishes',
        'step2-input': 'Input for step 2',
        'step2-output': 'Output from step 2',
        'step2-implementation': 'How to execute step 2',
        'step3-name': 'Name of third workflow step',
        'step3-description': 'What this step accomplishes',
        'step3-input': 'Input for step 3',
        'step3-output': 'Output from step 3',
        'step3-implementation': 'How to execute step 3',
        'param1-name': 'First tunable parameter name',
        'param1-default': 'Default value for param 1',
        'param2-name': 'Second tunable parameter name (optional)',
        'param2-default': 'Default value for param 2 (optional)',
        'param3-name': 'Third tunable parameter name (optional)',
        'param3-default': 'Default value for param 3 (optional)',
        'heuristics-description': 'Decision-making guidelines and edge cases',
    },
    'wc': {
        'path-count': 'Number of execution paths',
        'path1-name': 'First path name',
        'path1-trigger': 'When to use this path',
        'path1-steps': 'Steps for this path',
        'path2-name': 'Second path name (if path-count >= 2)',
        'path2-trigger': 'When to use path 2',
        'path2-steps': 'Steps for path 2',
    },
    'r': {
        'routing-logic': 'How to determine which path to take',
        'route1-trigger': 'Condition for route 1',
        'route1-destination': 'Where route 1 leads',
        'route2-trigger': 'Condition for route 2',
        'route2-destination': 'Where route 2 leads',
    },
    'cr': {
        'review-focus': 'What aspects to review (security, quality, etc)',
        'analysis-depth': 'How thorough should the review be',
    },
    'api': {
        'api-endpoint': 'Base API endpoint',
        'auth-method': 'Authentication approach',
        'request-format': 'Request structure/format',
        'response-handling': 'How to process responses',
    },
    'bp': {
        'practice-categories': 'Areas covered by best practices',
        'guidance-format': 'How guidance is structured',
    },
    'esc': {
        'evolution-check-description': 'How to verify evolution is available',
    },
    'sc': {
        'criterion1': 'First success criterion',
        'criterion2': 'Second success criterion',
        'criterion3': 'Third success criterion (optional)',
        'quality-metric1': 'First measurable metric',
        'expected-value1': 'Expected value for metric 1',
        'quality-metric2': 'Second measurable metric (optional)',
        'expected-value2': 'Expected value for metric 2 (optional)',
        'failure-condition1': 'First failure scenario',
        'failure-condition2': 'Second failure scenario (optional)',
    },
    
    # ES Modules
    'b': {
        'os-skill-name': 'Name of the operational skill',
        'os-path': 'Relative path to OS SKILL.md (usually ../operational/SKILL.md)',
    },
    'lb': {
        'l1-boundary-map': 'Map of L1 tags (usually auto-generated)',
    },
    'ep-es': {
        'eval-description': 'What evaluation measures',
        'eval-metrics': 'Specific metrics tracked',
    },
    'ew': {
        'evolution-strategy': 'How evolution candidates are selected',
        'selection-ratio': 'Ratio for selecting improvements (e.g., top 1/8)',
    },
    'vp': {
        'test-suite-description': 'What tests validate',
        'test-coverage': 'Areas covered by tests',
    },
    'vm': {
        'mock-scenarios': 'Scenarios for mock execution',
    },
    'vman': {
        'checklist-items': 'Manual validation checklist',
    },
}


# Presets that combine blocks
PRESETS = {
    'os': {
        'minimal': 'y-ws-esc',
        'standard': 'y-ep-iv-ws-esc-sc',
        'router': 'y-ep-iv-r-sc',
        'code-review': 'y-ep-iv-cr-esc-sc',
        'api-integration': 'y-ep-iv-api-esc-sc',
        'best-practices': 'y-ep-iv-bp-esc-sc',
    },
    'es': {
        'dev-agent': 'y-b-lb-ep-ew-vp',
        'webapp': 'y-b-lb-ee-ew-vm',
        'flexible': 'y-b-lb-ef-ew-vp',
        'manual': 'y-b-lb-ee-ew-vman',
    },
}


def get_required_variables(composition: str) -> Dict[str, str]:
    """Extract all required variables for a composition."""
    blocks = composition.split('-')
    variables = {}
    
    for block in blocks:
        if block in MODULE_VARIABLES:
            variables.update(MODULE_VARIABLES[block])
    
    # Add common variables always needed
    variables.update({
        'skill-name': 'Auto-generated from directory name',
        'timestamp': 'Auto-generated timestamp',
        'version': 'Auto-generated version',
        'current-timestamp': 'Auto-generated current timestamp',
    })
    
    return variables


def prompt_for_variable(name: str, description: str, existing_value: str = None) -> str:
    """Prompt user for a variable value."""
    if existing_value:
        print(f"\n{name}: {description}")
        print(f"  Current: {existing_value}")
        response = input("  New value (press Enter to keep current): ").strip()
        return response if response else existing_value
    else:
        print(f"\n{name}: {description}")
        return input("  Value: ").strip()


def build_context_interactive(composition: str, existing_context: Dict = None) -> Dict[str, str]:
    """Build context interactively by prompting for each variable."""
    if existing_context is None:
        existing_context = {}
    
    required = get_required_variables(composition)
    context = {}
    
    print(f"\n=== Building Context for Composition: {composition} ===")
    print(f"Required variables: {len(required)}")
    print("\nEnter values for each variable (auto-generated ones will be filled automatically):\n")
    
    for var_name, description in required.items():
        if var_name in ['skill-name', 'timestamp', 'version', 'current-timestamp']:
            # Auto-generated
            continue
        
        existing = existing_context.get(var_name)
        value = prompt_for_variable(var_name, description, existing)
        
        if value:
            context[var_name] = value
    
    return context


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build skill context interactively')
    parser.add_argument('--composition', '-c', help='Block composition (e.g., y-ep-iv-ws-esc-sc)')
    parser.add_argument('--preset', '-p', help='Use preset (e.g., os:standard, es:dev-agent)')
    parser.add_argument('--existing', '-e', help='Path to existing context JSON to update')
    parser.add_argument('--output', '-o', help='Output path for context JSON (required unless --list-vars)')
    parser.add_argument('--list-vars', action='store_true', help='List variables without prompting')
    
    args = parser.parse_args()
    
    # Determine composition
    composition = args.composition
    if args.preset:
        preset_type, preset_name = args.preset.split(':')
        if preset_type not in PRESETS or preset_name not in PRESETS[preset_type]:
            print(f"Error: Unknown preset {args.preset}")
            print(f"Available presets:")
            for ptype, presets in PRESETS.items():
                for pname in presets:
                    print(f"  {ptype}:{pname} → {presets[pname]}")
            sys.exit(1)
        composition = PRESETS[preset_type][preset_name]
        print(f"Using preset {args.preset} → {composition}")
    
    if not composition:
        print("Error: Must specify --composition or --preset")
        sys.exit(1)
    
    # List variables mode
    if args.list_vars:
        required = get_required_variables(composition)
        print(f"\nRequired variables for {composition}:")
        for name, desc in required.items():
            print(f"  {name}: {desc}")
        sys.exit(0)
    
    # Require output for interactive mode
    if not args.output:
        print("Error: --output is required for interactive mode")
        sys.exit(1)
    
    # Load existing context if provided
    existing = {}
    if args.existing:
        existing_path = Path(args.existing)
        if existing_path.exists():
            existing = json.loads(existing_path.read_text())
            print(f"Loaded existing context from {args.existing}")
    
    # Build context
    context = build_context_interactive(composition, existing)
    
    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(context, indent=2))
    
    print(f"\n✓ Context saved to {args.output}")
    print(f"  Variables: {len(context)}")


if __name__ == '__main__':
    main()
