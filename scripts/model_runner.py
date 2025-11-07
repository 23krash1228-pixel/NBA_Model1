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
    print("✅ Starting NBA model run...")

    # --- STEP 0: Setup folders ---
    import pandas as pd
    import os

    os.makedirs("logs", exist_ok=True)
    log_file = "logs/latest_results.txt"
    raw_file = "logs/raw_nbastuffer.csv"

    # --- STEP 1: Pull NBAstuffer CSV (stable for automation) ---
    # NBAstuffer’s team stats CSV (example path for 2025-26)
    csv_url = "https://www.nbastuffer.com/wp-content/uploads/2025-2026/NBA_Stats_Team.csv"

    # Read the CSV
    raw = pd.read_csv(csv_url)

    # (Optional) save a copy for debugging so you can see columns if needed
    raw.to_csv("logs/raw_nbastuffer.csv", index=False)

    # --- STEP 2: Normalize columns so code is robust to name changes ---
    # make a mapping from any “look alike” to the names we want
    df = raw.rename(columns={
        "TEAM": "Team",
        "OFFRTG": "OffRtg",
        "DEFRTG": "DefRtg"
    })

    # --- STEP 3: Compute Power Rating ---
    df["Power"] = (df["OffRtg"] - df["DefRtg"]).round(2)

    # --- STEP 4: Save summary ---
    with open(log_file, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(f"{row['Team']}: OffRtg {row['OffRtg']}, DefRtg {row['DefRtg']}, Power {row['Power']}\n")

    print("✅ Model complete — saved to logs/latest_results.txt")

except Exception as e:
    import traceback, sys
    from datetime import datetime

    with open("logs/error_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Error occurred at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(traceback.format_exc())
    print("❌ Model failed — see logs/error_log.txt")
    sys.exit(1)
