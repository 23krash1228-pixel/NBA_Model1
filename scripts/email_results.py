import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

gmail_user = os.getenv("GMAIL_USER")
gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
email_to = os.getenv("EMAIL_TO")

if not gmail_user or not gmail_pass or not email_to:
    print("⚠️ Email secrets missing – skipped email.")
    exit(0)

# 🔎 Check for error log first
error_file = "logs/error_log.txt"
results_file = "logs/latest_results.txt"

if os.path.exists(error_file):
    subject = "⚠️ NBA Model Error Alert"
    with open(error_file, "r") as f:
        content = f.read()
else:
    subject = "🏀 NBA Model Results Update"
    with open(results_file, "r") as f:
        content = f.read()

msg = MIMEMultipart()
msg["From"] = gmail_user
msg["To"] = email_to
msg["Subject"] = subject
msg.attach(MIMEText(content, "plain"))

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
    print(f"✅ Email sent successfully: {subject}")
except Exception as e:
    print("❌ Email sending failed:", e)
