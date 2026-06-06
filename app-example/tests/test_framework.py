from fastapi.testclient import TestClient
from app_example.main import app

client = TestClient(app)

def test_list_frameworks():
    response = client.get("/frameworks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("id" in f and "name" in f for f in data)

def test_get_framework_rise():
    response = client.get("/frameworks/rise")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "rise"
    assert data["name"] == "RISE"
    assert "description" in data

def test_get_framework_not_found():
    response = client.get("/frameworks/nonexistent")
    assert response.status_code == 404

def test_list_frameworks_returns_all():
    response = client.get("/frameworks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
