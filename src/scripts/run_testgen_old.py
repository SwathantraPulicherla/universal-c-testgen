#!/usr/bin/env python3
"""
Universal C Test Generator - Main executable
Usage: c-testgen /path/to/repo
"""

import os
import sys
import argparse
from pathlib import Path

# Add package to path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from context_engine.dependency_analyzer import DependencyAnalyzer
from context_engine.prompt_builder import PromptBuilder
from generators.unity_generator import UnityTestGenerator

def main():
    parser = argparse.ArgumentParser(description='Universal AI-powered C unit test generator')
    parser.add_argument('repo_path', help='Path to C repository')
    parser.add_argument('--output', '-o', default='tests/generated', help='Output directory for generated tests')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')

    args = parser.parse_args()

    # Validate repository path
    if not os.path.exists(args.repo_path):
        print(f"❌ Error: Repository path '{args.repo_path}' does not exist")
        sys.exit(1)

    # Get API key
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: Gemini API key required. Set GEMINI_API_KEY environment variable or use --api-key")
        sys.exit(1)

    print(f"🔍 Analyzing repository: {args.repo_path}")

    # Initialize components
    analyzer = DependencyAnalyzer(args.repo_path)
    prompt_builder = PromptBuilder(args.repo_path)
    generator = UnityTestGenerator(api_key)

    # Find all C files to process
    c_files = analyzer.find_all_c_files()
    if not c_files:
        print("❌ No C files found in repository")
        sys.exit(1)

    print(f"📁 Found {len(c_files)} C files to analyze")

    # Analyze each file
    analyses = []
    for file_path in c_files:
        rel_path = os.path.relpath(file_path, args.repo_path)
        print(f"   Analyzing: {rel_path}")
        analysis = analyzer.analyze_file_dependencies(file_path)
        analyses.append(analysis)

    # Build comprehensive prompt
    print("📝 Building context-aware prompt...")
    prompt = prompt_builder.build_test_generation_prompt(analyses)

    # Generate tests
    print("🤖 Generating tests with Gemini 2.5 Pro...")
    result = generator.generate_tests(prompt, args.output)

    if result['success']:
        print(f"✅ SUCCESS: Tests generated at {result['test_file']}")
        print(f"📂 Output directory: {args.output}")

        # Show generated file preview
        try:
            with open(result['test_file'], 'r') as f:
                lines = f.readlines()[:10]
                print("\n📄 Generated test preview (first 10 lines):")
                for line in lines:
                    print(f"   {line.rstrip()}")
                if len(lines) >= 10:
                    print("   ...")
        except Exception as e:
            print(f"   Could not preview file: {e}")

    else:
        print(f"❌ FAILED: {result['error']}")
        sys.exit(1)

if __name__ == '__main__':
    main()