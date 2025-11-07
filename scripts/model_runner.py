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
    print("🏀 Starting NBA model run (using NBAstuffer web scrape)...")

    # --- STEP 1: Pull NBAstuffer HTML page ---
    url = "https://www.nbastuffer.com/2025-2026/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text

    # --- STEP 2: Parse the HTML for the embedded table ---
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if not table:
        raise ValueError("Could not find any <table> tag on NBAstuffer. Page may have changed format.")

    df = pd.read_html(str(table))[0]

    print(f"✅ Found table with {len(df)} rows and {len(df.columns)} columns")

    # --- STEP 3: Auto-clean and detect Off/Def columns ---
    df.columns = [c.strip().upper() for c in df.columns]

    team_col = next((c for c in df.columns if "TEAM" in c), None)
    off_col = next((c for c in df.columns if "OFF" in c), None)
    def_col = next((c for c in df.columns if "DEF" in c), None)

    if not all([team_col, off_col, def_col]):
        raise ValueError(f"Could not detect Off/Def columns. Found: {df.columns.tolist()}")

    df.rename(columns={team_col: "Team", off_col: "OffRtg", def_col: "DefRtg"}, inplace=True)
    df["Power"] = (df["OffRtg"].astype(float) - df["DefRtg"].astype(float)).round(2)

    print("✅ Successfully extracted team ratings from NBAstuffer")

    # --- STEP 4: Format output ---
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"NBA Team Ratings - {timestamp}", ""]
    for _, row in df.iterrows():
        team = row["Team"]
        off = row["OffRtg"]
        deff = row["DefRtg"]
        power = row["Power"]
        lines.append(f"{team}: OffRtg {off}, DefRtg {deff}, Power {power}")

    content = "\n".join(lines)

except Exception as e:  # ✅ This closes the try: block
    print(f"❌ Model failed: {e}")
