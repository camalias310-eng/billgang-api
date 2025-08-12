from flask import Flask, request, jsonify
import json
import os
import shutil
import requests  # make sure requests is installed

# Ensure credentials file is in persistent storage
source_file = "credentials.txt"
dest_file = "/data/credentials.txt"

if not os.path.exists(dest_file) and os.path.exists(source_file):
    shutil.copy(source_file, dest_file)
    print("✅ Copied credentials.txt to /data")

app = Flask(__name__)

CREDENTIALS_FILE = "/data/credentials.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403925009810067547/SOp0rF8tZh6_Ba8tuPYLdDrZngMdo3jRxLDuBUCBIvCUQO5wSZDkTBQqca14skw8tO1K"  # replace with your actual webhook

# -------------------------
# API endpoint (Billgang webhook)
# -------------------------
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
        lines = f.readlines()

    stock_count = len(lines)

    if stock_count == 0:
        return jsonify({
            "delivery": "Sold out — no more credentials available",
            "success": False,
            "stock": 0
        })

    # Get first credential
    first_line = lines[0].strip()
    with open(CREDENTIALS_FILE, "w") as f:
        f.writelines(lines[1:])

    # Send Discord notification
    message = f"🎉 New Sale! Customer: {customer_email}\nDelivered: `{first_line}`\nStock left: {stock_count - 1}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    return jsonify({
        "delivery": f"Email: {first_line}",
        "success": True,
        "stock": stock_count - 1
    })

# -------------------------
# Thank You Page route
# -------------------------
@app.route('/thankyou', methods=['GET'])
def thank_you_page():
    if not os.path.exists(CREDENTIALS_FILE):
        return "<h2>Sorry, we’re out of stock!</h2>"

    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return "<h2>Sorry, we’re out of stock!</h2>"

    # Get first credential
    first_line = lines[0].strip()
    with open(CREDENTIALS_FILE, "w") as f:
        f.writelines(lines[1:])

    # Split into email & password
    if "," in first_line:
        email, password = first_line.split(",", 1)
    else:
        email = first_line
        password = "(no password found)"

    # Send Discord notification
    message = f"🎉 New Sale via Thank You page!\nDelivered: `{first_line}`\nStock left: {len(lines) - 1}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    # HTML thank you page
    return f"""
    <html>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🎉 Thanks for your order!</h1>
        <p>Here are your login details:</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Password:</strong> {password}</p>
        <p><em>Make sure to save these details securely.</em></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
