from flask import Flask, request, jsonify
import json
import os
import shutil  # <-- new

# Ensure credentials file is in persistent storage
source_file = "credentials.txt"
dest_file = "/data/credentials.txt"

# Only copy if it doesn't already exist in /data
if not os.path.exists(dest_file) and os.path.exists(source_file):
    shutil.copy(source_file, dest_file)
    print("✅ Copied credentials.txt to /data")
    
app = Flask(__name__)

CREDENTIALS_FILE = "/data/credentials.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403925009810067547/SOp0rF8tZh6_Ba8tuPYLdDrZngMdo3jRxLDuBUCBIvCUQO5wSZDkTBQqca14skw8tO1K"  # paste your Discord webhook here

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

    # Get the first line (email + password)
    first_line = lines[0].strip()

    # Save remaining lines back to the file
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




