from flask import Flask, request, jsonify
import os
import shutil
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ensure credentials file is in persistent storage
source_file = "credentials.txt"
dest_file = "/data/credentials.txt"

if not os.path.exists(dest_file) and os.path.exists(source_file):
    shutil.copy(source_file, dest_file)
    print("✅ Copied credentials.txt to /data")

app = Flask(__name__)

CREDENTIALS_FILE = "/data/credentials.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403925009810067547/SOp0rF8tZh6_Ba8tuPYLdDrZngMdo3jRxLDuBUCBIvCUQO5wSZDkTBQqca14skw8tO1K"

# Email sending config (replace with your real email & app password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "camalias310@gmail.com"
EMAIL_PASSWORD = "wxgmhtjpfaqqwxfd"  # Gmail app password, not normal login

def send_email(to_email, credentials):
    subject = "Your Login Details"
    body = f"Hello,\n\nHere are your login details:\n{credentials}\n\nThank you for your purchase!"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

@app.route('/generate-credentials', methods=['POST'])
def generate_credentials():
    customer_email = request.json.get('customer_email', '')

    if not os.path.exists(CREDENTIALS_FILE):
        return jsonify({
            "delivery": "No credentials file found",
            "success": False,
            "stock": 0
        })

    with open(CREDENTIALS_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    stock_count = len(lines)

    if stock_count == 0:
        return jsonify({
            "delivery": "Sold out — no more credentials available",
            "success": False,
            "stock": 0
        })

    # Get and remove the first credential
    first_credential = lines[0]
    with open(CREDENTIALS_FILE, "w") as f:
        f.write("\n".join(lines[1:]) + "\n")

    # Send Discord notification
    message = f"🎉 New Sale! Customer: {customer_email}\nDelivered: `{first_credential}`\nStock left: {stock_count - 1}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    # Send email to customer
    if customer_email:
        send_email(customer_email, first_credential)

    return jsonify({
        "delivery": first_credential,
        "success": True,
        "stock": stock_count - 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
