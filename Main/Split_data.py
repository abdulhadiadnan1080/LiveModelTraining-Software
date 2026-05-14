import pandas as pd
import glob
import os
from sklearn.model_selection import train_test_split

def find_cleaned_file(directory='data'):
    """Finds the first cleaned CSV file in the directory."""
    if not os.path.exists(directory):
        return None
    for root, dirs, files in os.walk(directory):
        for file in files:
            if 'cleaned' in file.lower() and file.endswith('.csv'):
                return os.path.join(root, file)
    return None

def split_data():
    target_file = find_cleaned_file()
    
    if not target_file:
        # Fallback to any CSV if no cleaned file exists
        for root, dirs, files in os.walk('data'):
            for file in files:
                if file.endswith('.csv') and not any(x in file.lower() for x in ['train', 'test']):
                    target_file = os.path.join(root, file)
                    break
            if target_file: break

    # Only split if we have a target file and no train/test pair exists already
    if target_file and not (os.path.exists('data/train.csv') and os.path.exists('data/test.csv')):
        print(f"Splitting {target_file}...")
        df = pd.read_csv(target_file)
        train, test = train_test_split(df, test_size=0.2, random_state=42)
        
        train.to_csv('data/train.csv', index=False)
        test.to_csv('data/test.csv', index=False)
        print("Done! Generated data/train.csv and data/test.csv")
    else:
        print("No split performed (already split or multiple files found).")

if __name__ == "__main__":
    split_data()
