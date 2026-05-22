import psycopg2
import matplotlib.pyplot as plt
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "events_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def plot_event_type_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT event_type, COUNT(*) AS count
            FROM events
            GROUP BY event_type
            ORDER BY count DESC
        """)
        rows = cur.fetchall()

    labels = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    plt.figure()
    plt.bar(labels, counts, color="steelblue")
    plt.title("Event Count by Type")
    plt.xlabel("Event Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("/output/event_type_count.png")
    plt.close()
    print("Saved: event_type_count.png")

def plot_hourly_trend(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('hour', timestamp) AS hour, COUNT(*) AS count
            FROM events
            GROUP BY hour
            ORDER BY hour
        """)
        rows = cur.fetchall()

    hours = [row[0].strftime("%H:%M") for row in rows]
    counts = [row[1] for row in rows]

    plt.figure()
    plt.plot(hours, counts, marker="o", color="steelblue")
    plt.title("Hourly Event Trend")
    plt.xlabel("Hour")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("/output/hourly_trend.png")
    plt.close()
    print("Saved: hourly_trend.png")

def main():
    conn = get_connection()
    plot_event_type_count(conn)
    plot_hourly_trend(conn)
    conn.close()

if __name__ == "__main__":
    main()