# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ================ Setup ==================
DB_PATH = "database/mlb_stats.db"

@st.cache_data
def load_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# ================ Sidebar Inputs ==================
st.sidebar.title("MLB Stats Dashboard")
category = st.sidebar.selectbox("Select category", ["batting", "pitching"])
year = st.sidebar.selectbox("Select year", [str(y) for y in range(2002, 2026)])
top_n = st.sidebar.slider("Top N", min_value=5, max_value=50, value=10)

table_name = f"{category}_{year}"
st.sidebar.write(f"Table: {table_name}")

# Load Data
try:
    df = load_table(table_name)
    st.write(f"### {category.capitalize()} — Year {year}")
except Exception as e:
    st.error(f"Could not load table {table_name}: {e}")
    st.stop()

# Visualization 1: Top N by #
if "Name" in df.columns:
    df_sorted = df.sort_values("#", ascending=False).head(top_n)
    fig1 = px.bar(df_sorted, x="Name", y="#", color="Team", title=f"Top {top_n} {category} by ‘#’ in {year}")
    st.plotly_chart(fig1)
else:
    st.warning("This table has no 'Name' column.")

# Visualization 2: Statistic vs Value
if "Statistic" in df.columns and "#" in df.columns:
    fig2 = px.scatter(df, x="#", y="Statistic", color="Team", hover_data=["Name"] if "Name" in df.columns else None,
                      title=f"Statistic value distribution – {category} {year}")
    st.plotly_chart(fig2)

# ================ Visualization 3: Trend Over Years ==================
# Only for “Name” present tables; let user pick one player for trend
if "Name" in df.columns:
    player = st.sidebar.text_input("Enter player name for trend chart", "")
    if player:
        conn = sqlite3.connect(DB_PATH)
        # Simplified: load all years for this category and player
        trend_frames = []
        for y in range(2002, 2026):
            tbl = f"{category}_{y}"
            try:
                df_y = pd.read_sql_query(f"SELECT * FROM {tbl} WHERE Name LIKE ?", conn, params=(f"%{player}%",))
                if not df_y.empty and "#" in df_y.columns:
                    df_y["Year"] = y
                    trend_frames.append(df_y)
            except:
                continue
        conn.close()
        if trend_frames:
            trend_df = pd.concat(trend_frames, ignore_index=True)
            fig3 = px.line(trend_df, x="Year", y="#", color="Statistic",
                           title=f"Trend for {player} in {category}")
            st.plotly_chart(fig3)
        else:
            st.info(f"No trend data found for player {player}.")

# End
st.write("___")
st.write("Dashboard built with Streamlit | Data from Baseball-Almanac derived CSVs")
