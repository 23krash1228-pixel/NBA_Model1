# ----------------------------
# NBA Auto Model – NBA Stuffer Version
# ----------------------------
import os
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from datetime import datetime

# ---- setup folders ----
os.makedirs("logs", exist_ok=True)
log_file = "logs/latest_results.txt"

# ---- STEP 1: pull latest stats table from nbastuffer.com ----
url = "https://www.nbastuffer.com/2025-2026/"
tables = pd.read_html(url)
df = tables[0]   # first table on the page

# ---- STEP 2: pick key columns ----
df = df[["Team", "OffRtg", "DefRtg", "NetRtg", "PTS", "OPP PTS"]]

# ---- STEP 3: compute custom “power” rating ----
df["Power"] = (df["OffRtg"] - df["DefRtg"]).round(2)

# ---- STEP 4: format the output ----
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
lines = [f"NBA Team Ratings – {timestamp}", ""]
for _, row in df.iterrows():
    line = f"{row['Team']}: OffRtg {row['OffRtg']}, DefRtg {row['DefRtg']}, Power {row['Power']}"
    lines.append(line)

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
    print("ℹ️ Email secrets missing, skipped email.")
