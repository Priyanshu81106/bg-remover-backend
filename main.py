import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

@app.route("/")
def home():
    return "Backend working successfully!"

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    image_base64 = base64.b64encode(image.read()).decode("utf-8")

    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "cjwbw/rembg:2ad2e06c746a2b5ef6726cdd89bfcaba14d3f9bb87bc6c2024b5f47aebda211d",
        "input": {
            "image": f"data:image/png;base64,{image_base64}"
        }
    }

    # 1️⃣ Create prediction
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        json=payload,
        headers=headers
    )

    if response.status_code != 201:
        return jsonify({"error": "Failed to create prediction"}), 500

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    # 2️⃣ Poll until done
    while True:
        poll = requests.get(prediction_url, headers=headers).json()
        status = poll["status"]

        if status == "succeeded":
            return jsonify({
                "output": poll["output"][0]
            })

        if status == "failed":
            return jsonify({"error": "Background removal failed"}), 500
