import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


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
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
        "input": {
            "image": f"data:image/png;base64,{image_base64}"
        }
    }

    # Create prediction
    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        json=payload
    )

    if response.status_code != 201:
        return jsonify({
            "error": "Failed to create prediction",
            "status_code": response.status_code,
            "replicate_response": response.text
        }), 500

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    # Poll until complete
    while True:
        poll = requests.get(prediction_url, headers=headers).json()
        status = poll.get("status")

        if status == "succeeded":
            return jsonify({"output": poll["output"][0]})

        if status == "failed":
            return jsonify({"error": "Background removal failed"}), 500
