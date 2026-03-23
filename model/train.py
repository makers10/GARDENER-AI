import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from model.architecture import HybridSSMTransformer

class Trainer:
    def __init__(self, input_dim=8, d_model=64, seq_len_out=24):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = HybridSSMTransformer(input_dim=input_dim, d_model=d_model, seq_len_out=seq_len_out).to(self.device)
        self.criterion_reg = nn.MSELoss()
        self.criterion_class = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def generate_synthetic_data(self, samples=1000, seq_length=48):
        """Generate realistic weather data (Temp, Humid, Rain, VPD, Sin/Cos time)."""
        data = []
        for i in range(samples):
            # 24h cycle
            t = np.linspace(0, 2 * np.pi, seq_length)
            temp = 20 + 5 * np.sin(t) + np.random.normal(0, 0.5, seq_length)
            humid = 60 + 10 * np.cos(t) + np.random.normal(0, 0.5, seq_length)
            rain = (np.random.rand(seq_length) > 0.8).astype(float) # 20% rain chance
            vpd = 1.0 + 0.5 * np.sin(t)
            hr_sin, hr_cos = np.sin(t), np.cos(t)
            day_sin, day_cos = np.sin(t/365), np.cos(t/365)
            
            sequence = np.stack([temp, humid, rain, vpd, hr_sin, hr_cos, day_sin, day_cos], axis=-1)
            data.append(sequence)
            
        return np.array(data)

    def train(self, data, epochs=10, batch_size=32):
        print(f"Starting training on {self.device}...")
        self.model.train()
        
        # Simple train/val split (80/20)
        train_size = int(0.8 * len(data))
        train_data = data[:train_size]
        
        for epoch in range(epochs):
            total_loss = 0
            for i in range(0, len(train_data), batch_size):
                batch = train_data[i:i+batch_size]
                if len(batch) < batch_size: continue
                
                # Input: past 24h -> Target: next 24h
                x = torch.FloatTensor(batch[:, :24, :]).to(self.device)
                y_true = torch.FloatTensor(batch[:, 24:48, :3]).to(self.device) # Only Temp, Humid, Rain
                
                self.optimizer.zero_grad()
                y_pred = self.model(x)
                
                # Regression Loss (Mean squared error for Temp/Humid)
                loss_reg = self.criterion_reg(y_pred[:, :, :2], y_true[:, :, :2])
                
                # Classification Loss (BCE for Rain probability)
                loss_class = self.criterion_class(y_pred[:, :, 2], y_true[:, :, 2])
                
                loss = loss_reg + loss_class
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
            
            print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/(len(train_data)//batch_size):.4f}")
        
        # Save model
        torch.save(self.model.state_dict(), "model/weights.pth")
        print("Model saved to model/weights.pth")

if __name__ == "__main__":
    trainer = Trainer()
    synth_data = trainer.generate_synthetic_data()
    trainer.train(synth_data, epochs=5)
