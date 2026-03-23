# 🌿 GartenAI: Next-Gen Micro-Climate Forecasting for Gardening

**GartenAI** is an advanced, AI-powered gardening assistant that uses **Hybrid State Space Models (SSM) and Transformers** to predict highly localized weather patterns. It combines global API data with your local DIY sensor readings (Soil Moisture, Temp, Hum) to provide actionable gardening intelligence.

---

## 🔥 Key Features

- **🚀 Hybrid AI Model:** A state-of-the-art SSM + Transformer architecture for 7-day high-precision temporal forecasting.
- **📡 Local Data Fusion:** Seamlessly integrates with Raspberry Pi and Arduino sensors to override general weather data with your specific garden's conditions.
- **💧 Smart Irrigation Logic:** Dynamically calculates **Vapor Pressure Deficit (VPD)** to tell you exactly when your plants are stressed.
- **🤖 Plant Expert Advisor:** Provides localized recommendations based on your **Country**, **Current Season**, and **Plant Species** (e.g., Tropical vs. Desert plants).
- **📱 SMS Alerts:** Automated notifications sent directly to your phone when soil moisture drops below critical levels (requires Twilio).
- **📊 7-Day Forecast:** Expanded visualization for long-term planning (Pruning, Planting, Fertilizing).

---

## 🛠️ Personal Setup Guide

### 1. Prerequisites
- **Python 3.9+**
- **OpenWeatherMap API Key** (Get a free one at [openweathermap.org](https://openweathermap.org/api))
- *(Optional)* **Twilio Account** for SMS notifications.

### 2. Installation
```powershell
# Clone or create the directory
cd "Micro-Climate Forecast for Gardening"

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration (`.env`)
Create/Edit the `.env` file in the root directory:
```env
OPENWEATHER_API_KEY=YOUR_KEY_HERE
TWILIO_SID=YOUR_TWILIO_SID
TWILIO_AUTH_TOKEN=YOUR_TWILIO_TOKEN
TWILIO_PHONE_FROM=+123456789
USER_PHONE_TO=+123456789
```

### 4. Hardware Integration (DIY)
To use real sensors, connect a **Capacitive Soil Moisture Sensor** and a **DHT22** to your Raspberry Pi/ESP32. Use the provided `utils/sensor_driver.py` logic to POST data to:
`http://your-server-ip:5000/api/sensor`

---

## 🚀 Running the App

1. **Start the AI Backend:**
   ```powershell
   python app.py
   ```
2. **Access the Dashboard:**
   Open `http://localhost:5000` in your browser.
3. **(Optional) Run Sensor Simulator:**
   ```powershell
   python utils/sensor_driver.py
   ```

---

## 📂 Project Structure
- `app.py`: The heart of the Flask server.
- `model/`: The PyTorch AI architecture (SSM + Transformer).
- `static/`: Premium Glassmorphism UI (CSS/JS).
- `utils/`: Specialized modules for APIs, Preprocessing, and Alerts.

---

## 📜 Personalization Suggestions
- **For Indoor Gardening:** Adjust the VPD thresholds in `model/predictor.py` for humidity-loving ferns.
- **For Farming:** Extend the data ingestion to include **Wind Speed** for crop dusting or pesticide application planning.
- **For Seasonal Trends:** Train the model on your local `history.csv` after 6 months of data collection for hyper-local performance.

---
*Built with ❤️ for Modern Gardeners.*
