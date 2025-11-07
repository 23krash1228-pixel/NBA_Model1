# ----------------------------
# NBA Auto Model – NBA Stuffer Version (auto-safe)
# ----------------------------
import os
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime

os.makedirs("logs", exist_ok=True)
log_file = "logs/latest_results.txt"

# ---- STEP 1: pull latest table from nbastuffer.com ----
url = "https://www.nbastuffer.com/2025-2026/"
tables = pd.read_html(url)
df = tables[0]
print(df.head())

# show columns for debugging (optional)
print("Columns found:", list(df.columns))

# ---- STEP 2: try to find columns automatically ----
# Some tables might have slightly different column headers like 'Team Name' or 'Off Rating'
rename_map = {}
for col in df.columns:
    col_lower = col.lower()
    if "team" in col_lower:
        rename_map[col] = "Team"
    elif "off" in col_lower and "rtg" in col_lower:
        rename_map[col] = "OffRtg"
    elif "def" in col_lower and "rtg" in col_lower:
        rename_map[col] = "DefRtg"
    elif "net" in col_lower:
        rename_map[col] = "NetRtg"
    elif "pts" in col_lower and "opp" not in col_lower:
        rename_map[col] = "PTS"
    elif "opp" in col_lower and "pts" in col_lower:
        rename_map[col] = "OPP PTS"

df = df.rename(columns=rename_map)

# keep only the columns that exist
valid_cols = [c for c in ["Team", "OffRtg", "DefRtg", "NetRtg", "PTS", "OPP PTS"] if c in df.columns]
df = df[valid_cols]

# ---- STEP 3: compute Power Rating ----
if "OffRtg" in df.columns and "DefRtg" in df.columns:
    df["Power"] = (df["OffRtg"] - df["DefRtg"]).round(2)
else:
    df["Power"] = 0  # fallback if ratings missing

# ---- STEP 4: format results ----
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
lines = [f"NBA Team Ratings – {timestamp}", ""]
for _, row in df.iterrows():
    team = row.get("Team", "Unknown")
    off = row.get("OffRtg", "N/A")
    deff = row.get("DefRtg", "N/A")
    power = row.get("Power", "N/A")
    lines.append(f"{team}: OffRtg {off}, DefRtg {deff}, Power {power}")

content = "\n".join(lines)

# ---- STEP 5: save results ----
with open(log_file, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Model pulled from NBA Stuffer and saved to logs/latest_results.txt")

# ---- STEP 6: email results ----
SMTP_USER = os.getenv("GMAIL_USER")
SMTP_PASS = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO  = os.getenv("EMAIL_TO")

if SMTP_USER and SMTP_PASS and EMAIL_TO:
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"NBA Model Results – {timestamp}"
    msg.set_content(content)

    with open(log_file, "rb") as fp:
        msg.add_attachment(fp.read(), maintype="text", subtype="plain", filename="latest_results.txt")

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)
    print("📧 Email sent successfully.")
else:
    print("ℹ️ Email secrets missing – skipped email.")
