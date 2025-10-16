import os
import subprocess
from typing import List

class GitChangedFiles:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def get_changed_c_files(self) -> List[str]:
        """Get C files changed in the last commit"""
        try:
            result = subprocess.run([
                'git', 'diff', '--name-only', 'HEAD~1', 'HEAD'
            ], capture_output=True, text=True, check=True, cwd=self.repo_path)

            changed_files = []
            for file_path in result.stdout.strip().split('\n'):
                if file_path.endswith('.c') and os.path.exists(os.path.join(self.repo_path, file_path)):
                    changed_files.append(os.path.join(self.repo_path, file_path))

            return changed_files

        except (subprocess.CalledProcessError, FileNotFoundError):
            return []