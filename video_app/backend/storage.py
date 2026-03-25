import json
import threading

try:
    import pymysql
    from pymysql.cursors import DictCursor
except Exception:
    pymysql = None
    DictCursor = None

from video_system_settings import load_settings


class MySQLStorage:
    def __init__(self):
        self._lock = threading.RLock()
        self._initialized = False

    def _config(self):
        database = load_settings()["database"]
        return {
            "host": database["host"],
            "port": int(database["port"]),
            "user": database["user"],
            "password": database["password"],
            "database": database["name"],
            "charset": database["charset"],
        }

    def _connect(self, with_database=True):
        if pymysql is None:
            raise RuntimeError("missing pymysql")
        config = self._config()
        options = {
            "host": config["host"],
            "port": config["port"],
            "user": config["user"],
            "password": config["password"],
            "charset": config["charset"],
            "cursorclass": DictCursor,
            "autocommit": True,
        }
        if with_database:
            options["database"] = config["database"]
        return pymysql.connect(**options)

    def ensure_ready(self):
        with self._lock:
            if self._initialized:
                return

            config = self._config()
            with self._connect(with_database=False) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{config['database']}` "
                        f"DEFAULT CHARACTER SET {config['charset']}"
                    )
            with self._connect(with_database=True) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS action_preferences (
                            action_id VARCHAR(128) PRIMARY KEY,
                            params_json LONGTEXT NOT NULL,
                            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS run_logs (
                            id BIGINT PRIMARY KEY AUTO_INCREMENT,
                            action_id VARCHAR(128) NOT NULL,
                            action_title VARCHAR(255) NOT NULL,
                            success TINYINT(1) NOT NULL,
                            message TEXT,
                            params_json LONGTEXT,
                            result_json LONGTEXT,
                            logs LONGTEXT,
                            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            INDEX idx_run_logs_action_time (action_id, created_at)
                        )
                        """
                    )
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS path_history (
                            id BIGINT PRIMARY KEY AUTO_INCREMENT,
                            path_kind VARCHAR(32) NOT NULL,
                            path_value VARCHAR(512) NOT NULL,
                            use_count INT NOT NULL DEFAULT 1,
                            last_used_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
                            UNIQUE KEY uniq_path_history (path_kind, path_value)
                        )
                        """
                    )
            self._initialized = True

    def status_text(self):
        if pymysql is None:
            return "missing: No module named 'pymysql'"
        try:
            self.ensure_ready()
            return "ok"
        except Exception as exc:
            return f"unavailable: {exc}"

    def load_preferences(self, action_id):
        self.ensure_ready()
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT params_json FROM action_preferences WHERE action_id=%s", (action_id,))
                row = cursor.fetchone()
        if not row:
            return {}
        try:
            return json.loads(row["params_json"] or "{}")
        except Exception:
            return {}

    def save_preferences(self, action_id, params):
        self.ensure_ready()
        payload = json.dumps(params or {}, ensure_ascii=False)
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO action_preferences (action_id, params_json)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE params_json=VALUES(params_json), updated_at=CURRENT_TIMESTAMP
                    """,
                    (action_id, payload),
                )

    def save_run_log(self, action_id, action_title, params, result):
        self.ensure_ready()
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO run_logs (
                        action_id, action_title, success, message, params_json, result_json, logs
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        action_id,
                        action_title,
                        1 if result.get("success") else 0,
                        result.get("message", ""),
                        json.dumps(params or {}, ensure_ascii=False),
                        json.dumps(result.get("data", {}), ensure_ascii=False),
                        result.get("logs", ""),
                    ),
                )

    def recent_logs(self, action_id=None, limit=20):
        self.ensure_ready()
        limit = max(1, min(int(limit), 200))
        sql = "SELECT id, action_id, action_title, success, message, created_at FROM run_logs "
        args = []
        if action_id:
            sql += "WHERE action_id=%s "
            args.append(action_id)
        sql += "ORDER BY created_at DESC, id DESC LIMIT %s"
        args.append(limit)
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(args))
                rows = cursor.fetchall() or []
        return rows

    def save_path_history(self, items):
        self.ensure_ready()
        normalized = []
        seen = set()
        for item in items or []:
            path_kind = str(item.get("path_kind") or "").strip()
            path_value = str(item.get("path_value") or "").strip()
            if not path_kind or not path_value:
                continue
            key = (path_kind, path_value)
            if key in seen:
                continue
            seen.add(key)
            normalized.append((path_kind, path_value[:512]))
        if not normalized:
            return
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                for path_kind, path_value in normalized:
                    cursor.execute(
                        """
                        INSERT INTO path_history (path_kind, path_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            use_count = use_count + 1,
                            last_used_at = CURRENT_TIMESTAMP
                        """,
                        (path_kind, path_value),
                    )

    def recent_path_history(self, path_kind=None, limit=30):
        self.ensure_ready()
        limit = max(1, min(int(limit), 200))
        sql = "SELECT path_kind, path_value, use_count, last_used_at FROM path_history "
        args = []
        if path_kind:
            sql += "WHERE path_kind=%s "
            args.append(path_kind)
        sql += "ORDER BY last_used_at DESC, use_count DESC, id DESC LIMIT %s"
        args.append(limit)
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, tuple(args))
                rows = cursor.fetchall() or []
        return rows

    def delete_path_history(self, path_kind, path_value):
        self.ensure_ready()
        normalized_kind = str(path_kind or "").strip()
        normalized_value = str(path_value or "").strip()
        if not normalized_kind or not normalized_value:
            return 0
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM path_history WHERE path_kind=%s AND path_value=%s",
                    (normalized_kind, normalized_value[:512]),
                )
                return int(cursor.rowcount or 0)

    def clear_path_history(self, path_kind):
        self.ensure_ready()
        normalized_kind = str(path_kind or "").strip()
        if not normalized_kind:
            return 0
        with self._connect(with_database=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM path_history WHERE path_kind=%s",
                    (normalized_kind,),
                )
                return int(cursor.rowcount or 0)


_STORE = MySQLStorage()


def get_storage():
    return _STORE
