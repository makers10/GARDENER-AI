import torch
import torch.nn as nn
import torch.nn.functional as F

class SSMLayer(nn.Module):
    """
    A simplified State Space Model (SSM) layer inspired by S4/Mamba.
    This layer captures long-range dependencies by learning an A, B, C state representation.
    """
    def __init__(self, d_model, d_state=16):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        
        # State space parameters
        self.A = nn.Parameter(torch.randn(d_state, d_state))
        self.B = nn.Parameter(torch.randn(d_model, d_state))
        self.C = nn.Parameter(torch.randn(d_state, d_model))
        
    def forward(self, x):
        # x shape: [batch, seq_len, d_model]
        batch_size, seq_len, _ = x.shape
        h = torch.zeros(batch_size, self.d_state).to(x.device)
        outputs = []
        
        for t in range(seq_len):
            # Recurrence: h_{t+1} = A*h_t + B*x_t
            # Output: y_t = C*h_t
            h = torch.tanh(torch.matmul(h, self.A) + torch.matmul(x[:, t, :], self.B))
            y = torch.matmul(h, self.C)
            outputs.append(y.unsqueeze(1))
            
        return torch.cat(outputs, dim=1) + x # Residual connection

class HybridSSMTransformer(nn.Module):
    def __init__(self, input_dim=8, d_model=64, n_heads=4, n_layers=2, output_dim=3, seq_len_out=24):
        super().__init__()
        self.seq_len_out = seq_len_out
        
        # 1. Feature projection
        self.input_projection = nn.Linear(input_dim, d_model)
        
        # 2. SSM Layer (Long-term dependency)
        self.ssm_layer = SSMLayer(d_model)
        
        # 3. Transformer Encoder (Multi-feature relationships)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=n_heads, 
            dim_feedforward=d_model*4,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # 4. Global average pooling across time dimension (or selection of latest step)
        self.fc_regression = nn.Linear(d_model, 2 * seq_len_out)     # Temp, Humidity for 24h
        self.fc_classification = nn.Linear(d_model, 1 * seq_len_out) # Rain probability for 24h
        
    def forward(self, x):
        # x shape: [batch, seq_len_in, input_dim]
        
        # Proj & SSM
        x = self.input_projection(x)
        x = self.ssm_layer(x)
        
        # Transformer
        x = self.transformer_encoder(x)
        
        # Predict based on the last sequence step
        last_step = x[:, -1, :] 
        
        # Regression: Temp/Humid predictions [Batch, 2 * seq_len_out]
        reg_out = self.fc_regression(last_step).view(-1, self.seq_len_out, 2)
        
        # Classification: Rain prob [Batch, 1 * seq_len_out]
        class_out = torch.sigmoid(self.fc_classification(last_step).view(-1, self.seq_len_out, 1))
        
        # Combined output [Batch, SeqLenOut, 3] -> (Temp, Humidity, RainProb)
        return torch.cat([reg_out, class_out], dim=-1)

if __name__ == "__main__":
    # Test model forward pass
    model = HybridSSMTransformer(input_dim=8)
    sample_input = torch.randn(2, 24, 8) # [Batch=2, Past=24h, Features=8]
    output = model(sample_input)
    print("Output Shape:", output.shape) # Expected [2, 24, 3]
