from flask import Flask, request
import datetime
import json
import psycopg2

connection = psycopg2.connect(database="WeatherApp", host="localhost", port=5432)
cursor = connection.cursor()

app = Flask(__name__)

@app.route("/ingest", methods=['POST'])
def ingest():
    received_at = datetime.datetime.now().astimezone().isoformat()
    data = request.json
    retMessage = {"status": "ok", "status_message": "Data succesfully recorded","timestamp": received_at}
    try:
        cursor.execute("""
            INSERT INTO weather_readings (station_id, measured_at, received_at, temperature_c, humidity_pct, pressure_hpa)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (data['station_id'], data['timestamp'], received_at, data['temperature_c'], data['humidity_pct'], data['press_hpa']
        ))
    except KeyError:
        retMessage["status"] = "nok"
        retMessage["status_message"] = "Invalid JSON format"
        return retMessage, 400
    except:
        retMessage["status"] = "nok"
        retMessage["status_message"] = "Unexpected error"
        return retMessage, 500
    return retMessage, 201

@app.route("/latest")
def latest():
    cursor.execute("SELECT * FROM weather_readings WHERE id=(SELECT max(id) FROM weather_readings);")
    data = cursor.fetchone()
    if data == None:
        return "No data has yet been ingested", 503
    retData = {
        "station_id": data[1],
        "measured_at": data[2],
        "received_at": data[3],
        "temperature_c": data[4],
        "humidity_pct": data[5],
        "pressure_hpa": data[6]
    }
    return retData, 200

@app.route("/range", methods=['GET'])
def range():
    return "[Requested range weather data here]"
