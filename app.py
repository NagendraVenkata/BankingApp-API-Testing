from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory "database" of users
users = {
    "user1": {"password": "pass123", "balance": 1000.0},
    "user2": {"password": "pass456", "balance": 500.0},
}

# Simple token storage (token: username)
tokens = {}

def authenticate(token):
    """Return user dict if token is valid, else None."""
    username = tokens.get(token)
    if username:
        return users.get(username)
    return None

@app.route("/", methods=["GET"])
def home():
    return "<h2>Welcome to Banking API</h2><p>Use /login, /balance, /transaction endpoints.</p>"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = users.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    # Create a simple token (insecure, for demo only)
    token = f"token-{username}"
    tokens[token] = username

    return jsonify({"token": token})

@app.route("/balance", methods=["GET"])
def balance():
    token = request.headers.get("Authorization")
    user = authenticate(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"balance": user["balance"]})

@app.route("/transaction", methods=["POST"])
def transaction():
    token = request.headers.get("Authorization")
    user = authenticate(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    amount = data.get("amount")

    if amount is None:
        return jsonify({"error": "Amount is required"}), 400

    if not isinstance(amount, (int, float)):
        return jsonify({"error": "Amount must be a number"}), 400

    # Prevent overdraft
    if user["balance"] + amount < 0:
        return jsonify({"error": "Overdraft not allowed"}), 400

    user["balance"] += amount
    return jsonify({"balance": user["balance"]})

if __name__ == "__main__":
    app.run(debug=True)
