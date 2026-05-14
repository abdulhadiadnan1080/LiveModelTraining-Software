import pandas as pd
import numpy as np
import os
import joblib
from sklearn.linear_model import LinearRegression

def train_linear_regression():
    train_path = 'data/train.csv'
    if not os.path.exists(train_path):
        print(f"Error: {train_path} not found. Please run the split step first.")
        return None
    
    print(f"🧠 Loading training data from {train_path}...")
    df = pd.read_csv(train_path)
    
    target_col = 'Price (in rupees)'
    if target_col not in df.columns:
        print(f"Error: Target column '{target_col}' not found in training data.")
        return None
        
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print(f"Training Linear Regression model on {len(X)} samples with {len(X.columns)} features...")
    model = LinearRegression()
    model.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    # Overwrite the same model file so the evaluate script automatically picks it up
    model_path = 'models/house_price_model.pkl'
    joblib.dump(model, model_path)
    print(f"✅ Linear Regression Model trained successfully and saved to {model_path}")
    
    return {'model_type': 'Linear Regression', 'train_samples': len(X)}

if __name__ == "__main__":
    train_linear_regression()
