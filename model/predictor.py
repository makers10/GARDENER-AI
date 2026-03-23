import torch
import numpy as np
import pandas as pd
from model.architecture import HybridSSMTransformer

class Predictor:
    def __init__(self, model_path="model/weights.pth", device="cpu"):
        self.device = device
        self.model = HybridSSMTransformer(input_dim=8).to(self.device)
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=device))
            self.model.eval()
        except FileNotFoundError:
            print(f"Warning: Model weight file not found at {model_path}. Please train the model first.")
    
    def get_recommendation(self, forecast_df):
        """Rule-based gardening assistant recommendations."""
        recommendations = []
        
        # Calculate key metrics from tomorrow's forecast (next 24h)
        avg_temp = forecast_df['temp'].mean()
        max_rain = forecast_df['rain_prob'].max()
        avg_vpd = forecast_df['vpd'].mean()
        
        # 1. Watering Logic
        if max_rain > 0.6:
            recommendations.append({
                "type": "watering", 
                "status": "Skip Watering", 
                "impact": "Low", 
                "msg": "Heavy rain expected tomorrow. Nature will do the work for you."
            })
        elif avg_temp > 28:
            recommendations.append({
                "type": "watering", 
                "status": "Daily Morning", 
                "impact": "Critical", 
                "msg": "High temperatures forecasted. Water deeply in the early morning to minimize evaporation."
            })
        else:
            recommendations.append({
                "type": "watering", 
                "status": "As Needed", 
                "impact": "Normal", 
                "msg": "Optimal weather conditions. Check soil moisture before watering."
            })
            
        # 2. Fertilizing Logic
        if avg_temp < 15:
            recommendations.append({
                "type": "fertilizing", 
                "status": "Delay", 
                "impact": "Low", 
                "msg": "Temps are too low for optimal nutrient uptake. Wait for a warmer window."
            })
        elif 0.1 < max_rain < 0.3:
            recommendations.append({
                "type": "fertilizing", 
                "status": "Great Timing", 
                "impact": "High", 
                "msg": "Light rain expected. Perfect for washing granular fertilizer into the root zone."
            })
        
        return recommendations

    def predict(self, input_data):
        """Run model inference on preprocessed sequences (Past 24H -> Next 24H)."""
        input_tensor = torch.FloatTensor(input_data).unsqueeze(0).to(self.device) # Add batch dim
        with torch.no_grad():
            output = self.model(input_tensor)
            
        # Output is [Batch, 24, 3] -> (Temp, Humid, RainProb)
        output = output.squeeze(0).cpu().numpy()
        
        # Calculate derived VPD for's forecast
        # (Using a simple vector calculation for speed)
        vpsat = 0.611 * np.exp((17.27 * output[:, 0]) / (output[:, 0] + 237.3))
        vpair = vpsat * (output[:, 1] / 100.0)
        vpd = vpsat - vpair
        
        forecast_df = pd.DataFrame(output, columns=['temp', 'humidity', 'rain_prob'])
        forecast_df['vpd'] = vpd
        
        return forecast_df

if __name__ == "__main__":
    predictor = Predictor()
    # Test with random past 24h data
    dummy_past = np.random.randn(24, 8) 
    forecast = predictor.predict(dummy_past)
    recs = predictor.get_recommendation(forecast)
    print("Forecast Preds (First 3h):\n", forecast.head(3))
    print("Recs:", recs)
