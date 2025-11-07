import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read secrets from GitHub Actions environment
gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
email_to = os.getenv("EMAIL_TO")

if not gmail_user or not gmail_pass or not email_to:
    print("⚠️ Email secrets missing – skipped email.")
    exit(0)

# Read the latest results file
results_file = "logs/latest_results.txt"
if not os.path.exists(results_file):
    print("⚠️ No results file found – skipping email.")
    exit(0)

with open(results_file, "r") as f:
    results_content = f.read()

# Build email
msg = MIMEMultipart()
msg["From"] = gmail_user
msg["To"] = email_to
msg["Subject"] = "NBA Model Results Update"
msg.attach(MIMEText(results_content, "plain"))

# Send via Gmail
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
    print("✅ Email sent successfully to:", email_to)
except Exception as e:
    print("❌ Email sending failed:", e)
