from flask import Flask, request, jsonify
import os

app = Flask(__name__)

CLIENT_KEY = os.getenv("CLIENT_KEY")  # optional

def verify_client_key():
    if CLIENT_KEY is None:
        return True
    client_key = request.headers.get("x-client-key")
    if not client_key or client_key != CLIENT_KEY:
        return False
    return True


@app.route("/")
def home():
    return "Server running"


@app.route("/download", methods=["POST"])
def download():
    if not verify_client_key():
        return jsonify({"error": "Invalid client key"}), 401

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

