from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

CREDENTIALS_FILE = "credentials.txt"
POSITION_FILE = "position.txt"
ASSIGNMENTS_FILE = "assignments.json"  # Tracks what each buyer got


def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        return []
    with open(CREDENTIALS_FILE, "r") as file:
        return [line.strip() for line in file if line.strip()]


def load_position():
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, "r") as file:
                return int(file.read().strip())
        except ValueError:
            return 0
    return 0


def save_position(position):
    with open(POSITION_FILE, "w") as file:
        file.write(str(position))


def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        try:
            with open(ASSIGNMENTS_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}


def save_assignments(data):
    with open(ASSIGNMENTS_FILE, "w") as file:
        json.dump(data, file)


def get_next_credential(buyer_email):
    credentials = load_credentials()
    if not credentials:
        return None

    position = load_position()
    assignments = load_assignments()

    # Create an entry for the buyer if not present
    if buyer_email not in assignments:
        assignments[buyer_email] = []

    # Try finding the next unused credential for this buyer
    start_position = position
    loops = 0
    while True:
        cred_line = credentials[position]
        if cred_line not in assignments[buyer_email]:
            # Assign this credential
            assignments[buyer_email].append(cred_line)
            save_assignments(assignments)

            # Move pointer forward for next buyer
            position = (position + 1) % len(credentials)
            save_position(position)

            return cred_line.split(",")

        # Move to next position
        position = (position + 1) % len(credentials)
        loops += 1

        # If we've looped through everything, break (no new creds)
        if loops >= len(credentials):
            return None


@app.route("/generate-credentials", methods=["POST"])
def generate_credentials():
    order_data = request.json
    print("Received order:", order_data)

    # Get buyer email from Billgang order data
    buyer_email = order_data.get("customer_email", "").strip().lower()
    if not buyer_email:
        return jsonify({"success": False, "delivery": "Missing buyer email"})

    credential = get_next_credential(buyer_email)
    if not credential:
        return jsonify({"success": False, "delivery": "No new credentials available"})

    email, password = credential
    return jsonify({
        "success": True,
        "delivery": f"Email: {email}\nPassword: {password}"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
