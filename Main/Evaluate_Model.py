import pandas as pd
import numpy as np
import os
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_model():
    test_path = 'data/test.csv'
    model_path = 'models/house_price_model.pkl'
    
    if not os.path.exists(test_path) or not os.path.exists(model_path):
        print("Error: Missing test data or model file. Run previous steps first.")
        return None
        
    print(f"📊 Loading test data and model...")
    df = pd.read_csv(test_path)
    model = joblib.load(model_path)
    
    target_col = 'Price (in rupees)'
    X_test = df.drop(columns=[target_col])
    y_test = df[target_col]
    
    print("Making predictions...")
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"Results:\nMAE: {mae:.2f}\nRMSE: {rmse:.2f}\nR2 Score: {r2:.4f}")
    
    # Visualization
    print("Generating Actual vs Predicted plot...")
    os.makedirs('plots', exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Price (Scaled)')
    plt.ylabel('Predicted Price (Scaled)')
    plt.title('Actual vs Predicted House Prices')
    plt.savefig('plots/model_evaluation.png')
    plt.close()
    print("Saved model_evaluation.png to plots/")
    
    return {'mae': float(mae), 'rmse': float(rmse), 'r2': float(r2)}

if __name__ == "__main__":
    evaluate_model()
