from __future__ import annotations

import re
import subprocess
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], description: str) -> int:
    print(f"[security-gate] {description}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode


def _load_dependency_allowlist() -> set[str]:
    file_path = ROOT / "docs" / "SECURITY_DEPENDENCY_ALLOWLIST.json"
    if not file_path.exists():
        return set()
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    ids = payload.get("allowed_vulnerability_ids") or []
    return {str(item).strip() for item in ids if str(item).strip()}


def _secrets_scan() -> int:
    include_extensions = {".py", ".yml", ".yaml", ".json", ".env", ".ini", ".toml"}
    excluded_prefixes = {
        ROOT / "docs",
        ROOT / "node_modules",
        ROOT / ".git",
        ROOT / "tests",
    }
    excluded_files = {
        ROOT / ".env.example",
    }

    patterns = [
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----"),
        re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{24,}"),
        re.compile(r"(?i)token\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{24,}"),
    ]

    findings: list[str] = []
    for file_path in ROOT.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path in excluded_files:
            continue
        if any(str(file_path).startswith(str(prefix)) for prefix in excluded_prefixes):
            continue
        if file_path.suffix.lower() not in include_extensions:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            for pattern in patterns:
                if pattern.search(line):
                    rel = file_path.relative_to(ROOT)
                    findings.append(f"{rel}:{line_no}: potential secret pattern")
                    break

    if findings:
        print("[security-gate] Secret scan findings:")
        for item in findings[:200]:
            print(f"- {item}")
        if len(findings) > 200:
            print(f"... and {len(findings) - 200} more")
        return 1

    print("[security-gate] Secret scan: no findings")
    return 0


def main() -> int:
    failures = 0

    failures += _run(
        [
            sys.executable,
            "-m",
            "bandit",
            "-q",
            "-r",
            "apps/api/app",
            "apps/back/app",
            "apps/worker/app",
            "-lll",
            "-iii",
        ],
        "SAST bandit (high severity/confidence)",
    )

    allowlist = sorted(_load_dependency_allowlist())
    pip_audit_cmd = [sys.executable, "-m", "pip_audit", "-r", "apps/api/requirements.txt"]
    for vuln in allowlist:
        pip_audit_cmd.extend(["--ignore-vuln", vuln])
    failures += _run(pip_audit_cmd, "Dependency audit pip-audit")
    failures += _secrets_scan()

    if failures:
        print("[security-gate] FAILED")
        return 1

    print("[security-gate] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
