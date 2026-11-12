"""Generate quality baseline metrics for the repository."""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

from defusedxml import ElementTree

REPO_ROOT = Path(__file__).resolve().parent.parent

SUPPRESSION_PATTERN = re.compile(r"(#\s*noqa|#\s*type:\s*ignore|pragma:\s*no\s*cover)")


def measure_ruff(repo_root: Path) -> int:
    """Measure number of ruff lint problems."""
    cmd = [sys.executable, "-m", "ruff", "check", ".", "--output-format=json"]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"ruff check failed with code {proc.returncode}:\n{proc.stderr}")
    try:
        data = json.loads(proc.stdout) if proc.stdout.strip() else []
        return len(data)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse ruff output: {exc}") from exc


def measure_mypy(repo_root: Path) -> int:
    """Measure number of mypy type check errors."""
    cmd = [sys.executable, "-m", "mypy"]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"mypy failed with code {proc.returncode}:\n{proc.stderr}")
    error_lines = [line for line in proc.stdout.splitlines() if ": error:" in line]
    if proc.returncode == 1 and not error_lines:
        raise RuntimeError(f"mypy exited with code 1 but no error lines found:\n{proc.stdout}")
    return len(error_lines)


def measure_tests_and_coverage(repo_root: Path) -> tuple[int, int, float]:
    """Measure tests passed, tests skipped, and coverage percent using pytest."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cov_json_path = tmp_path / "coverage.json"
        junit_xml_path = tmp_path / "junit.xml"
        cov_data_path = tmp_path / ".coverage"

        env = os.environ.copy()
        env["COVERAGE_FILE"] = str(cov_data_path)

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--cov=ad_copy_grader",
            f"--cov-report=json:{cov_json_path}",
            f"--junitxml={junit_xml_path}",
            "-q",
        ]
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        root_coverage = repo_root / ".coverage"
        if root_coverage.exists():
            root_coverage.unlink(missing_ok=True)

        if proc.returncode != 0:
            raise RuntimeError(
                f"pytest suite must be green, failed with code {proc.returncode}:\n"
                f"{proc.stdout}\n{proc.stderr}"
            )

        if not junit_xml_path.exists():
            raise RuntimeError("pytest junit xml output was not generated.")
        if not cov_json_path.exists():
            raise RuntimeError("coverage json report was not generated.")

        tree = ElementTree.parse(junit_xml_path)
        root = tree.getroot()

        tests_count = 0
        skipped_count = 0
        failures_count = 0
        errors_count = 0

        suite_elements = [root] if root.tag == "testsuite" else root.findall("testsuite")
        for suite in suite_elements:
            tests_count += int(suite.attrib.get("tests", 0))
            skipped_count += int(suite.attrib.get("skipped", 0))
            failures_count += int(suite.attrib.get("failures", 0))
            errors_count += int(suite.attrib.get("errors", 0))

        passed_count = tests_count - failures_count - errors_count - skipped_count

        cov_data = json.loads(cov_json_path.read_text(encoding="utf-8"))
        raw_pct = float(cov_data.get("totals", {}).get("percent_covered", 0.0))
        coverage_percent = round(raw_pct, 1)

        return passed_count, skipped_count, coverage_percent


def measure_suppressions(repo_root: Path) -> int:
    """Count occurrences of noqa, type: ignore, and pragma: no cover in src/ and tests/."""
    count = 0
    for target_dir in ("src", "tests"):
        dir_path = repo_root / target_dir
        if not dir_path.exists():
            continue
        for py_path in dir_path.rglob("*.py"):
            text = py_path.read_text(encoding="utf-8", errors="ignore")
            count += len(SUPPRESSION_PATTERN.findall(text))
    return count


def measure_quality(repo_root: Path) -> dict[str, Any]:
    """Measure all 6 quality ratchet metrics."""
    ruff_problems = measure_ruff(repo_root)
    mypy_errors = measure_mypy(repo_root)
    tests_passed, tests_skipped, coverage_percent = measure_tests_and_coverage(repo_root)
    suppressions = measure_suppressions(repo_root)

    return {
        "ruff_problems": ruff_problems,
        "mypy_errors": mypy_errors,
        "tests_passed": tests_passed,
        "tests_skipped": tests_skipped,
        "coverage_percent": coverage_percent,
        "suppressions": suppressions,
    }


def main() -> None:
    """Measure quality metrics and record baseline to quality-baseline.json."""
    print("Measuring repository quality metrics...")
    metrics = measure_quality(REPO_ROOT)
    metrics["generated_at"] = date.today().isoformat()

    baseline_path = REPO_ROOT / "quality-baseline.json"
    baseline_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded quality baseline to {baseline_path}:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
