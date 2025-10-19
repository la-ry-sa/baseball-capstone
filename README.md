# MLB Stats Dashboard — Capstone Project

This project scrapes, cleans, and visualizes **Major League Baseball (MLB)** historical data from [Baseball Almanac](https://www.baseball-almanac.com/).  
It demonstrates a full data workflow: **web scraping → CSV export → database import → interactive visualization**.

---

## Project Overview

**Goal:**  
To build a data pipeline and interactive dashboard that showcases MLB statistics (batting, pitching, standings, and more) from 2000–2025.

**Main Steps:**
1. **Web Scraping** – `scraper.py`  
   Uses Selenium to extract yearly baseball statistics tables and saves them as CSVs.

2. **Database Import** – `db_importer.py`  
   Cleans and imports all CSVs into a single SQLite database (`mlb_stats.db`), one table per file.

3. **Query Tool** – `query_tool.py`  
   Interactive command-line tool to explore the database, list available years, and search by player name.

4. **Dashboard** – `dashboard.py`  
   Streamlit app that visualizes key statistics and trends across multiple years, using Plotly for dynamic charts.

---

## Requirements

All dependencies are listed in **`requirements.txt`**.  

Running the Project
1. Scrape Data
python scraper.py

2. Import into SQLite
python db_importer.py

3. Explore via CLI
python query_tool.py

4. Launch the Dashboard
streamlit run dashboard.py
