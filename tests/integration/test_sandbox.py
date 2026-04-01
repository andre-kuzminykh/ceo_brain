"""
Integration tests for sandbox runner.
Requirement ID: NFR-10
Test Case ID: TC-NFR-010-01
"""

import os
import tempfile

import pytest

from app.infra.sandbox import SandboxRunner


@pytest.mark.integration
class TestSandboxRunner:

    def test_NFR_010_path_restriction(self):
        """
        Automation ID: AT-NFR-010-INT-01
        Description: Sandbox blocks access outside allowed directory.
        """
        with tempfile.TemporaryDirectory() as sandbox_dir:
            runner = SandboxRunner(allowed_dir=sandbox_dir)

            # Inside sandbox: allowed
            inside = os.path.join(sandbox_dir, "test.py")
            assert runner.is_path_allowed(inside)

            # Outside sandbox: blocked
            assert not runner.is_path_allowed("/etc/passwd")
            assert not runner.is_path_allowed("/tmp/outside.py")
            assert not runner.is_path_allowed(os.path.expanduser("~"))

    def test_NFR_010_symlink_escape_blocked(self):
        """
        Description: Symlink escape attempt is blocked.
        """
        with tempfile.TemporaryDirectory() as sandbox_dir:
            runner = SandboxRunner(allowed_dir=sandbox_dir)

            # Create a symlink pointing outside
            link_path = os.path.join(sandbox_dir, "escape_link")
            try:
                os.symlink("/etc", link_path)
                # The resolved path should be outside sandbox
                assert not runner.is_path_allowed(os.path.join(link_path, "passwd"))
            except OSError:
                pytest.skip("Cannot create symlinks in this environment")

    def test_compile_check_valid_code(self):
        """Description: Valid Python files pass compile check."""
        runner = SandboxRunner()
        files = {
            "good.py": "def hello():\n    return 'world'\n",
        }
        errors = runner.compile_check(files)
        assert errors == []

    def test_compile_check_invalid_code(self):
        """Description: Invalid Python files fail compile check."""
        runner = SandboxRunner()
        files = {
            "bad.py": "def hello(\n    return 'world'\n",
        }
        errors = runner.compile_check(files)
        assert len(errors) > 0
        assert "bad.py" in errors[0]

    def test_write_files_creates_in_sandbox(self):
        """Description: Files are written inside sandbox directory."""
        with tempfile.TemporaryDirectory() as sandbox_dir:
            runner = SandboxRunner(allowed_dir=sandbox_dir)
            files = {"test.py": "x = 1\n"}

            result_dir = runner.write_files(files)
            assert os.path.exists(os.path.join(result_dir, "test.py"))
            assert runner.is_path_allowed(os.path.join(result_dir, "test.py"))
