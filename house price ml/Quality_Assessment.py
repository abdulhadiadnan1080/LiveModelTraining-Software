import matplotlib
matplotlib.use('Agg') # MUST be before pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

def find_data_file(directory='data'):
    """Finds the first raw CSV file in the directory (skipping already cleaned/split files)."""
    if not os.path.exists(directory):
        return None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv') and not any(x in file.lower() for x in ['cleaned', 'train', 'test']):
                return os.path.join(root, file)
    return None

def run_assessment(file_path=None):
    if file_path is None:
        file_path = find_data_file()
        
    if not file_path or not os.path.exists(file_path):
        print(f"Error: No raw data CSV found in 'data/' folder.")
        return
    
    df = pd.read_csv(file_path)
    print(f"📋 Quality Assessment for: {file_path}")
    print(f"Shape: {df.shape}\n")

    # --- 1. MISSING VALUES ---
    print("--- 1. MISSING VALUES ANALYSIS ---")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({'Missing': missing, 'Percentage': missing_pct})
    print(missing_df[missing_df['Missing'] > 0].sort_values(by='Missing', ascending=False))
    print("\n")

    # --- 2. CATEGORICAL DATA ---
    print("--- 2. CATEGORICAL DATA ANALYSIS ---")
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        print(f"Column '{col}': {df[col].nunique()} unique values. Top 3: {df[col].dropna().unique()[:3]}")
    print("\n")

    # --- 3. IRRELEVANT DATA ---
    print("--- 3. IRRELEVANT DATA ANALYSIS ---")
    # Constant columns
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    print(f"Constant/Empty Columns: {constant_cols}")
    # High cardinality IDs
    id_like = [col for col in df.columns if 'index' in col.lower() or 'id' in col.lower()]
    print(f"Potential ID Columns: {id_like}")
    print("\n")

    # --- 4. DATA VISUALIZATION ---
    print("--- 4. DATA VISUALIZATION ---")
    os.makedirs('plots', exist_ok=True)
    
    # Missing values heatmap
    print("Generating Missing Values Heatmap...")
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')
    plt.title('Missing Values Heatmap')
    plt.savefig('plots/missing_values_heatmap.png')
    plt.close()
    print("Saved missing_values_heatmap.png")
    
    # Distribution of target (if exists)
    target_col = 'Price (in rupees)'
    if target_col in df.columns:
        print(f"Generating Distribution plot for {target_col}...")
        plt.figure(figsize=(10, 6))
        sns.histplot(df[target_col].dropna(), kde=True)
        plt.title(f'Distribution of {target_col}')
        plt.savefig('plots/target_distribution.png')
        plt.close()
        print("Saved target_distribution.png")
    else:
        print(f"Skipping distribution plot: '{target_col}' not found in columns.")
    print("Visualizations complete.\n")

    # --- 5. OUTLIERS ---
    print("--- 5. OUTLIER DETECTION ---")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
        if len(outliers) > 0:
            print(f"Column '{col}': {len(outliers)} potential outliers detected.")
    print("\n")

    # --- 6. FEATURE SCALING CHECK ---
    print("--- 6. FEATURE SCALING CHECK ---")
    if len(numeric_cols) > 0:
        stats = df[numeric_cols].describe().loc[['min', 'max']]
        print(stats)
        print("\nObservation: Significant range differences indicate scaling is needed.")

    # Return stats for the GUI
    assessment_stats = {
        'total_missing': float(df.isnull().sum().sum()),
        'cat_cols_count': float(len(df.select_dtypes(include=['object']).columns)),
        'num_cols_count': float(len(df.select_dtypes(include=[np.number]).columns)),
        'row_count': float(len(df))
    }
    return assessment_stats

if __name__ == "__main__":
    run_assessment()
