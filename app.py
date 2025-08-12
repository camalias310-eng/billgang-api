from flask import Flask, request, jsonify, render_template_string
import os
import shutil
import requests

# Ensure credentials file is in persistent storage
source_file = "credentials.txt"
dest_file = "/data/credentials.txt"

if not os.path.exists(dest_file) and os.path.exists(source_file):
    shutil.copy(source_file, dest_file)
    print("✅ Copied credentials.txt to /data")
    
app = Flask(__name__)

CREDENTIALS_FILE = "/data/credentials.txt"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1403925009810067547/SOp0rF8tZh6_Ba8tuPYLdDrZngMdo3jRxLDuBUCBIvCUQO5wSZDkTBQqca14skw8tO1K"

@app.route('/thankyou')
def thankyou():
    customer_email = request.args.get('email', 'Unknown buyer')

    if not os.path.exists(CREDENTIALS_FILE):
        return "No credentials available. Please contact support."

    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return "Sold out — no more credentials available."

    first_line = lines[0].strip()

    # Save remaining lines back
    with open(CREDENTIALS_FILE, "w") as f:
        f.writelines(lines[1:])

    # Notify Discord
    stock_left = len(lines) - 1
    message = f"🎉 New Sale! Customer: {customer_email}\nDelivered: `{first_line}`\nStock left: {stock_left}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    # Show HTML page to customer
    html_page = f"""
    <html>
    <head><title>Thank You</title></head>
    <body style="font-family: Arial; text-align: center; margin-top: 50px;">
        <h1>Thank You for Your Order!</h1>
        <p>Here are your login details:</p>
        <div style="background: #f4f4f4; padding: 10px; display: inline-block; border-radius: 5px;">
            <strong>{first_line}</strong>
        </div>
        <p>Stock left: {stock_left}</p>
    </body>
    </html>
    """
    return render_template_string(html_page)

# Old API endpoint remains in case you still need it
@app.route('/generate-credentials', methods=['POST'])
def generate_credentials():
    customer_email = request.json.get('customer_email', '')

    if not os.path.exists(CREDENTIALS_FILE):
        return jsonify({"delivery": "No credentials file found", "success": False, "stock": 0})

    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return jsonify({"delivery": "Sold out — no more credentials available", "success": False, "stock": 0})

    first_line = lines[0].strip()
    with open(CREDENTIALS_FILE, "w") as f:
        f.writelines(lines[1:])

    stock_left = len(lines) - 1
    message = f"🎉 New Sale! Customer: {customer_email}\nDelivered: `{first_line}`\nStock left: {stock_left}"
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

    return jsonify({"delivery": f"Email: {first_line}", "success": True, "stock": stock_left})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
