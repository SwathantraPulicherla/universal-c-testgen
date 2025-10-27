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
import re

# Add package to path
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))

from context_engine.dependency_analyzer import DependencyAnalyzer


class SmartTestGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
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

            # POST-PROCESSING: Clean up common AI generation issues
            test_code = self._post_process_test_code(test_code, analysis, analysis['includes'])

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

CRITICAL REQUIREMENTS - FOLLOW THESE EXACTLY TO AVOID COMPILATION ERRORS:

1. OUTPUT FORMAT:
   - Generate ONLY clean C code with NO markdown markers (```c, ```)
   - NO explanations, comments about generation, or extra text
   - Start directly with #include statements

2. COMPILATION SAFETY:
   - Include ONLY "unity.h" and existing header files from the source
   - DO NOT include non-existent headers (like "main.h" if no main.h exists)
   - Function signatures must EXACTLY match the source code
   - NO calls to main() or other functions that don't exist in testable form

3. FLOATING POINT HANDLING:
   - ALWAYS use TEST_ASSERT_FLOAT_WITHIN(tolerance, expected, actual)
   - NEVER use TEST_ASSERT_EQUAL_FLOAT (causes precision failures)
   - Use tolerance 0.01f for temperature comparisons

4. STUB IMPLEMENTATION:
   - Implement stubs for ALL listed functions that need stubs
   - Stubs must have EXACT same signature as source functions
   - Use static variables for call counts and return values
   - Reset ALL stub state in setUp() function

5. TEST DESIGN:
   - Test functions individually, not main() or complex workflows
   - Use realistic values within sensor operational ranges
   - Include setUp() and tearDown() for proper isolation
   - Each test should be independent and focused

6. UNITY FRAMEWORK USAGE:
   - Use TEST_ASSERT_* macros correctly
   - TEST_ASSERT_TRUE/TEST_ASSERT_FALSE for boolean results
   - TEST_ASSERT_EQUAL for integers
   - TEST_ASSERT_FLOAT_WITHIN for floating point
   - TEST_ASSERT_EQUAL_STRING for string comparisons

VALIDATION REQUIREMENTS - FOLLOW THESE CRITERIA:

