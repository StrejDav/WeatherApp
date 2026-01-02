from flask import Flask, request
import datetime
import json

app = Flask(__name__)

@app.route("/ingest", methods=['POST'])
def ingest():
    if request.method == 'POST':
        data = request.json
        retMessage = {"status": "ok", "timestamp": datetime.datetime.now().astimezone().isoformat()}
        return retMessage, 200

@app.route("/latest")
def latest():
    return "[Latest weather data here]"

@app.route("/range", methods=['GET'])
def range():
    return "[Requested range weather data here]"
    