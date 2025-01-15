import sqlite3

DB_NAME = "logs.db"

# Initialize the database and create the logs table
def initialize_database():
    """
    Initialize the database by creating the logs table if it does not exist.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                raw_log TEXT NOT NULL
            )
            """
        )
        conn.commit()
        print("[INFO] Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to initialize database: {e}")
    finally:
        conn.close()

# Insert a log into the database
def insert_log(uuid, raw_log):
    """
    Insert a log entry into the database.

    Args:
        uuid (str): The unique identifier for the log source.
        raw_log (str): The raw log data in XML format.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (uuid, raw_log) VALUES (?, ?)", (uuid, raw_log))
        conn.commit()
        print("[INFO] Log inserted successfully.")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert log: {e}")
    finally:
        conn.close()

# Fetch logs by UUID
def fetch_logs_by_uuid(uuid):
    """
    Fetch logs associated with a specific UUID.

    Args:
        uuid (str): The unique identifier for the log source.

    Returns:
        list: A list of raw logs associated with the given UUID.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT raw_log FROM logs WHERE uuid = ?", (uuid,))
        rows = cursor.fetchall()
        print(f"[INFO] Fetched {len(rows)} logs for UUID {uuid}.")
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to fetch logs: {e}")
        return []
    finally:
        conn.close()

# Clear all logs
def clear_logs():
    """
    Delete all logs from the database.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs")
        conn.commit()
        print("[INFO] All logs cleared from the database.")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to clear logs: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
