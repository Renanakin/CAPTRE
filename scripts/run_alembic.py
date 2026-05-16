from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    api_dir = repo_root / "apps" / "api"

    args = sys.argv[1:]
    if not args:
        print("Usage: python scripts/run_alembic.py <alembic args>", file=sys.stderr)
        return 2

    command = [sys.executable, "-c", "from alembic.config import main; main()", *args]
    env = os.environ.copy()
    process = subprocess.run(command, cwd=str(api_dir), env=env)
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
