import requests


def test_health() -> None:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    assert response.status_code == 200
