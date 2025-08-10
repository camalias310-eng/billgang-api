from flask import Flask, request, jsonify
import os

app = Flask(__name__)

CREDENTIALS_FILE = "credentials.txt"

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

    return jsonify({
        "delivery": f"Email: {first_line}",
        "success": True,
        "stock": stock_count - 1
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
