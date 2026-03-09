import json
import os

import pytest
from app import app, get_db_connection, init_db

TEST_DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "logs_db"),
    "user": os.getenv("DB_USER", "logs_user"),
    "password": os.getenv("DB_PASSWORD", "logs_password"),
    "port": int(os.getenv("DB_PORT", 5432)),
}


@pytest.fixture(scope="session")
def test_db():
    """Initialise la base de test une fois pour la session."""
    app.config["DB_CONFIG"] = TEST_DB_CONFIG
    init_db()
    yield


@pytest.fixture(autouse=True)
def clean_logs_table(test_db):
    """Nettoie la table avant chaque test pour éviter les effets de bord."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    cursor.close()
    conn.close()


@pytest.fixture
def client(test_db):
    """Crée un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert "database" in data
    assert "timestamp" in data
    assert data["status"] == "ok"


def test_add_log(client):
    test_log = {
        "level": "info",
        "message": "Test log message",
        "service": "test_service",
        "data": {"key": "value"},
    }

    response = client.post(
        "/logs",
        data=json.dumps(test_log),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert "log" in data
    assert data["log"]["message"] == test_log["message"]
    assert data["log"]["level"] == test_log["level"]
    assert data["log"]["service"] == test_log["service"]


def test_get_logs(client):
    test_log = {
        "level": "info",
        "message": "Test log for retrieval",
        "service": "test_service",
    }

    client.post(
        "/logs",
        data=json.dumps(test_log),
        content_type="application/json",
    )

    response = client.get("/logs")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "logs" in data
    assert "total" in data
    assert "returned" in data
    assert "limit" in data
    assert "offset" in data
    assert data["total"] == 1

    response = client.get("/logs?limit=1&offset=0")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["logs"]) <= 1


def test_get_stats(client):
    test_logs = [
        {"level": "info", "message": "Test log 1", "service": "service1"},
        {"level": "error", "message": "Test log 2", "service": "service2"},
        {"level": "warning", "message": "Test log 3", "service": "service1"},
    ]

    for log in test_logs:
        client.post(
            "/logs",
            data=json.dumps(log),
            content_type="application/json",
        )

    response = client.get("/stats")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total_logs" in data
    assert "levels" in data
    assert "services" in data
    assert "last_log" in data
    assert data["total_logs"] == len(test_logs)
    assert "info" in data["levels"]
    assert "error" in data["levels"]
    assert "warning" in data["levels"]
    assert "service1" in data["services"]
    assert "service2" in data["services"]


def test_clear_logs(client):
    test_log = {
        "level": "info",
        "message": "Test log to be cleared",
        "service": "test_service",
    }

    client.post(
        "/logs",
        data=json.dumps(test_log),
        content_type="application/json",
    )

    response = client.delete("/logs/clear")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "success" in data
    assert data["success"] is True

    response = client.get("/logs")
    data = json.loads(response.data)
    assert data["total"] == 0


def test_invalid_log_data(client):
    invalid_log = {
        "invalid_field": "test",
    }

    response = client.post(
        "/logs",
        data=json.dumps(invalid_log),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["log"]["level"] == "info"
    assert data["log"]["message"] == ""
    assert data["log"]["service"] == "unknown"
