import os
import time
from datetime import datetime
from threading import Lock

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

_db_init_lock = Lock()
_db_initialized = False


def read_config_value(env_name, default=None, strip=True):
    """Lit une valeur depuis VAR ou VAR_FILE si présent."""
    file_var = f"{env_name}_FILE"
    file_path = os.getenv(file_var)

    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            value = f.read()
        return value.strip() if strip else value

    value = os.getenv(env_name, default)
    if isinstance(value, str) and strip:
        return value.strip()
    return value


def get_db_config():
    """Retourne la configuration DB depuis app.config ou l'environnement/secrets."""
    return app.config.get(
        "DB_CONFIG",
        {
            "host": read_config_value("DB_HOST", "db"),
            "database": read_config_value("DB_NAME", "logs_db"),
            "user": read_config_value("DB_USER", "logs_user"),
            "password": read_config_value("DB_PASSWORD", "logs_password"),
            "port": int(read_config_value("DB_PORT", 5432)),
        },
    )


def get_db_connection():
    """Crée une connexion à la base de données."""
    return psycopg2.connect(**get_db_config())


def wait_for_db(max_retries=15, delay=2):
    """Attend que PostgreSQL soit joignable avant l'initialisation."""
    for attempt in range(1, max_retries + 1):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            print(f"Database is ready (attempt {attempt}/{max_retries})")
            return
        except Exception as e:
            print(f"Database not ready yet (attempt {attempt}/{max_retries}): {e}")
            time.sleep(delay)

    raise RuntimeError("Database did not become ready in time")


def init_db():
    """Initialise la base et crée la table logs si besoin."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    level VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    service VARCHAR(100) DEFAULT 'unknown',
                    data JSONB DEFAULT '{}'
                )
                """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp
                ON logs(timestamp DESC)
                """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_level
                ON logs(level)
                """)


def ensure_db_initialized():
    """Initialise la base une seule fois par processus."""
    global _db_initialized

    if _db_initialized:
        return

    with _db_init_lock:
        if _db_initialized:
            return

        wait_for_db()
        init_db()
        _db_initialized = True


@app.before_request
def bootstrap_database():
    """Garantit que la base est prête avant de servir une requête."""
    ensure_db_initialized()


@app.route("/health", methods=["GET"])
def health():
    """Point de santé simple."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return jsonify(
            {
                "status": "ok",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "database": "disconnected",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/logs", methods=["GET"])
def get_logs():
    """Récupère la liste des logs."""
    try:
        limit = min(request.args.get("limit", 100, type=int), 1000)
        offset = request.args.get("offset", 0, type=int)

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, timestamp, level, message, service, data
                    FROM logs
                    ORDER BY timestamp DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                logs = cursor.fetchall()

                logs_list = [
                    {
                        "id": log["id"],
                        "timestamp": log["timestamp"].isoformat(),
                        "level": log["level"],
                        "message": log["message"],
                        "service": log["service"],
                        "data": log["data"],
                    }
                    for log in logs
                ]

                cursor.execute("SELECT COUNT(*) AS count FROM logs")
                total = cursor.fetchone()["count"]

        return jsonify(
            {
                "logs": logs_list,
                "total": total,
                "returned": len(logs_list),
                "limit": limit,
                "offset": offset,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs", methods=["POST"])
def add_log():
    """Ajoute un nouveau log."""
    try:
        payload = request.get_json()

        if payload is None:
            return jsonify({"error": "No data provided"}), 400

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO logs (level, message, service, data)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, timestamp, level, message, service, data
                    """,
                    (
                        payload.get("level", "info"),
                        payload.get("message", ""),
                        payload.get("service", "unknown"),
                        psycopg2.extras.Json(payload.get("data", {})),
                    ),
                )
                log_entry = cursor.fetchone()

        return (
            jsonify(
                {
                    "success": True,
                    "log": {
                        "id": log_entry["id"],
                        "timestamp": log_entry["timestamp"].isoformat(),
                        "level": log_entry["level"],
                        "message": log_entry["message"],
                        "service": log_entry["service"],
                        "data": log_entry["data"],
                    },
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Statistiques simples sur les logs."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) AS total FROM logs")
                total = cursor.fetchone()["total"]

                if total == 0:
                    return jsonify(
                        {
                            "total_logs": 0,
                            "levels": {},
                            "services": {},
                            "last_log": None,
                        }
                    )

                cursor.execute("""
                    SELECT level, COUNT(*) AS count
                    FROM logs
                    GROUP BY level
                    """)
                levels = {row["level"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("""
                    SELECT service, COUNT(*) AS count
                    FROM logs
                    GROUP BY service
                    ORDER BY count DESC
                    LIMIT 10
                    """)
                services = {row["service"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("""
                    SELECT id, timestamp, level, message, service, data
                    FROM logs
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """)
                last_log_row = cursor.fetchone()

        last_log = None
        if last_log_row:
            last_log = {
                "id": last_log_row["id"],
                "timestamp": last_log_row["timestamp"].isoformat(),
                "level": last_log_row["level"],
                "message": last_log_row["message"],
                "service": last_log_row["service"],
                "data": last_log_row["data"],
            }

        return jsonify(
            {
                "total_logs": total,
                "levels": levels,
                "services": services,
                "last_log": last_log,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logs/clear", methods=["DELETE"])
def clear_logs():
    """Vide tous les logs."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM logs")
                deleted_count = cursor.rowcount

        return jsonify(
            {
                "success": True,
                "message": f"{deleted_count} logs cleared",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    ensure_db_initialized()
    app.run(host="0.0.0.0", port=int(read_config_value("BACKEND_PORT", 5000)))  # nosec B104
