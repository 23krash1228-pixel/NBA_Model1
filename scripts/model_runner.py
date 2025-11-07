import os
import json
import pandas as pd
from datetime import datetime
import traceback

try:
    print("✅ Starting NBA model run...")

    # --- STEP 0: Setup folders ---
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/latest_results.txt"
    raw_file = "logs/raw_nbastuffer.csv"

    # --- STEP 1: Load rosters and player stats ---
    with open("data/rosters.json", "r", encoding="utf-8") as f:
        rosters = json.load(f)

    with open("data/player_stats.json", "r", encoding="utf-8") as f:
        players = json.load(f)

    # --- STEP 2: Pull latest team stats from NBAstuffer ---
    csv_url = "https://www.nbastuffer.com/2025-2026/"
    tables = pd.read_html(csv_url)
    df = tables[0]  # Get the first table (team stats)
    print("✅ Successfully pulled NBAstuffer data")

    # --- STEP 3: Clean and normalize ---
    df.columns = [c.strip() for c in df.columns]  # remove extra spaces
    if "OffRtg" in df.columns and "DefRtg" in df.columns:
        df["Power"] = (df["oEFF"] - df["dEFF"]).round(2)
    else:
        print("⚠️ Missing expected columns (OffRtg/DefRtg) in NBAsuffer data")

    # --- STEP 4: Merge player stats into team stats ---
    # Create a DataFrame from player_stats.json
    player_rows = []
    for p in players:
        player_rows.append({
            "Player": p.get("Player", "Unknown"),
            "TEAM": p.get("TEAM", "Unknown"),
            "PPG": p.get("PPG", 0),
            "APG": p.get("APG", 0),
            "RPG": p.get("RPG", 0)
        })



    player_df = pd.DataFrame(player_rows)

    # Calculate average player stats per team
       TEAM_AVGS = player_df.groupby("TEAM")[["PPG", "APG", "RPG"]].mean().round(1).reset_index()
        df = df.merge(TEAM_AVGS, how="left", on="TEAM")

    # Add roster size (optional)
    df["RosterSize"] = df["TEAM"].apply(lambda t: len(rosters.get(t, [])))

    # --- STEP 5: Save results to log file ---
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"NBA Model Update — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        for _, row in df.iterrows():
            f.write(
                f"{row['TEAM']}: "
                f"OffRtg {row.get('OffRtg', 'N/A')}, "
                f"DefRtg {row.get('DefRtg', 'N/A')}, "
                f"Power {row.get('Power', 'N/A')}, "
                f"Avg PPG {row.get('PPG', 'N/A')}, "
                f"Avg APG {row.get('APG', 'N/A')}, "
                f"Avg RPG {row.get('RPG', 'N/A')}, "
                f"Roster Size {row.get('RosterSize', 'N/A')}\n"
            )

    # --- STEP 6: Save raw data as CSV for debugging ---
    df.to_csv(raw_file, index=False)
    print("✅ Model complete — results saved to logs/latest_results.txt")

except Exception as e:
    error_log = "logs/error_log.txt"
    with open(error_log, "w", encoding="utf-8") as f:
        f.write(f"Error occurred at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write(traceback.format_exc())
    print(f"❌ Model failed — see {error_log}")
