"""Check current repository quality against quality-baseline.json ratchet."""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from quality_baseline import measure_quality

HIGHER_IS_WORSE = ("ruff_problems", "mypy_errors", "tests_skipped", "suppressions")
LOWER_IS_WORSE = ("tests_passed", "coverage_percent")


def check_quality() -> int:
    """Compare measured quality against quality-baseline.json and enforce strict ratchet."""
    baseline_path = REPO_ROOT / "quality-baseline.json"
    if not baseline_path.exists():
        print(f"Error: {baseline_path} not found. Run scripts/quality_baseline.py first.")
        return 1

    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error reading {baseline_path}: {exc}")
        return 1

    current = measure_quality(REPO_ROOT)

    worsened: list[str] = []
    improved: list[str] = []

    print("\n--- Quality Ratchet Verification ---")
    all_keys = list(HIGHER_IS_WORSE) + list(LOWER_IS_WORSE)
    for key in all_keys:
        base_val = baseline.get(key)
        curr_val = current.get(key)
        if base_val is None or curr_val is None:
            print(f"Error: Missing metric '{key}' in baseline or current measurement.")
            return 1

        delta = (
            round(curr_val - base_val, 1) if isinstance(curr_val, float) else curr_val - base_val
        )
        delta_str = f"+{delta}" if delta > 0 else str(delta)

        status = "OK"
        if key in HIGHER_IS_WORSE:
            if curr_val > base_val:
                status = "WORSENED"
                worsened.append(key)
            elif curr_val < base_val:
                status = "IMPROVED"
                improved.append(key)
        else:
            if curr_val < base_val:
                status = "WORSENED"
                worsened.append(key)
            elif curr_val > base_val:
                status = "IMPROVED"
                improved.append(key)

        print(f"  {key:<18}: {base_val} -> {curr_val} ({delta_str}) [{status}]")

    print("------------------------------------\n")

    if worsened:
        print(
            "Quality ratchet failed: at least one metric worsened compared to "
            "quality-baseline.json.",
            file=sys.stderr,
        )
        for key in worsened:
            print(f"  - {key}: baseline {baseline[key]} -> current {current[key]}", file=sys.stderr)
        return 1

    if improved:
        first_improved = improved[0]
        print(
            f"Metric {first_improved} improved: run 'uv run python scripts/quality_baseline.py' "
            "and commit the updated quality-baseline.json to tighten the ratchet.",
            file=sys.stderr,
        )
        return 1

    print("Quality ratchet passed: all metrics match quality-baseline.json exactly.")
    return 0


def main() -> None:
    """Execute quality check."""
    sys.exit(check_quality())


if __name__ == "__main__":
    main()
