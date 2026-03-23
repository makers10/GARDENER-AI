import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AlertSystem:
    def __init__(self):
        self.twilio_sid = os.getenv("TWILIO_SID")
        self.twilio_token = os.getenv("TWILIO_TOKEN")
        self.from_phone = os.getenv("TWILIO_FROM")
        self.to_phone = os.getenv("USER_PHONE_TO")
        self.last_alert_time = 0
        
    def send_low_moisture_alert(self, moisture_val):
        """Send an SMS via Twilio for critically low soil moisture."""
        msg = f"⚠️ [GartenAI Alert] Your garden is thirsty! Soil moisture is critically low at {moisture_val}%. Please water your plants."
        
        # 1. Logic for real Twilio integration
        # (Requires 'pip install twilio')
        if self.twilio_sid and self.twilio_token:
            try:
                # Mocking the Twilio call without requiring the heavy library for now
                # In production, use: from twilio.rest import Client
                print(f"📱 [REAL SMS ATTEMPT] To: {self.to_phone} | Msg: {msg}")
            except Exception as e:
                print(f"❌ SMS Failed: {e}")
        
        # 2. Log to a local file for history regardless
        with open("alerts.log", "a") as f:
            f.write(f"[{os.getpid()}] {msg} | Val: {moisture_val}%\n")
            
        print(f"📧 [NOTIFICATION] Alert logged to alerts.log: {msg}")

if __name__ == "__main__":
    alerts = AlertSystem()
    alerts.send_low_moisture_alert(24.5)
