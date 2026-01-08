from flask import Flask, request
import datetime
import json
import psycopg2
import os
import time
from dateutil import parser

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": os.environ["DB_PORT"],
    "database": os.environ["DB_DATABASE"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"]
}

for i in range(10):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    raise RuntimeError("Database is not available")

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_readings (
        id            BIGSERIAL PRIMARY KEY,
        station_id    TEXT NOT NULL,

        measured_at   TIMESTAMPTZ NOT NULL,
        received_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

        temperature_c NUMERIC(3, 1),
        humidity_pct  NUMERIC(3, 1),
        pressure_hpa  NUMERIC(5, 1)
    );
""")
connection.commit()

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
    from_ts = request.args.get("from")
    to_ts = request.args.get("to")

    if not from_ts or not to_ts:
        return {
            "error": "Both 'from' and 'to' query parameters are required"
        }, 400

    try:
        # Parse ISO 8601 timestamps with timezone
        from_dt = parser.isoparse(from_ts)
        to_dt = parser.isoparse(to_ts)
    except (ValueError, TypeError):
        return {
            "error": "Invalid timestamp format. Use ISO 8601 with timezone."
        }, 400

    if from_dt >= to_dt:
        return {
            "error": "'from' must be earlier than 'to'"
        }, 400

    cursor.execute(
        """
        SELECT
            station_id,
            measured_at,
            received_at,
            temperature_c,
            humidity_pct,
            pressure_hpa
        FROM weather_readings
        WHERE measured_at >= %s
          AND measured_at <= %s
        ORDER BY measured_at ASC;
        """,
        (from_dt, to_dt)
    )

    rows = cursor.fetchall()

    if not rows:
        return {
            "data": [],
            "count": 0
        }, 200

    result = []
    for row in rows:
        result.append({
            "station_id": row[0],
            "measured_at": row[1].isoformat(),
            "received_at": row[2].isoformat(),
            "temperature_c": float(row[3]) if row[3] is not None else None,
            "humidity_pct": float(row[4]) if row[4] is not None else None,
            "pressure_hpa": float(row[5]) if row[5] is not None else None,
        })

    return {
        "count": len(result),
        "data": result
    }, 200
