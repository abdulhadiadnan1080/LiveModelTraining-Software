import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestRegressor

def train_random_forest():
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
    
    print(f"Training RandomForestRegressor on {len(X)} samples with {len(X.columns)} features...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    model_path = 'models/house_price_model.pkl'
    joblib.dump(model, model_path)
    print(f"✅ Random Forest Model trained successfully and saved to {model_path}")
    
    return {'model_type': 'Random Forest', 'train_samples': len(X)}

if __name__ == "__main__":
    train_random_forest()
