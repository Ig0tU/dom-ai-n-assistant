import sqlite3
import uuid
import json
from .shared.logger import log

DB_PATH = 'db/auraflow.db'

class StateManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS ventures (
                    id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    niche_idea TEXT,
                    product_details TEXT,
                    marketing_details TEXT,
                    sales_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def create_venture(self):
        venture_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute(
                "INSERT INTO ventures (id, state) VALUES (?, ?)",
                (venture_id, "DISCOVERY")
            )
        log.info(f"Created new venture with ID: {venture_id}")
        return venture_id

    def get_venture(self, venture_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM ventures WHERE id = ?", (venture_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def update_venture_state(self, venture_id, new_state):
        with self.conn:
            self.conn.execute(
                "UPDATE ventures SET state = ? WHERE id = ?",
                (new_state, venture_id)
            )
        log.info(f"Venture {venture_id} state updated to: {new_state}")

    def update_venture_details(self, venture_id, detail_field, data):
        # List of allowed columns to prevent SQL injection.
        allowed_fields = ["niche_idea", "product_details", "marketing_details", "sales_details"]
        if detail_field not in allowed_fields:
            log.error(f"Invalid detail_field: {detail_field}. Update aborted.")
            return

        json_data = json.dumps(data)
        with self.conn:
            # Using a safe, parameterized query approach.
            query = f"UPDATE ventures SET {detail_field} = ? WHERE id = ?"
            self.conn.execute(query, (json_data, venture_id))
        log.info(f"Updated {detail_field} for venture {venture_id}")
