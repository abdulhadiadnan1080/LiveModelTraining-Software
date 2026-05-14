import pandas as pd
import numpy as np
import re
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder

def find_data_file(directory='data'):
    """Finds the first raw CSV file in the directory (skipping already cleaned/split files)."""
    if not os.path.exists(directory):
        return None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and not any(x in file.lower() for x in ['cleaned', 'train', 'test']):
                return os.path.join(root, file)
    return None

def clean_data(file_path=None):
    if file_path is None:
        file_path = find_data_file()

    if not file_path or not os.path.exists(file_path):
        print(f"Error: No raw data CSV found in 'data/' folder.")
        return
    
    df = pd.read_csv(file_path)
    print(f"🧹 Starting Cleaning Process: {file_path}")
    print(f"Initial Shape: {df.shape}")

    # --- 1. REMOVE IRRELEVANT DATA ---
    print("--- 1. REMOVING IRRELEVANT DATA ---")
    initial_rows = len(df)
    cols_to_drop = ['Index', 'Status', 'Dimensions', 'Plot Area']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    df = df.drop_duplicates()
    final_rows_irrelevant = len(df)
    print(f"Rows removed: {initial_rows - final_rows_irrelevant} ({( (initial_rows - final_rows_irrelevant) / initial_rows * 100):.2f}%)")

    # --- 2. HANDLE MISSING VALUES ---
    print("--- 2. HANDLING MISSING VALUES ---")
    total_missing_before = df.isnull().sum().sum()
    # Drop rows where target is missing
    if 'Price (in rupees)' in df.columns:
        df = df.dropna(subset=['Price (in rupees)'])
    
    # Impute numeric with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())
        
    # Impute categorical with 'Unknown'
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df[col] = df[col].fillna('Unknown')
    
    total_missing_after = df.isnull().sum().sum()
    print(f"Missing values filled: {float(total_missing_before - total_missing_after)}")

    # --- 3. PROCESS CATEGORICAL DATA ---
    print("--- 3. PROCESSING CATEGORICAL DATA ---")
    def extract_num(val):
        if pd.isna(val) or not isinstance(val, str): return val
        match = re.search(r'(\d+\.?\d*)', val)
        return float(match.group(1)) if match else np.nan

    converted_count = 0
    for col in ['Carpet Area', 'Super Area', 'Bathroom', 'Balcony']:
        if col in df.columns:
            df[col] = df[col].apply(extract_num).fillna(0)
            converted_count += 1
    
    # Encoding categorical columns
    le = LabelEncoder()
    encoded_count = 0
    for col in cat_cols:
        if col in df.columns and col not in ['Title', 'Description']:
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            encoded_count += 1
            
    # Drop all original object columns (including skipped ones like Title/Description)
    remaining_obj_cols = df.select_dtypes(include=['object']).columns
    df = df.drop(columns=remaining_obj_cols)
            
    print(f"Columns processed: {float(converted_count)}, Encoded: {float(encoded_count)}")

    # --- 4. HANDLE OUTLIERS ---
    print("--- 4. HANDLING OUTLIERS (Capping) ---")
    capped_total = 0
    for col in df.select_dtypes(include=[np.number]).columns:
        lower = df[col].quantile(0.01)
        upper = df[col].quantile(0.99)
        # Count how many were actually changed
        capped_total += len(df[(df[col] < lower) | (df[col] > upper)])
        df[col] = df[col].clip(lower, upper)
    print(f"Total outlier points capped: {float(capped_total)}")

    # --- 5. FEATURE SCALING ---
    print("--- 5. FEATURE SCALING ---")
    scaler = StandardScaler()
    num_cols_to_scale = [col for col in df.select_dtypes(include=[np.number]).columns if col != 'Price (in rupees)']
    if num_cols_to_scale:
        df[num_cols_to_scale] = scaler.fit_transform(df[num_cols_to_scale])
        print(f"Scaled {float(len(num_cols_to_scale))} numeric columns.")
    
    # Return stats for the GUI
    stats = {
        'initial_rows': float(initial_rows),
        'rows_removed': float(initial_rows - final_rows_irrelevant),
        'missing_filled': float(total_missing_before - total_missing_after),
        'cols_encoded': float(encoded_count),
        'outliers_capped': float(capped_total),
        'retention_pct': float((len(df) / initial_rows * 100))
    }
    
    # Save cleaned data
    out_path = 'data/house_prices_cleaned.csv'
    df.to_csv(out_path, index=False)
    print(f"✅ Final data retention: {stats['retention_pct']:.2f}%")
    print(f"Cleaned file saved to: {out_path}")
    return stats

if __name__ == "__main__":
    clean_data()
