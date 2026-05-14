import os
import re
import zipfile
import subprocess
from pathlib import Path

# ==========================================
# CONFIGURATION - Set your credentials here
# ==========================================
KAGGLE_USERNAME = "bingfox123456789"
KAGGLE_TOKEN = "KGAT_e6626d5b5022062b41e7f9e19e6e4706"  # Replace with "XYZ Access Token" if needed
# ==========================================

def parse_kaggle_url(url):
    """
    Parses a Kaggle URL to determine if it's a competition or a dataset.
    Returns (type, slug)
    """
    # Competition or Dataset ?
    comp_match = re.search(r'kaggle\.com/competitions/([^/]+)', url)
    if comp_match:
        return "competition", comp_match.group(1)
    
    ds_match = re.search(r'kaggle\.com/datasets/([^/]+/[^/?]+)', url)
    if ds_match:
        return "dataset", ds_match.group(1)
    
    # Direct slug check ("username/dataset-name" or "competition-name")
    if "/" in url:
        return "dataset", url.strip()
    else:
        return "competition", url.strip()

def download_from_kaggle(url, username, token, save_path="data"):
    # 1. Parse URL
    item_type, slug = parse_kaggle_url(url)
    print(f"Detected {item_type}: {slug}")
    
    # 2. Setup paths
    data_dir = Path(save_path) #Not workinng on mac, because of difference of download/data(Mac) and download\data(Window)
    data_dir.mkdir(exist_ok=True)
    zip_path = data_dir / "download.zip"
    
    # 3. Construct API Endpoint
    if item_type == "competition":
        api_url = f"https://www.kaggle.com/api/v1/competitions/data/download-all/{slug}"
    else:
        api_url = f"https://www.kaggle.com/api/v1/datasets/download/{slug}"
    
    # 4. Download using curl
    print(f"Downloading from Kaggle...")
    
    if token.startswith("KGAT_"):
        auth_args = ["-H", f"Authorization: Bearer {token}"]
    else:
        if not username:
            print("Error: Kaggle Username is required if you are using a standard API Key.")
            return
        auth_args = ["-u", f"{username}:{token}"]

    cmd = [
        "curl", "-L",
        *auth_args,
        api_url,
        "-o", str(zip_path)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Check for errors in the downloaded file (Kaggle returns JSON errors even for file downloads)
        if zip_path.exists() and zip_path.stat().st_size < 1000:
            with open(zip_path, 'r') as f:
                content = f.read()
                if '"code":403' in content:
                    print("\nError 403: You must accept the rules on the Kaggle website first!")
                    print(f"Link: {url}")
                    os.remove(zip_path)
                    return
                elif '"code":401' in content:
                    print("\nError 401: Unauthorized. Please check your KAGGLE_TOKEN.")
                    os.remove(zip_path)
                    return
        
        # 5. Extract
        if zip_path.exists() and zipfile.is_zipfile(zip_path):
            print(f"Extracting files to {data_dir}/...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            print("Done!")
            os.remove(zip_path)
        elif zip_path.exists():
            print("Download completed but it doesn't look like a zip file. Check the contents of the data folder.")
        else:
            print("Download failed.")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    target_url = input("Enter Url: ").strip()
    if target_url:
        download_from_kaggle(target_url)
    else:
        print("No URL provided.")
