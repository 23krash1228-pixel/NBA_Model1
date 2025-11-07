import os
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime
import traceback
import sys
from bs4 import BeautifulSoup  # ✅ You added this
import requests  # ✅ required for scraping

try:
# --- STEP 1: Pull NBAstuffer CSV (stable for automation) ---
import pandas as pd

# NBAstuffer’s team stats CSV (example path for 2025-26)
csv_url = "https://www.nbastuffer.com/wp-content/uploads/2025-2026/NBA_Stats_Team.csv"

# Read the CSV
raw = pd.read_csv(csv_url)

# (Optional) save a copy for debugging so you can see columns if needed
raw.to_csv("logs/raw_nbastuffer.csv", index=False)

# --- STEP 2: Normalize columns so code is robust to name changes ---
# make a mapping from any “look alike” to the names we want
norm_map = {}
upper_cols = {c.upper(): c for c in raw.columns}

# Try to grab the three important columns using flexible matches
def pick(col_names, candidates):
    # return the first column in this CSV whose UPPER name matches any candidate
    for cand in candidates:
        if cand in upper_cols:
            return upper_cols[cand]
    # if not found, try contains style matches
    for c_up, c_orig in upper_cols.items():
        if any(tok in c_up for tok in candidates):
            return c_orig
    return None

team_col = pick(upper_cols, ["TEAM"])
off_col  = pick(upper_cols, ["OFFRTG", "OFF_RTG", "OFF RATING", "ORTG", "OFFENSIVE RATING"])
def_col  = pick(upper_cols, ["DEFRTG", "DEF_RTG", "DEF RATING", "DRTG", "DEFENSIVE RATING"])

if not all([team_col, off_col, def_col]):
    raise ValueError(f"Could not find columns. Got: {list(raw.columns)}")

df = raw.rename(columns={team_col: "Team", off_col: "OffRtg", def_col: "DefRtg"}).copy()

# ensure numeric
df["OffRtg"] = pd.to_numeric(df["OffRtg"], errors="coerce")
df["DefRtg"] = pd.to_numeric(df["DefRtg"], errors="coerce")

# --- STEP 3: Compute Power ---
df["Power"] = (df["OffRtg"] - df["DefRtg"]).round(2)

# --- STEP 4: build text lines (same as before) ---
from datetime import datetime
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
lines = [f"NBA Team Ratings - {timestamp}", ""]
for _, row in df.iterrows():
    team  = row["Team"]
    off   = row["OffRtg"]
    deff  = row["DefRtg"]
    power = row["Power"]
    lines.append(f"{team}: OffRtg {off}, DefRtg {deff}, Power {power}")

content = "\n".join(lines)

# write to file (your code probably already does this; keep just one writer)
with open("logs/latest_results.txt", "w", encoding="utf-8") as f:
    f.write(content)
