# ----------------------------
# NBA Auto Model – Real data + Email
# ----------------------------

import os, json, requests, smtplib, ssl
from datetime import datetime
from email.message import EmailMessage

# Make sure folders exist
os.makedirs("logs", exist_ok=True)

# File paths
roster_path = "data/rosters.json"
log_file = "logs/latest_results.txt"

# --- Load your teams from rosters.json ---
with open(roster_path, "r", encoding="utf-8") as f:
    roster = json.load(f)
teams = [t["name"] for t in roster.get("teams", [])]

# --- NBA team abbreviations (for the API) ---
TEAM_MAP = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR", "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
}

def to_abbr(name):
    for k, v in TEAM_MAP.items():
        if name.lower() in k.lower() or k.lower() in name.lower():
            return v
    return None

# --- Pull team stats from balldontlie API ---
def get_team_power(abbr):
    base_url = "https://www.balldontlie.io/api/v1"
    # Get team ID
    teams_resp = requests.get(f"{base_url}/teams", timeout=15).json()["data"]
    match = next((t for t in teams_resp if t["abbreviation"] == abbr), None)
    if not match:
        return None, None

    team_id = match["id"]
    team_name = match["full_name"]

    # Get recent games (up to 25)
    games_resp = requests.get(
        f"{base_url}/games",
        params={"team_ids[]": team_id, "per_page": 25},
        timeout=15
    ).json()["data"]

    if not games_resp:
        return team_name, None

    points = []
    for g in games_resp:
        if g["home_team"]["id"] == team_id:
            points.append(g["home_team_score"])
        else:
            points.append(g["visitor_team_score"])

    if not points:
        return team_name, None

    ppg = sum(points) / len(points)
    league_avg = 115  # simple baseline
    power = round(ppg - league_avg, 2)
    return team_name, power


# --- Run for all your teams ---
lines = []
for team in teams:
    abbr = to_abbr(team)
    if not abbr:
        lines.append(f"{team}: no abbreviation match")
        continue

    name, power = get_team_power(abbr)
    if power is None:
        lines.append(f"{name}: no data available")
    else:
        lines.append(f"{name}: Power rating {power}")

# --- Save results ---
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
content = f"Model run at {timestamp}\n" + "\n".join(lines)

with open(log_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Model completed and saved to logs/latest_results.txt")

# --- Email results using Gmail ---
SMTP_USER = os.getenv("GMAIL_USER")
SMTP_PASS = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

if SMTP_USER and SMTP_PASS and EMAIL_TO:
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"NBA Model Results – {timestamp}"
    msg.set_content(content)

    # attach the text file
    with open(log_file, "rb") as fp:
        msg.add_attachment(
            fp.read(), maintype="text", subtype="plain", filename="latest_results.txt"
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("📧 Email sent successfully.")
else:
    print("ℹ️ Email settings missing – skipped email.")
