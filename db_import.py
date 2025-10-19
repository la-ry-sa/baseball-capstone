# Imports all scraped CSV files from the /data folder
# into a single SQLite database (mlb_stats.db)

import os
import pandas as pd
import sqlite3

# Path setup

data_folder = "data"
db_path = os.path.join("database/mlb_stats.db")

# Reset database
if os.path.exists(db_path):
    os.remove(db_path)
    print("Existing database removed — starting fresh.")

# Create new connection
conn = sqlite3.connect(db_path)

# Import
for file in os.listdir(data_folder):
    if file.endswith(".csv"):
        csv_path = os.path.join(data_folder, file)
        table_name = os.path.splitext(file)[0]
        print(f"Importing {file} → table '{table_name}'")

        try:
            # Skip first two garbage rows, clean headers
            df = pd.read_csv(csv_path, skiprows=2, header=0)
            # Drop empty rows
            df.dropna(how="all", inplace=True)
            # Remove duplicate header rows
            if "Statistic" in df.columns:
                df = df[df["Statistic"].astype(str).str.lower() != "statistic"]

            # Clean string fields: trim spaces, remove non-breaking spaces
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.replace("\xa0", " ", regex=False)
                )

            # Standardize column names
            df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

            # Write to SQLite
            if not df.empty:
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"   ✅ Imported {len(df)} rows into '{table_name}'")
            else:
                print(f"   ⚠️ {file} produced an empty DataFrame — skipped.")

        except Exception as e:
            print(f"   ❌ Failed to import {file}: {e}")
            with open("import_errors.log", "a") as log:
                log.write(f"{file} — {e}\n")

# Close connection
conn.close()
print("\n All CSVs imported successfully into mlb_stats.db")
