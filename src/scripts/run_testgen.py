#!/usr/bin/env python3

"""
Universal C Test Generator - SMART File-by-File Processing
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set
import google.generativeai as genai

# Add package to path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from context_engine.dependency_analyzer import DependencyAnalyzer


class SmartTestGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.dependency_map = {}  # Maps functions to their source files

    def build_dependency_map(self, repo_path: str) -> Dict[str, str]:
        """Build a map of function_name -> source_file for the entire repository"""
        print("� Building global dependency map...")
        analyzer = DependencyAnalyzer(repo_path)
        all_c_files = analyzer.find_all_c_files()

        dependency_map = {}

        for file_path in all_c_files:
            functions = analyzer._extract_functions(file_path)
            for func in functions:
                dependency_map[func['name']] = file_path

        print(f"   Mapped {len(dependency_map)} functions across {len(all_c_files)} files")
        return dependency_map

    def generate_tests_for_file(self, file_path: str, repo_path: str, output_dir: str, dependency_map: Dict[str, str]) -> Dict:
        """Generate tests for a SINGLE file with proper context"""
        analyzer = DependencyAnalyzer(repo_path)

        # Analyze this specific file
        analysis = analyzer.analyze_file_dependencies(file_path)

        # IDENTIFY FUNCTIONS THAT NEED STUBS
        functions_that_need_stubs = []
        implemented_functions = {f['name'] for f in analysis['functions']}

        for called_func in analysis['called_functions']:
            # If called function is not in current file AND not a standard library function
            if (called_func not in implemented_functions and
                called_func in dependency_map and
                dependency_map[called_func] != file_path):
                functions_that_need_stubs.append(called_func)

        print(f"   📋 {os.path.basename(file_path)}: {len(analysis['functions'])} functions, {len(functions_that_need_stubs)} need stubs")

        # Build targeted prompt for this file only
        prompt = self._build_targeted_prompt(analysis, functions_that_need_stubs, repo_path)

        # Generate tests
        try:
            response = self.model.generate_content(prompt)
            test_code = response.text.strip()

            # Save test file
            test_filename = f"test_{os.path.basename(file_path)}"
            output_path = os.path.join(output_dir, test_filename)

            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(test_code)

            return {'success': True, 'test_file': output_path}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _build_targeted_prompt(self, analysis: Dict, functions_that_need_stubs: List[str], repo_path: str) -> str:
        """Build a focused prompt for a single file with stub requirements"""

        file_content = self._read_file_safely(analysis['file_path'])
        rel_path = os.path.relpath(analysis['file_path'], repo_path)

        prompt = f"""
Generate Unity tests for this C file: {rel_path}

SOURCE CODE TO TEST:
```c
{file_content}
```

FUNCTIONS TO TEST:
{chr(10).join(f"- {func['return_type']} {func['name']}" for func in analysis['functions'])}

FUNCTIONS THAT NEED STUBS (implement these as stub functions):
{chr(10).join(f"- {func_name}" for func_name in functions_that_need_stubs) or "- None"}

INSTRUCTIONS:

Create a complete Unity test file named test_{os.path.basename(analysis['file_path'])}

Generate stub functions for ALL listed functions that need stubs

Stubs should track call counts and allow configuring return values

Test normal cases, edge cases, and error conditions

Use TEST_ASSERT_* macros appropriately

Include setUp() and tearDown() if needed

Generate ONLY the complete C test file code. No explanations.
"""
        return prompt

    def _read_file_safely(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception:
            return "// Unable to read file"


def main():
    parser = argparse.ArgumentParser(description='Smart AI-powered C unit test generator')
    parser.add_argument('repo_path', help='Path to C repository')
    parser.add_argument('--output', '-o', default='tests/generated', help='Output directory (relative to repo if not absolute)')
    parser.add_argument('--api-key', help='Gemini API key')

    args = parser.parse_args()

    # Make output directory relative to repo_path if not absolute
    if not os.path.isabs(args.output):
        args.output = os.path.join(args.repo_path, args.output)

    # Validate inputs
    if not os.path.exists(args.repo_path):
        print(f"❌ Repository path '{args.repo_path}' does not exist")
        sys.exit(1)

    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    print(f"🚀 Starting SMART test generation for: {args.repo_path}")

    # Initialize generator
    generator = SmartTestGenerator(api_key)

    # Build global function dependency map
    dependency_map = generator.build_dependency_map(args.repo_path)

    # Find all C files
    analyzer = DependencyAnalyzer(args.repo_path)
    c_files = analyzer.find_all_c_files()

    if not c_files:
        print("❌ No C files found")
        sys.exit(1)

    print(f"� Processing {len(c_files)} files...")

    # Process each file individually
    successful_generations = 0
    for file_path in c_files:
        rel_path = os.path.relpath(file_path, args.repo_path)
        print(f"   🎯 Generating tests for: {rel_path}")

        result = generator.generate_tests_for_file(
            file_path, args.repo_path, args.output, dependency_map
        )

        if result['success']:
            print(f"      ✅ Generated: {os.path.basename(result['test_file'])}")
            successful_generations += 1
        else:
            print(f"      ❌ Failed: {result['error']}")

    print(f"\n🎉 COMPLETED: {successful_generations}/{len(c_files)} files successfully generated")
    print(f"� Test files saved to: {args.output}")


if __name__ == '__main__':
    main()
