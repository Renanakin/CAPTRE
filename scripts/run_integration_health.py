import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def wait_for_health(url: str, timeout_s: float = 10.0) -> bool:
    end = time.time() + timeout_s
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    api_dir = repo_root / "apps" / "api"

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(api_dir),
    )

    try:
        if not wait_for_health("http://127.0.0.1:8000/api/v1/health"):
            print("Health endpoint no disponible en el tiempo esperado", file=sys.stderr)
            return 1

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "..\\..\\tests\\integration\\test_health.py", "-q"],
            cwd=str(api_dir),
        )
        return result.returncode
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
