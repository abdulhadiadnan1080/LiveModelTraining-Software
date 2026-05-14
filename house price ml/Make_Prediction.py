import pandas as pd
import os
import joblib
import random

def make_prediction():
    test_path = 'data/test.csv'
    model_path = 'models/house_price_model.pkl'
    
    if not os.path.exists(test_path) or not os.path.exists(model_path):
        print("Error: Missing test data or model file. Run training and split steps first.")
        return None
        
    print(f"🔮 Loading test data and model for prediction...")
    df = pd.read_csv(test_path)
    model = joblib.load(model_path)
    
    target_col = 'Price (in rupees)'
    X_test = df.drop(columns=[target_col])
    y_test = df[target_col]
    
    # Pick a random sample
    random_idx = random.randint(0, len(X_test) - 1)
    sample_features = X_test.iloc[[random_idx]]
    actual_price = y_test.iloc[random_idx]
    
    print(f"Making prediction on sample #{random_idx}...")
    predicted_price = model.predict(sample_features)[0]
    
    print("\n" + "="*30)
    print(f"🏠 Prediction Results:")
    print(f"Actual Price (Scaled):    {actual_price:,.4f}")
    print(f"Predicted Price (Scaled): {predicted_price:,.4f}")
    print(f"Difference:               {abs(actual_price - predicted_price):,.4f}")
    print("="*30 + "\n")
    
    return {'actual_price': float(actual_price), 'predicted_price': float(predicted_price)}

if __name__ == "__main__":
    make_prediction()
