
WeatherApp is a small personal project written mainly for educational purposes. It works with WeatherStation, which is an embedded software written for ESP32, but the API is well-defined, so it can work with anything that respects the API. 
Messages are sent through POST HTTP requests to `/ingest` endpoint. The entries can be read with requests to `/latest` and `/range` endpoints.
The app is written in Python using Flask for server hosting. Included are dockerfile and terraform configuration for AWS. For the database PostgreSQL is used.
# Architecture

## Data fields
- `temperature_c` - temperature in Celsius
- `humidity_pct` - humidity in percentage
- `pressure_hpa` - pressure in hPa
- `timestamp` - timestamp in ISO 8601 format (UTC+01 timezone)
- `station_id` - unique ID of the station
- `version`
## Update frequency
- 5 minutes
## API endpoints
- `/ingest` - receives messages through POST method
- `/latest` - returns latest recorded data
- `/range?from=&to=` - returns all data from the given range
## Database schema
| Column          | Data type       |
| --------------- | --------------- |
| `id`            | `bigserial`     |
| `station_id`    | `text`          |
| `measured_at`   | `timestamptz`   |
| `received_at`   | `timestamptz`   |
| `temperature_c` | `numeric(3, 1)` |
| `humidity_pct`  | `numeric(3, 1)` |
| `press_hpa`     | `numeric(5, 1)` |
```sql
CREATE TABLE weather_readings (
    id            BIGSERIAL PRIMARY KEY,
    station_id    TEXT NOT NULL,

    measured_at   TIMESTAMPTZ NOT NULL,
    received_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    temperature_c NUMERIC(3, 1),
    humidity_pct  NUMERIC(3, 1),
    pressure_hpa  NUMERIC(5, 1)
);
```
# Message structure
```json
{
	"version": 1,
	"station_id": "outside-01",
	"timestamp": "2026-01-01T17:45:53+01",
	"payload":
	{
		"temperature_c": 20.0,
		"humidity_pct": 62.0,
		"press_hpa": 1012.0
	}
}
```