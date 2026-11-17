import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "la_squadra_doro.db"
SCHEMA_FILE = BASE_DIR / "la_squadra_doro_schema.sql"
SEED_FILE = BASE_DIR / "la_squadra_doro_seed.sql"


def init_db():
    print(f"Connecting to database: {DB_FILE.name}...")
    if DB_FILE.exists():
        try:
            DB_FILE.unlink()
        except Exception:
            pass
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Executing schema DDL (10 tables)...")
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    print("Inserting seed data...")
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed_sql = f.read()
    cursor.executescript(seed_sql)

    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print("\nSuccessfully verified tables in database:")
    for idx, table in enumerate(tables, 1):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {idx:2d}. {table:<22} ({count} rows)")

    conn.close()
    print("\nDatabase initialization complete! You can open 'la_squadra_doro.db' in DB Browser for SQLite.")


if __name__ == "__main__":
    init_db()
