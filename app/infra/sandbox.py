"""
Sandbox runner for generated Python code.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class SandboxRunner:
    """Runs generated Python code in a restricted subprocess."""

    def __init__(self, allowed_dir: str | None = None, timeout: int = 30):
        self.allowed_dir = allowed_dir or tempfile.mkdtemp(prefix="sandbox_")
        self.timeout = timeout

    def write_files(self, files: dict[str, str]) -> str:
        """Write files to sandbox directory. Returns the directory path."""
        for filename, content in files.items():
            filepath = os.path.join(self.allowed_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
        return self.allowed_dir

    def compile_check(self, files: dict[str, str]) -> list[str]:
        """Check if all files compile without syntax errors."""
        errors = []
        for filename, code in files.items():
            try:
                compile(code, filename, "exec")
            except SyntaxError as e:
                errors.append(f"{filename}:{e.lineno}: {e.msg}")
        return errors

    def import_check(self, files: dict[str, str]) -> list[str]:
        """Check if files can be imported (runs in subprocess)."""
        errors = []
        sandbox_dir = self.write_files(files)

        for filename in files:
            if not filename.endswith(".py"):
                continue
            module_name = filename.replace(".py", "").replace("/", ".")
            try:
                result = subprocess.run(
                    ["python", "-c", f"import sys; sys.path.insert(0, '{sandbox_dir}'); import {module_name}"],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=sandbox_dir,
                )
                if result.returncode != 0:
                    errors.append(f"{filename}: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                errors.append(f"{filename}: import timed out")
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")

        return errors

    def is_path_allowed(self, path: str) -> bool:
        """Check if a path is within the sandbox directory."""
        resolved = os.path.realpath(path)
        sandbox_resolved = os.path.realpath(self.allowed_dir)
        return resolved.startswith(sandbox_resolved)
