import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Backend working successfully!"

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    return jsonify({"status": "route exists"})

