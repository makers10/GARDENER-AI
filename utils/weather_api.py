import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, lat, lon):
        """Fetch current weather for a specific location."""
        url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching current weather: {response.status_code}")
            return None

    def get_hourly_forecast(self, lat, lon):
        """Fetch 48-hour hourly forecast (Note: Requires One Call API 3.0)."""
        # Note: OpenWeatherMap One Call 3.0 requires a subscription (often with a free tier)
        one_call_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,daily,alerts&appid={self.api_key}&units=metric"
        response = requests.get(one_call_url)
        if response.status_code == 200:
            return response.json()['hourly']
        else:
            # Fallback to standard 5-day/3-hour forecast if One Call is not available
            print(f"Switching to 5-day/3-hour forecast fallback...")
            url = f"{self.base_url}/forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()['list']
            return None

    def get_7day_forecast(self, lat, lon):
        """Fetch 7-day daily forecast trend."""
        # Using One Call API 3.0 for 7-day daily forecast
        one_call_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={self.api_key}&units=metric"
        response = requests.get(one_call_url)
        if response.status_code == 200:
            return response.json()['daily']
        else:
            # Fallback for standard API: Return 5-day 3-hour forecast chunks formatted as days
            url = f"{self.base_url}/forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()['list']
                # Aggregate 3hr chunks into daily averages
                daily_agg = []
                for i in range(0, len(data), 8): # 8 * 3h = 24h
                    chunk = data[i:i+8]
                    if len(chunk) < 4: continue
                    day_data = {
                        "dt": chunk[0]['dt'],
                        "temp": {"day": sum(c['main']['temp'] for c in chunk)/len(chunk)},
                        "humidity": sum(c['main']['humidity'] for c in chunk)/len(chunk),
                        "rain": sum(c.get('rain', {}).get('3h', 0) for c in chunk),
                        "description": chunk[0]['weather'][0]['description']
                    }
                    daily_agg.append(day_data)
                return daily_agg
            return None

    def process_forecast_data(self, raw_data):
        """Convert raw JSON forecast into a structured Pandas DataFrame."""
        if not raw_data:
            return None
        
        forecast_list = []
        for entry in raw_data:
            # Handle differences between One Call Hourly and Standard Forecast structures
            main = entry.get('main', entry)
            weather = entry.get('weather', [{}])[0]
            
            data = {
                'timestamp': entry.get('dt'),
                'datetime': datetime.fromtimestamp(entry.get('dt')),
                'temp': main.get('temp'),
                'humidity': main.get('humidity'),
                'pressure': main.get('pressure'),
                'rain': entry.get('rain', {}).get('1h', 0) if 'rain' in entry else 0,
                'clouds': entry.get('clouds', {}).get('all', 0)
            }
            forecast_list.append(data)
            
        return pd.DataFrame(forecast_list)

if __name__ == "__main__":
    # Test (with a placeholder key)
    api = WeatherAPI()
    # Sample Lat/Lon (e.g., London)
    # print(api.get_current_weather(51.5074, -0.1278))
