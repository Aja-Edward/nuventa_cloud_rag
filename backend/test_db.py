from backend.db import get_connection

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT version();")
    print("PostgreSQL version:", cur.fetchone())

    cur.close()
    conn.close()

    print("✅ DB connection successful")

except Exception as e:
    print("❌ DB connection failed:")
    print(e)
