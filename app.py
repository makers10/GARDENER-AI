import os
import random
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.weather_api import WeatherAPI
from utils.data_utils import DataUtils
from utils.plant_advisor import PlantAdvisor
from utils.alert_system import AlertSystem
from model.predictor import Predictor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize modules
weather_service = WeatherAPI()
data_utils = DataUtils()
plant_advisor = PlantAdvisor()
alert_system = AlertSystem()
# Initialize predictor with synthetic data weights if training is not yet fully complete
predictor = Predictor(model_path="model/weights.pth")

# Global storage for local sensor data (In-memory for now)
local_sensor_storage = {
    "temp": None,
    "humidity": None,
    "soil_moisture": None,
    "last_updated": None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/forecast', methods=['GET'])
def get_dashboard_data():
    """
    Main endpoint for dashboard functionality.
    """
    is_test = request.args.get('test', 'false').lower() == 'true'
    lat = request.args.get('lat', '51.5074')
    lon = request.args.get('lon', '-0.1278')
    
    if is_test:
        # --- RETURN SYNTHETIC TEST DATA ---
        timestamps = [(datetime.now() + timedelta(hours=i)).strftime('%H:00') for i in range(24)]
        t = np.linspace(0, 2 * np.pi, 24)
        mock_temp = (22 + 5 * np.sin(t) + np.random.normal(0, 0.2, 24)).tolist()
        mock_humid = (55 + 10 * np.cos(t) + np.random.normal(0, 0.2, 24)).tolist()
        mock_rain = [round(random.uniform(0, 0.2), 2) for _ in range(24)]
        mock_rain[10] = 0.85 # Artificial rain event
        
        response = {
            "is_test": True,
            "current": {"temp": 22.4, "humidity": 62, "rain": 0, "vpd": 0.85, "wind": 4.2, "desc": "Simulated Clear Sky"},
            "local_sensor": local_sensor_storage,
            "recommendations": [{"type": "watering", "status": "Test Mode Active", "impact": "Normal", "msg": "You are viewing simulated data for testing purposes."}],
            "forecast": {"times": timestamps, "temp": mock_temp, "humidity": mock_humid, "rain_prob": mock_rain},
            "daily_trend": [{"dt": datetime.now().timestamp(), "temp": {"day": 21}, "humidity": 60, "rain": 0, "description": "Partly Cloudy"}] * 7
        }
        return jsonify(response)
    
    # --- REAL DATA PATH ---
    raw_forecast = weather_service.get_hourly_forecast(lat, lon)
    if not raw_forecast:
        return jsonify({"error": "Failed to fetch weather data. Check your API key. Showing synthetic data instead for demo."}), 503
    
    # 2. Convert to DataFrame
    df = weather_service.process_forecast_data(raw_forecast)
    processed_df = data_utils.preprocess_forecast(df)
    
    # 3. Model Context Sequence Preparation (Take last 24 available entries as "past")
    # For a real scenario, we'd take history. Here we use the context from the forecast entries.
    subset = processed_df[['temp', 'humidity', 'rain', 'vpd', 'hr_sin', 'hr_cos', 'day_sin', 'day_cos']].tail(24)
    past_24h_data = subset.values
    
    # Pad to 24 if short
    if len(past_24h_data) < 24:
        past_24h_data = np.pad(past_24h_data, ((24 - len(past_24h_data), 0), (0, 0)), mode='constant')
        
    # 4. Predict next 24h
    model_output = predictor.predict(past_24h_data)
    
    # 5. Generate Recommendations
    recommendations = predictor.get_recommendation(model_output)
    
    # 6. Format Current Weather Status
    current = weather_service.get_current_weather(lat, lon)
    if current:
        current_status = {
            "temp": current['main']['temp'],
            "humidity": current['main']['humidity'],
            "rain": current.get('rain', {}).get('1h', 0) if 'rain' in current else 0,
            "vpd": round(data_utils.calculate_vpd(current['main']['temp'], current['main']['humidity']), 2),
            "wind": current['wind']['speed'],
            "desc": current['weather'][0]['description']
        }
    else:
        current_status = None
    
    # 7. Prepare response (Chart.js ready)
    timestamps = [(datetime.now() + timedelta(hours=i)).strftime('%H:00') for i in range(24)]
    
    # 8. Fetch 7-day trend (New)
    daily_forecast = weather_service.get_7day_forecast(lat, lon)
    
    response = {
        "current": current_status,
        "local_sensor": local_sensor_storage,
        "recommendations": recommendations,
        "forecast": {
            "times": timestamps,
            "temp": model_output['temp'].tolist(),
            "humidity": model_output['humidity'].tolist(),
            "rain_prob": model_output['rain_prob'].tolist()
        },
        "daily_trend": daily_forecast
    }
    
    return jsonify(response)

@app.route('/api/plant-advice', methods=['GET'])
def get_plant_advice():
    """Get expert localized gardening advice for a specific plant."""
    plant = request.args.get('plant', 'Baseline')
    country = request.args.get('country', 'US')
    advice = plant_advisor.advise(plant_name=plant, country=country)
    return jsonify(advice)

@app.route('/api/sensor', methods=['POST'])
def update_sensor_data():
    """
    Endpoint for local sensors (Raspberry Pi/Arduino) to push data.
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    local_sensor_storage["temp"] = data.get("temp")
    local_sensor_storage["humidity"] = data.get("humidity")
    soil_moist = data.get("soil_moisture")
    local_sensor_storage["soil_moisture"] = soil_moist
    local_sensor_storage["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check for critical soil moisture (New: SMS Alerting)
    if soil_moist is not None and soil_moist < 30: # 30% Threshold
        alert_system.send_low_moisture_alert(soil_moist)
    
    return jsonify({"status": "success", "message": "Sensor data updated"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
