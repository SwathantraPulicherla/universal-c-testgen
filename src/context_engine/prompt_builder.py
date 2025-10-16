import os
from typing import List, Dict

class PromptBuilder:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def build_test_generation_prompt(self, analysis_results: List[Dict]) -> str:
        """Build comprehensive prompt for Gemini 2.5 Pro"""

        prompt_parts = []

        # Repository overview
        prompt_parts.append(self._build_repository_context())

        # Detailed file analyses
        for analysis in analysis_results:
            prompt_parts.append(self._build_file_analysis_section(analysis))

        # Test generation instructions
        prompt_parts.append(self._build_test_requirements())

        return "\n\n" + "="*80 + "\n\n".join(prompt_parts) + "\n" + "="*80

    def _build_repository_context(self) -> str:
        """Build repository structure overview"""
        c_files = []
        h_files = []

        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.c'):
                    c_files.append(os.path.relpath(os.path.join(root, file), self.repo_path))
                elif file.endswith('.h'):
                    h_files.append(os.path.relpath(os.path.join(root, file), self.repo_path))

        return f"""REPOSITORY CONTEXT:
This is a C project with the following structure:

SOURCE FILES ({len(c_files)}):
{chr(10).join(f'  - {f}' for f in sorted(c_files))}

HEADER FILES ({len(h_files)}):
{chr(10).join(f'  - {f}' for f in sorted(h_files))}"""

    def _build_file_analysis_section(self, analysis: Dict) -> str:
        """Build detailed analysis for a single file"""
        file_content = self._read_file_safely(analysis['file_path'])
        rel_path = os.path.relpath(analysis['file_path'], self.repo_path)

        section = f"""
FILE ANALYSIS: {rel_path}
{'-' * (len(rel_path) + 18)}

FUNCTIONS TO TEST ({len(analysis['functions'])}):
{chr(10).join(f'  - {func["return_type"]} {func["name"]}(...)' for func in analysis['functions'])}

DEPENDENCIES:
  Includes: {', '.join(analysis['includes']) or 'None'}
  Called Functions: {', '.join(sorted(analysis['called_functions'])) or 'None'}
  File Dependencies: {', '.join([os.path.relpath(f, self.repo_path) for f in analysis['file_dependencies']]) or 'None'}

SOURCE CODE:
```c
{file_content}
```"""
        return section

    def _build_test_requirements(self) -> str:
        return """TEST GENERATION INSTRUCTIONS:

Generate COMPLETE Unity test files for ALL functions listed above.

CRITICAL REQUIREMENTS:
1. Create ONE test file per source file named: test_<original_filename>.c
2. Generate appropriate stubs for ALL external function dependencies
3. Include ALL necessary Unity framework headers and setup
4. Test normal cases, edge cases, boundary values, and error conditions
5. Create setUp() and tearDown() functions where needed
6. Use proper TEST_ASSERT_* macros for comprehensive testing
7. Include a test runner function for each test suite

STUB GENERATION RULES:
- Create stub functions for ALL called functions that aren't in the current file
- Stubs should track call counts, parameters, and return configurable values
- Use meaningful default return values based on function return types

OUTPUT FORMAT:
Generate COMPLETE, COMPILABLE C files. Include:
1. All necessary #include directives
2. Stub function implementations
3. Test case functions with descriptive names
4. setUp() and tearDown() if needed
5. test runner function

Generate ONLY the complete C code. No explanations, no markdown, just ready-to-compile test files."""

    def _read_file_safely(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"// Unable to read file: {e}"