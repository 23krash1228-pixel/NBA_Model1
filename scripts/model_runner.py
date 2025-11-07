import os
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime
import traceback
import sys

try:
    print("🏀 Starting NBA model run...")

    # --- STEP 0: Setup folders ---
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/latest_results.txt"

# --- STEP 1: Pull latest table dynamically from NBAstuffer ---
    url = "https://www.nbastuffer.com/2025-2026/"
    tables = pd.read_html(url)

    # Try to find the table that actually contains offensive/defensive ratings
    df = None
    for t in tables:
        cols = [c.lower() for c in t.columns.astype(str)]
        if any("off" in c for c in cols) and any("def" in c for c in cols):
            df = t
            break

    if df is None:
        raise ValueError("Could not find Off/Def Rating table on NBAstuffer.")

    # Normalize column names
    df.columns = [c.strip().title().replace("Off", "OffRtg").replace("Def", "DefRtg").replace("Team", "Team") for c in df.columns]

    # Extract the key columns that exist
    team_col = next((c for c in df.columns if "Team" in c), None)
    off_col = next((c for c in df.columns if "Off" in c), None)
    def_col = next((c for c in df.columns if "Def" in c), None)

    if not all([team_col, off_col, def_col]):
        raise ValueError(f"Column mismatch: found {df.columns.tolist()}")

    # --- STEP 3: Compute Power Rating ---
    df["Power"] = (df[off_col].astype(float) - df[def_col].astype(float)).round(2)

    # --- STEP 4: Format results ---
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"NBA Team Ratings - {timestamp}", ""]
    for _, row in df.iterrows():
        team = row.get(team_col, "Unknown")
        off = row.get(off_col, "N/A")
        deff = row.get(def_col, "N/A")
        power = row.get("Power", "N/A")
        lines.append(f"{team}: OffRtg {off}, DefRtg {deff}, Power {power}")

    content = "\n".join(lines)

    # --- STEP 5: Save results ---
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Model pulled from NBA Stuffer and saved to logs/latest_results.txt")

except Exception as e:
    error_log = "logs/error_log.txt"
    with open(error_log, "w", encoding="utf-8") as f:
        f.write(f"Error occurred at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(traceback.format_exc())
    print(f"❌ Model failed – see {error_log}")
