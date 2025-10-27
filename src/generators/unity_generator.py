import os
import google.generativeai as genai
from typing import Dict, List
import re

class UnityTestGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_tests(self, prompt: str, output_dir: str) -> Dict[str, str]:
        """Generate tests using Gemini 2.5 Pro free tier"""
        try:
            print("🚀 Sending request to Gemini 2.5 Pro...")
            response = self.model.generate_content(prompt)
            test_code = response.text.strip()

            # Extract or generate filename
            test_filename = self._extract_test_filename(prompt, test_code)
            output_path = os.path.join(output_dir, test_filename)

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Write the generated test file
            with open(output_path, 'w') as f:
                f.write(test_code)

            return {
                'success': True,
                'test_file': output_path,
                'test_code': test_code
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_test_filename(self, prompt: str, test_code: str) -> str:
        """Extract filename from context or generate default"""
        # Try to find source filename in prompt
        source_match = re.search(r'FILE ANALYSIS:\s*([^\s\n]+\.c)', prompt)
        if source_match:
            source_file = os.path.basename(source_match.group(1))
            return f"test_{source_file}"

        # Default name if extraction fails
        return "test_generated.c"