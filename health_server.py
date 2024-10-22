# health_server.py

from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/")
def health_check():
    return jsonify({"status": "healthy"}), 200


def run():
    port = int(os.getenv("PORT", 80))
    app.run(host="0.0.0.0", port=port)
