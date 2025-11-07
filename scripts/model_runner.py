import os
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime
import traceback
import sys

try:
    # --- STEP 0: Setup folders ---
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/latest_results.txt"

    # --- STEP 1: Pull latest table from nbastuffer.com ---
    url = "https://www.nbastuffer.com/2025-2026/"
    tables = pd.read_html(url)
    df = tables[0]

    # --- STEP 2: Rename columns for consistency ---
    df = df.rename(columns={
        "TEAM": "Team",
        "OFFRTG": "OffRtg",
        "DEFRTG": "DefRtg"
    })

    # --- STEP 3: Compute Power Rating ---
    df["Power"] = (df["OffRtg"] - df["DefRtg"]).round(2)

    # --- STEP 4: Format results ---
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"NBA Team Ratings – {timestamp}", ""]
    for _, row in df.iterrows():
        team = row.get("Team", "Unknown")
        off = row.get("OffRtg", "N/A")
        deff = row.get("DefRtg", "N/A")
        power = row.get("Power", "N/A")
        lines.append(f"{team}: OffRtg {off}, DefRtg {deff}, Power {power}")

    content = "\n".join(lines)

    # --- STEP 5: Save results ---
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Model pulled from NBA Stuffer and
    print("✅ Model pulled from NBA Stuffer and saved to logs/latest_results.txt")

except Exception as e:
    error_log = "logs/error_log.txt"
    with open(error_log, "w", encoding="utf-8") as f:
        f.write(f"Error occurred at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(traceback.format_exc())

    print(f"❌ Model failed — see {error_log}")
    sys.exit(1)
