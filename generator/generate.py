import json
import psycopg2
import random
import time
import os
from datetime import datetime, timezone

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "events_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

EVENT_TYPES = ["page_view", "purchase", "error"]

METADATA = {
    "page_view": lambda: {"page": random.choice(["/home", "/product", "/cart", "/about"])},
    "purchase": lambda: {"amount": round(random.uniform(5.0, 200.0), 2), "item_id": f"item_{random.randint(1, 50)}"},
    "error": lambda: {"code": random.choice([404, 500, 403]), "message": "something went wrong"},
}

def wait_for_db():
    for attempt in range(10):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            print("DB connected")
            return
        except Exception as e:
            print(f"Waiting for DB... attempt {attempt + 1}: {e}")
            time.sleep(3)
    raise Exception("Could not connect to DB after 10 attempts")

def generate_event():
    event_type = random.choice(EVENT_TYPES)
    return {
        "event_type": event_type,
        "user_id": f"user_{random.randint(1, 20)}",
        "timestamp": datetime.now(timezone.utc),
        "metadata": METADATA[event_type](),
    }

def insert_event(conn, event):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO events (event_type, user_id, timestamp, metadata)
            VALUES (%s, %s, %s, %s)
            """,
            (
                event["event_type"],
                event["user_id"],
                event["timestamp"],
                json.dumps(event["metadata"]),
            ),
        )
    conn.commit()

def main():
    wait_for_db()
    conn = psycopg2.connect(**DB_CONFIG)
    count = int(os.getenv("EVENT_COUNT", "200"))
    print(f"Generating {count} events...")
    for _ in range(count):
        event = generate_event()
        insert_event(conn, event)
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
