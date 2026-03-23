import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

class DataUtils:
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    @staticmethod
    def calculate_vpd(temp, rh):
        """Calculate Vapor Pressure Deficit (VPD) in kPa."""
        # Saturation Vapor Pressure (VPsat)
        vpsat = 0.611 * np.exp((17.27 * temp) / (temp + 237.3))
        # Actual Vapor Pressure (VPair)
        vpair = vpsat * (rh / 100.0)
        # Vapor Pressure Deficit (VPD)
        return vpsat - vpair

    @staticmethod
    def encode_time(dt_object):
        """Cyclical encoding of hour and day-of-year features (Sin/Cos)."""
        hour = dt_object.hour
        day_of_year = dt_object.timetuple().tm_yday
        
        # Hour encoding (24h cycle)
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        
        # Day of year encoding (365.25 cycle)
        day_sin = np.sin(2 * np.pi * day_of_year / 365.25)
        day_cos = np.cos(2 * np.pi * day_of_year / 365.25)
        
        return hour_sin, hour_cos, day_sin, day_cos

    def preprocess_forecast(self, df):
        """Full preprocessing pipeline for incoming forecast DataFrames."""
        if df is None or len(df) == 0:
            return None
        
        # Ensure we have datetime objects
        if not isinstance(df['datetime'].iloc[0], datetime):
            df['datetime'] = pd.to_datetime(df['datetime'])
            
        # 1. Feature Engineering
        df['vpd'] = df.apply(lambda x: self.calculate_vpd(x['temp'], x['humidity']), axis=1)
        
        # 2. Temporal Encoding
        time_features = df['datetime'].apply(self.encode_time)
        df[['hr_sin', 'hr_cos', 'day_sin', 'day_cos']] = pd.DataFrame(time_features.tolist(), index=df.index)
        
        # 3. Handle missing values
        df = df.interpolate(method='linear').fillna(method='ffill').fillna(method='bfill')
        
        return df

    def create_sequences(self, data, seq_length_in=24, seq_length_out=24):
        """Generate windowed sequences for sliding-window forecasting."""
        x, y = [], []
        # Target columns: Temp, Humidity, Rain Probability
        for i in range(len(data) - seq_length_in - seq_length_out + 1):
            x.append(data[i:(i + seq_length_in)])
            y.append(data[(i + seq_length_in):(i + seq_length_in + seq_length_out)])
        return np.array(x), np.array(y)

if __name__ == "__main__":
    # Unit tests can be added here
    utils = DataUtils()
    print("VPD (25C, 60% RH):", utils.calculate_vpd(25, 60), "kPa")
