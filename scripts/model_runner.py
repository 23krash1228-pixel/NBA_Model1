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
    import os
    import traceback
    from datetime import datetime

    # make sure logs folder exists
    os.makedirs("logs", exist_ok=True)

    log_file = "logs/latest_results.txt"
    error_file = "logs/error_log.txt"

    print("✅ Starting NBA model run...")

    import json

    # --- Load rosters and player stats ---
    
    with open("data/rosters.json", "r", encoding="utf-8") as f:
    rosters = json.load(f)

    with open("data/player_stats.json", "r", encoding="utf-8") as f:
    players = json.load(f)

    # --- STEP 0: Setup folders ---
    import pandas as pd
    import os

    os.makedirs("logs", exist_ok=True)
    log_file = "logs/latest_results.txt"
    raw_file = "logs/raw_nbastuffer.csv"

    # --- STEP 1: Pull NBAstuffer CSV (stable for automation) ---
    # NBAstuffer’s team stats CSV (example path for 2025-26)
    csv_url = "https://www.nbastuffer.com/2025-2026-nba-team-stats/"


    # Read the CSV
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd

    print("📥 Fetching data from NBAstuffer...")

    # URL for 2025-26 team stats page
    url = "https://www.nbastuffer.com/2025-2026-nba-team-stats/"

    # Make the request look like a normal browser
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # will stop if the site is down

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the first table on the page (the big team stats one)
    table = soup.find("table")

    # Convert the HTML table to a DataFrame
    raw = pd.read_html(str(table))[0]

    # Save it to logs
    raw.to_csv("logs/raw_nbastuffer.csv", index=False)
    print("✅ Successfully pulled NBAstuffer data as HTML table")


    # (Optional) save a copy for debugging so you can see columns if needed
    raw.to_csv("logs/raw_nbastuffer.csv", index=False)

    # --- STEP 2: Normalize columns so code is robust to name changes ---
    # make a mapping from any “look alike” to the names we want
    df = raw.rename(columns={
        "TEAM": "Team",
        "OFFRTG": "oEFF",
        "DEFRTG": "dEFF"
    })

    # --- STEP 3: Compute Power Rating ---
    df["Power"] = (df["oEFF"] - df["dEFF"]).round(2)

    import pandas as pd

    player_df = pd.DataFrame(players)
    team_summary = player_df.groupby("Team").agg({
        "PPG": "mean",
        "RPG": "mean",
        "APG": "mean"
    }).reset_index()

    df = df.merge(team_summary, on="Team", how="left")

    # --- STEP 4: Save summary ---
        with open("logs/latest_results.txt", "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            f.write(f"{row['Team']}: OffRtg {row['OffRtg']}, DefRtg {row['DefRtg']}, "
                    f"Power {row['Power']}, Avg PPG {row['PPG']:.1f}, "
                    f"RPG {row['RPG']:.1f}, APG {row['APG']:.1f}\n")


    print("✅ Model complete — saved to logs/latest_results.txt")

except Exception as e:
    with open(error_file, "w") as f:
        f.write(f"Error occurred at {datetime.utcnow()} UTC\n")
        traceback.print_exc(file=f)
    print(f"❌ Model failed – see {error_file}")
    raise  # keep this so GitHub marks the run as failed (exit code 1)