1. COMPILATION SAFETY:
   - Include ALL necessary headers (#include "unity.h", source headers)
   - Ensure stub function signatures EXACTLY match source function signatures
   - No duplicate symbol definitions
   - Proper Unity test framework usage

2. REALITY CHECKS:
   - Use realistic test values within operational ranges
   - Avoid impossible scenarios (temperatures below absolute zero, etc.)
   - Stubs must match actual function return types and parameters
   - Use appropriate tolerance for floating-point comparisons (TEST_ASSERT_FLOAT_WITHIN)

3. TEST QUALITY:
   - Cover edge cases (min/max values, zero, boundaries)
   - Test error conditions where applicable
   - Reset stubs properly in setUp()/tearDown() functions
   - Each test should verify meaningful behavior
   - Avoid redundant or trivial test cases

4. LOGICAL CONSISTENCY:
   - Test names should match their actual content
   - No contradictory assertions within tests
   - Use reasonable threshold values for comparisons
   - Proper use of TEST_ASSERT_* macros
   - tearDown() must reset ALL stub state variables to ensure test isolation

INSTRUCTIONS:

Create a complete Unity test file named test_{os.path.basename(analysis['file_path'])}

Generate stub functions for ALL listed functions that need stubs
Stubs should track call counts and allow configuring return values

Test normal cases, edge cases, and error conditions
Use TEST_ASSERT_* macros appropriately
Include setUp() and tearDown() functions for proper test isolation
CRITICAL: tearDown() must reset ALL stub variables (call counts and return values) to 0/default values

Generate ONLY the complete C test file code. No explanations.
"""
        return prompt

    def _read_file_safely(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception:
            return "// Unable to read file"

    def _post_process_test_code(self, test_code: str, analysis: Dict, source_includes: List[str]) -> str:
        """Post-process generated test code to fix common issues"""

        # Remove markdown code block markers
        test_code = re.sub(r'^```c?\s*', '', test_code, flags=re.MULTILINE)
        test_code = re.sub(r'```\s*$', '', test_code, flags=re.MULTILINE)

        # Fix floating point assertions - replace TEST_ASSERT_EQUAL_FLOAT with TEST_ASSERT_FLOAT_WITHIN
        test_code = re.sub(
            r'TEST_ASSERT_EQUAL_FLOAT\s*\(\s*([^,]+)\s*,\s*([^)]+)\s*\)',
            r'TEST_ASSERT_FLOAT_WITHIN(0.01f, \1, \2)',
            test_code
        )

        # Remove invalid function calls (like main())
        test_code = re.sub(r'\bmain\s*\(\s*\)\s*;', '', test_code)
        # Remove any main function definitions that might appear
        test_code = re.sub(r'int\s+main\s*\([^)]*\)\s*{[^}]*}', '', test_code, flags=re.DOTALL)

        # Remove printf/scanf statements that might appear in tests
        test_code = re.sub(r'printf\s*\([^;]*\);\s*', '', test_code)
        test_code = re.sub(r'scanf\s*\([^;]*\);\s*', '', test_code)

        # Remove any standalone function declarations that aren't part of the test
        # Keep only what's needed for the test file

        # Ensure proper includes - only include unity.h and existing source headers
        lines = test_code.split('\n')
        cleaned_lines = []

        for line in lines:
            # Keep unity.h include
            if '#include "unity.h"' in line:
                cleaned_lines.append(line)
                continue

            # Only keep includes for headers that actually exist in source
            if line.startswith('#include'):
                include_match = re.match(r'#include\s+["<]([^">]+)[">]', line)
                if include_match:
                    header_name = include_match.group(1)
                    # Only include headers that exist in source_includes or are standard headers
                    if header_name in source_includes or header_name.endswith('.h'):
                        # Additional check: don't include main.h if it doesn't exist
                        if header_name == 'main.h' and not any('main.h' in inc for inc in source_includes):
                            continue
                        cleaned_lines.append(line)
                # Skip non-matching include lines
                continue

            # Keep all other lines
            cleaned_lines.append(line)

        # Ensure unity.h is included if not present
        has_unity = any('#include "unity.h"' in line for line in cleaned_lines)
        if not has_unity:
            cleaned_lines.insert(0, '#include "unity.h"')

        return '\n'.join(cleaned_lines)


class TestValidator:
    """Universal C Test File Validator - Repo Independent"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.analyzer = DependencyAnalyzer(repo_path)

    def validate_test_file(self, test_file_path: str, source_file_path: str) -> Dict:
        """
        Validate a generated test file against its source file using comprehensive criteria
        """
        validation_result = {
            'file': os.path.basename(test_file_path),
            'compiles': True,
            'realistic': True,
            'quality': 'High',
            'issues': [],
            'keep': [],
            'fix': [],
            'remove': []
        }

        try:
            # Read both files
            with open(test_file_path, 'r') as f:
                test_content = f.read()
            with open(source_file_path, 'r') as f:
                source_content = f.read()

            # Extract source function signatures
            source_functions = self.analyzer._extract_functions(source_file_path)
            source_includes = self.analyzer._extract_includes(source_file_path)

            # 1. COMPILATION SAFETY CHECKS
            self._check_compilation_safety(test_content, source_functions, source_includes, validation_result)

            # 2. REALITY CHECKS
            self._check_reality_tests(test_content, source_functions, validation_result)

            # 3. TEST QUALITY ASSESSMENT
            self._assess_test_quality(test_content, source_functions, validation_result)

            # 4. LOGICAL CONSISTENCY VERIFICATION
            self._verify_logical_consistency(test_content, validation_result)

            # Determine overall quality rating
            validation_result['quality'] = self._calculate_quality_rating(validation_result)

        except Exception as e:
            validation_result['issues'].append(f"Validation error: {str(e)}")
            validation_result['compiles'] = False
            validation_result['quality'] = 'Low'

        return validation_result

    def _check_compilation_safety(self, test_content: str, source_functions: List[Dict], source_includes: List[str], result: Dict):
        """Check compilation safety criteria"""

        # Check for markdown markers (should be removed by post-processing)
        if '```' in test_content:
            result['issues'].append("Found markdown code block markers (```) - should be removed")
            result['compiles'] = False

        # Check for required includes
        required_includes = ['unity.h'] + [f"{func['name']}.h" for func in source_functions if func['name'] != 'main']
        for include in required_includes:
            if f'#include "{include}"' not in test_content and f'#include <{include}>' not in test_content:
                if include == 'unity.h':
                    result['issues'].append(f"Missing required Unity include: #include \"unity.h\"")
                    result['compiles'] = False

        # Check for invalid includes (headers that don't exist)
        invalid_includes = []
        include_pattern = re.compile(r'#include\s+["<]([^">]+)[">]')
        for match in include_pattern.finditer(test_content):
            header = match.group(1)
            if header not in source_includes and header != 'unity.h' and not header.startswith('std'):
                # Check if it's a valid header file that should exist
                if not any(header in inc for inc in source_includes):
                    invalid_includes.append(header)

        if invalid_includes:
            result['issues'].append(f"Invalid includes for non-existent headers: {invalid_includes}")
            result['compiles'] = False

        # Check function signature matches
        test_functions = self._extract_test_functions(test_content)
        for test_func in test_functions:
            if 'test_' in test_func['name']:
                # Check if stub functions match source signatures
                stub_matches = re.findall(r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{', test_content)
                for return_type, func_name in stub_matches:
                    # Find matching source function
                    source_match = next((f for f in source_functions if f['name'] == func_name), None)
                    if source_match and source_match['return_type'] != return_type:
                        result['issues'].append(f"Stub function {func_name} return type mismatch: {return_type} vs {source_match['return_type']}")
                        result['compiles'] = False

        # Check for duplicate symbols
        function_names = [f['name'] for f in test_functions]
        if len(function_names) != len(set(function_names)):
            duplicates = [name for name in function_names if function_names.count(name) > 1]
            result['issues'].append(f"Duplicate function definitions: {duplicates}")
            result['compiles'] = False

        # Check for invalid function calls (like main())
        if re.search(r'\bmain\s*\(', test_content):
            result['issues'].append("Invalid call to main() function - not suitable for unit testing")
            result['compiles'] = False

    def _check_reality_tests(self, test_content: str, source_functions: List[Dict], result: Dict):
        """Validate reality checks"""

        # Check for invalid floating point assertions
        if 'TEST_ASSERT_EQUAL_FLOAT' in test_content:
            result['issues'].append("TEST_ASSERT_EQUAL_FLOAT used - will fail due to precision. Use TEST_ASSERT_FLOAT_WITHIN instead")
            result['realistic'] = False

        # Check for impossible test values
        impossible_patterns = [
            (r'-?273\.15f?', 'Absolute zero temperature test - physically impossible'),
            (r'1e10+', 'Extremely large values that may cause overflow'),
            (r'NULL.*=.*[^=!].*NULL', 'Testing NULL assignments that may crash'),
        ]

        lines = test_content.split('\n')
        for i, line in enumerate(lines, 1):
            for pattern, description in impossible_patterns:
                if re.search(pattern, line):
                    result['issues'].append(f"Line {i}: {description} - unrealistic test scenario")
                    result['realistic'] = False

        # Check floating point comparisons have tolerance
        float_assertions = re.findall(r'TEST_ASSERT_FLOAT_WITHIN\s*\([^)]+\)', test_content)
        if not float_assertions and ('float' in test_content.lower() or '.0f' in test_content):
            result['issues'].append("Floating-point values present but no TEST_ASSERT_FLOAT_WITHIN found")
            result['realistic'] = False

        # Check stub return types match expected ranges
        if 'temperature' in test_content.lower() or 'celsius' in test_content.lower():
            # Temperature should be reasonable range for the specific sensor
            temp_values = re.findall(r'(\d+\.?\d*)f?', test_content)
            for val in temp_values:
                try:
                    temp = float(val)
                    # Context-aware validation: check if this looks like a raw ADC value or temperature
                    # Raw ADC values are typically 0-1023, temperatures are usually < 200°C
                    if temp > 200.0 and temp <= 1024.0:
                        # This might be a raw ADC value, not a temperature - check context
                        if 'raw' in test_content.lower() or 'adc' in test_content.lower() or '1023' in test_content:
                            continue  # Likely a raw ADC value, skip validation
                        else:
                            result['issues'].append(f"Temperature value {temp} seems unreasonably high")
                            result['realistic'] = False
                    elif temp > 1024.0:  # Definitely too high
                        result['issues'].append(f"Temperature value {temp} seems unreasonably high")
                        result['realistic'] = False
                    elif temp < -100.0:  # Definitely too low
                        result['issues'].append(f"Temperature value {temp} seems unreasonably low")
                        result['realistic'] = False
                except ValueError:
                    pass

    def _assess_test_quality(self, test_content: str, source_functions: List[Dict], result: Dict):
        """Assess test quality criteria"""

        test_functions = self._extract_test_functions(test_content)
        test_names = [f['name'] for f in test_functions if f['name'].startswith('test_')]

        # Check for edge cases
        edge_case_indicators = ['min', 'max', 'zero', 'negative', 'boundary', 'edge', 'limit']
        has_edge_cases = any(any(indicator in name.lower() for indicator in edge_case_indicators) for name in test_names)

        if not has_edge_cases and len(test_names) > 1:
            result['issues'].append("Missing edge case tests (min/max values, boundaries)")

        # Check for error conditions
        error_indicators = ['error', 'fail', 'invalid', 'null', 'boundary']
        has_error_tests = any(any(indicator in name.lower() for indicator in error_indicators) for name in test_names)

        # Check setUp/tearDown usage
        has_setup = 'setUp(' in test_content
        has_teardown = 'tearDown(' in test_content

        if has_setup and has_teardown:
            # Verify stubs are reset - check for either reset functions or direct variable resets
            has_reset_functions = 'reset_' in test_content
            # Check for direct variable resets in tearDown (e.g., var_name = 0)
            teardown_section = re.search(r'void tearDown\(void\)\s*{([^}]*)}', test_content, re.DOTALL)
            has_direct_resets = False
            if teardown_section:
                teardown_content = teardown_section.group(1)
                # Look for variable assignments to 0, 0.0f, NULL, etc.
                has_direct_resets = bool(re.search(r'\w+\s*=\s*(0|0\.0f|NULL|false);', teardown_content))

            if not (has_reset_functions or has_direct_resets):
                result['issues'].append("setUp/tearDown present but stub reset functions not called")
        elif len(test_names) > 3:  # Multiple tests without setup/teardown
            result['issues'].append("Multiple tests without setUp/tearDown functions")

        # Check for meaningful assertions
        assertion_count = len(re.findall(r'TEST_ASSERT_\w+', test_content))
        if assertion_count < len(test_names):
            result['issues'].append("Some tests lack assertions")

        # Check for redundant tests
        if len(test_names) > 5 and len(set([name.split('_')[-1] for name in test_names])) < 3:
            result['issues'].append("Too many similar test cases - consider consolidating")

    def _verify_logical_consistency(self, test_content: str, result: Dict):
        """Verify logical consistency"""

        # Check test descriptions match content
        test_pattern = r'void\s+(test_\w+)\s*\([^)]*\)\s*\{([^}]*)\}'
        matches = re.findall(test_pattern, test_content, re.DOTALL)

        for test_name, test_body in matches:
            # Check for contradictory assertions
            assertions = re.findall(r'TEST_ASSERT_\w+\s*\([^)]+\)', test_body)
            if len(assertions) > 1:
                # Look for contradictory patterns
                if 'TEST_ASSERT_EQUAL_INT(0,' in test_body and 'TEST_ASSERT_EQUAL_INT(1,' in test_body:
                    result['issues'].append(f"{test_name}: Contradictory assertions in same test")

            # Check reasonable threshold values
            threshold_values = re.findall(r'TEST_ASSERT_\w+\s*\(\s*([^,]+)\s*,', test_body)
            for threshold in threshold_values:
                if threshold.strip() in ['INT_MAX', 'INT_MIN', 'FLT_MAX', 'FLT_MIN']:
                    result['issues'].append(f"{test_name}: Using extreme threshold values")

        # Check proper TEST_ASSERT_* usage
        invalid_assertions = re.findall(r'TEST_ASSERT_[^(]*\([^)]*\)', test_content)
        for assertion in invalid_assertions:
            if not assertion.startswith('TEST_ASSERT_'):
                result['issues'].append(f"Invalid assertion format: {assertion}")

    def _extract_test_functions(self, content: str) -> List[Dict]:
        """Extract test function signatures from test file"""
        functions = []
        pattern = r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
        matches = re.findall(pattern, content)

        for return_type, func_name in matches:
            functions.append({
                'name': func_name,
                'return_type': return_type
            })

        return functions

    def _calculate_quality_rating(self, result: Dict) -> str:
        """Calculate overall quality rating"""
        issue_count = len(result['issues'])
        compiles = result['compiles']
        realistic = result['realistic']

        if not compiles:
            return 'Low'
        elif issue_count == 0 and realistic:
            return 'High'
        elif issue_count <= 2:
            return 'Medium'
        else:
            return 'Low'

    def print_validation_report(self, validation_result: Dict):
        """Print validation report in specified format"""
        print(f"\nFILE: {validation_result['file']}")
        print(f"✅ COMPILES: {'Yes' if validation_result['compiles'] else 'No'}")
        print(f"✅ REALISTIC: {'Yes' if validation_result['realistic'] else 'No'}")
        print(f"✅ QUALITY: {validation_result['quality']}")

        if validation_result['issues']:
            print("\nISSUES:")
            for issue in validation_result['issues']:
                print(f"- {issue}")

        # Categorize tests
        if validation_result['issues']:
            print("\nKEEP: [All tests - review issues manually]")
            print("FIX: [Tests with compilation issues]")
            print("REMOVE: [Tests with impossible scenarios]")
        else:
            print("\nKEEP: [All tests]")
            print("FIX: []")
            print("REMOVE: []")


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

    # Initialize validator
    validator = TestValidator(args.repo_path)

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
    validation_reports = []

    for file_path in c_files:
        rel_path = os.path.relpath(file_path, args.repo_path)
        print(f"   🎯 Generating tests for: {rel_path}")

        result = generator.generate_tests_for_file(
            file_path, args.repo_path, args.output, dependency_map
        )

        if result['success']:
            print(f"      ✅ Generated: {os.path.basename(result['test_file'])}")
            successful_generations += 1

            # Validate the generated test file
            print(f"      🔍 Validating: {os.path.basename(result['test_file'])}")
            validation_result = validator.validate_test_file(result['test_file'], file_path)
            validation_reports.append(validation_result)

            # Print validation summary
            status = "✅" if validation_result['compiles'] and validation_result['realistic'] else "⚠️"
            print(f"         {status} {validation_result['quality']} quality ({'Compiles' if validation_result['compiles'] else 'Broken'}, {'Realistic' if validation_result['realistic'] else 'Unrealistic'})")

        else:
            print(f"      ❌ Failed: {result['error']}")

    # Print detailed validation reports
    if validation_reports:
        print(f"\n{'='*60}")
        print("VALIDATION REPORTS")
        print(f"{'='*60}")

        for report in validation_reports:
            validator.print_validation_report(report)

    print(f"\n🎉 COMPLETED: {successful_generations}/{len(c_files)} files successfully generated")
    print(f"� Test files saved to: {args.output}")


if __name__ == '__main__':
    main()
