# Interactive tool for users

# Options:
#     • List all available categories and year ranges
#     • Browse data by category and year
#     • Search for player names across batting/pitching tables

import sqlite3
import os

DB_PATH = os.path.join("database", "mlb_stats.db")

# Get categories

def list_categories():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]
        categories = {}
        for t in tables:
            parts = t.split("_")
            if len(parts) >= 2 and parts[-1].isdigit():
                cat = "_".join(parts[:-1])
                yr = parts[-1]
                categories.setdefault(cat, []).append(yr)

        print("\n📋 Available data:")
        for cat, yrs in categories.items():
            print(f"  {cat:15} → {min(map(int, yrs))}-{max(map(int, yrs))}")
        print()
        return categories

# Query by year

def query_by_year(category, year):
    table = f"{category}_{year}"
    # Show the first 10 rows from a specific category and year table.
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        if not cur.fetchone():
            print(f"⚠️ Table '{table}' not found.")
            return
        cur.execute(f"SELECT * FROM '{table}' LIMIT 10;")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        print(f"\nShowing first 10 rows from {table}:\n")
        print(" | ".join(cols))
        print("-" * 80)
        for r in rows:
            print(" | ".join(str(x) for x in r))

# Query by player name

def search_player(player):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        table_query = """
        SELECT name FROM sqlite_master
        WHERE name LIKE 'batting_%' OR name LIKE 'pitching_%';
        """
        found = False
        for (table,) in cur.execute(table_query):
            # Check if the table contains a 'Name' column
            cols = [c[1] for c in conn.execute(f"PRAGMA table_info('{table}');").fetchall()]
            if "Name" not in cols:
                continue
            # Case-insensitive partial match search
            rows = conn.execute(
                f'SELECT * FROM "{table}" WHERE "Name" LIKE ?', (f"%{player}%",)
            ).fetchall()
            if rows:
                found = True
                print(f"\n📅 {table}")
                for r in rows:
                    print(" | ".join(str(x) for x in r))
        if not found:
            print("No matches found.")

# Interactive loop

if not os.path.exists(DB_PATH):
    print("❌ Database not found. Run the importer first.")
else:
    print("✅ Connected to MLB stats database.")
    list_categories()

    while True:
        print("\nChoose an option:")
        print("1. Browse by year & category")
        print("2. Search for player name (batting/pitching only)")
        print("Q. Quit")
        choice = input("→ ").strip().lower()

        if choice == "1":
            cat = input("Enter category (batting/pitching/fielding/standings/misc): ").strip().lower()
            yr = input("Enter year (e.g. 2014): ").strip()
            query_by_year(cat, yr)
        elif choice == "2":
            name = input("Enter player name: ").strip()
            search_player(name)
        elif choice == "q":
            print("Exiting.")
            break
        else:
            print("Invalid choice.")
