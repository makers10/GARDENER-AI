import requests
import time
import random
import argparse

class SensorSimulator:
    def __init__(self, endpoint="http://127.0.0.1:5000/api/sensor"):
        self.endpoint = endpoint
        
    def read_dht22(self):
        """Simulate DHT22 Temperature and Humidity sensor."""
        # Realistic garden ambient temp range: 18-28.5C
        return round(random.uniform(18.0, 28.5), 1), round(random.uniform(45.0, 75.0), 1)

    def read_soil_moisture(self):
        """Simulate Capacitive Soil Moisture Sensor."""
        # 0% = Dry, 60%+ = Wet
        return round(random.uniform(10.0, 95.0), 1)

    def run(self, interval=5):
        print(f"📡 Sensor Simulator Started (Interval: {interval}s)")
        print(f"📡 Sending data to: {self.endpoint}")
        
        try:
            while True:
                temp, humid = self.read_dht22()
                soil = self.read_soil_moisture()
                
                payload = {
                    "temp": temp,
                    "humidity": humid,
                    "soil_moisture": soil
                }
                
                try:
                    r = requests.post(self.endpoint, json=payload, timeout=5)
                    if r.status_code == 200:
                        print(f"✅ [SUCCESS] Temp: {temp}C | Humidity: {humid}% | Soil: {soil}%")
                    else:
                        print(f"❌ [API ERROR] Server response: {r.status_code}")
                except requests.exceptions.ConnectionError:
                    print("❌ [SERVER DOWN] Backend is not running. Please start app.py first.")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Simulator Stopped by User.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate local gardening sensors (Soil/Temp/Hum).")
    parser.add_argument("--interval", type=int, default=5, help="Simulation interval (seconds)")
    args = parser.parse_args()
    
    sim = SensorSimulator()
    sim.run(interval=args.interval)
