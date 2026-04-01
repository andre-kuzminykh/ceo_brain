"""
Critic & Auto-Repair Service.
"""

from __future__ import annotations

from typing import Any

from app.models.state_models import (
    CriticResult,
    CriticVerdict,
    ErrorClass,
    RepairAttempt,
)


class StepCritic:
    """Validates individual step outputs."""

    async def evaluate(
        self,
        action_description: str,
        expected_schema: dict[str, Any] | None,
        actual_output: Any,
        goal_context: str = "",
    ) -> CriticResult:
        issues = []
        score = 1.0

        # Check output exists
        if actual_output is None:
            issues.append("Output is None")
            score = 0.0
            return CriticResult(
                verdict=CriticVerdict.RETRY,
                issues=issues,
                score=score,
            )

        # Check schema conformance
        if expected_schema:
            schema_issues = self._check_schema(expected_schema, actual_output)
            if schema_issues:
                issues.extend(schema_issues)
                score -= 0.3 * len(schema_issues)

        # Check completeness
        if isinstance(actual_output, str) and len(actual_output.strip()) == 0:
            issues.append("Output is empty string")
            score -= 0.5

        if isinstance(actual_output, dict) and not actual_output:
            issues.append("Output is empty dict")
            score -= 0.5

        # Determine verdict
        score = max(0.0, min(1.0, score))
        if score >= 0.8:
            verdict = CriticVerdict.PASS
        elif score >= 0.4:
            verdict = CriticVerdict.RETRY
        else:
            verdict = CriticVerdict.REPAIR

        return CriticResult(verdict=verdict, issues=issues, score=score)

    def _check_schema(self, schema: dict, output: Any) -> list[str]:
        issues = []
        if isinstance(schema, dict) and isinstance(output, dict):
            for key in schema:
                if key not in output:
                    issues.append(f"Missing required field: {key}")
        return issues


class BuildCritic:
    """Validates generated workflow code."""

    async def validate(
        self,
        files: dict[str, str],
        sandbox_runner=None,
    ) -> CriticResult:
        issues = []
        tests_to_run = ["compile", "import", "smoke"]

        # Compile check
        compile_results = self._compile_check(files)
        if compile_results:
            issues.extend(compile_results)
            return CriticResult(
                verdict=CriticVerdict.REPAIR,
                issues=issues,
                score=0.0,
                error_class=ErrorClass.CODEGEN_ERROR,
                fix_strategy=["Fix syntax errors"],
                files_to_change=[f for f in files.keys()],
                tests_to_run=tests_to_run,
            )

        # Import check
        import_results = self._import_check(files)
        if import_results:
            issues.extend(import_results)
            return CriticResult(
                verdict=CriticVerdict.REPAIR,
                issues=issues,
                score=0.2,
                error_class=ErrorClass.CODEGEN_ERROR,
                fix_strategy=["Fix import errors"],
                files_to_change=[f for f in files.keys()],
                tests_to_run=tests_to_run,
            )

        return CriticResult(verdict=CriticVerdict.PASS, score=1.0)

    def _compile_check(self, files: dict[str, str]) -> list[str]:
        issues = []
        for filename, code in files.items():
            try:
                compile(code, filename, "exec")
            except SyntaxError as e:
                issues.append(f"{filename}: SyntaxError at line {e.lineno}: {e.msg}")
        return issues

    def _import_check(self, files: dict[str, str]) -> list[str]:
        # In production, this runs in sandbox subprocess
        # Here we just check for obvious import issues
        issues = []
        for filename, code in files.items():
            for line in code.split("\n"):
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    # Check for obviously wrong imports
                    if "import nonexistent_module" in stripped:
                        issues.append(f"{filename}: Bad import: {stripped}")
        return issues


class RepairService:
    """Auto-repairs generated code based on critic feedback."""

    MAX_ATTEMPTS = 3

    def __init__(self, llm_repair_fn=None):
        self.llm_repair_fn = llm_repair_fn

    async def repair_loop(
        self,
        files: dict[str, str],
        critic: BuildCritic,
        max_attempts: int | None = None,
    ) -> tuple[dict[str, str], list[RepairAttempt], bool]:
        """
        Run repair loop.
        Returns: (final_files, attempts_log, success)
        """
        max_attempts = max_attempts or self.MAX_ATTEMPTS
        attempts = []
        current_files = dict(files)

        for i in range(max_attempts):
            result = await critic.validate(current_files)

            if result.verdict == CriticVerdict.PASS:
                if attempts:
                    attempts[-1].validation_passed = True
                return current_files, attempts, True

            # Record attempt
            attempt = RepairAttempt(
                attempt_number=i + 1,
                error_class=result.error_class or ErrorClass.CODEGEN_ERROR,
                fix_strategy="; ".join(result.fix_strategy),
                files_changed=result.files_to_change,
                validation_passed=False,
                traceback="; ".join(result.issues),
            )
            attempts.append(attempt)

            # Apply repair
            current_files = await self._apply_repair(
                current_files, result, i + 1
            )

        # Final validation
        final_result = await critic.validate(current_files)
        if final_result.verdict == CriticVerdict.PASS:
            attempts[-1].validation_passed = True
            return current_files, attempts, True

        return current_files, attempts, False

    async def _apply_repair(
        self,
        files: dict[str, str],
        critic_result: CriticResult,
        attempt: int,
    ) -> dict[str, str]:
        """Apply repairs based on critic feedback."""
        if self.llm_repair_fn:
            return await self.llm_repair_fn(files, critic_result)

        # Default: simple heuristic repairs for common issues
        repaired = dict(files)
        for issue in critic_result.issues:
            if "SyntaxError" in issue:
                # Extract filename and try basic fix
                for fname in critic_result.files_to_change:
                    if fname in repaired:
                        repaired[fname] = self._fix_syntax(repaired[fname])
            if "Bad import" in issue:
                for fname in critic_result.files_to_change:
                    if fname in repaired:
                        repaired[fname] = self._fix_imports(repaired[fname])

        return repaired

    def _fix_syntax(self, code: str) -> str:
        """Basic syntax fix - remove obviously broken lines."""
        lines = code.split("\n")
        fixed = []
        for line in lines:
            try:
                compile(line + "\n", "<string>", "exec")
                fixed.append(line)
            except SyntaxError:
                fixed.append(f"# REMOVED: {line}")
        return "\n".join(fixed)

    def _fix_imports(self, code: str) -> str:
        """Remove bad imports."""
        lines = code.split("\n")
        fixed = []
        for line in lines:
            if "import nonexistent_module" in line:
                continue
            fixed.append(line)
        return "\n".join(fixed)
