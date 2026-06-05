import os
import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables if they exist
load_dotenv()

API_KEY = os.getenv('AVIATIONSTACK_API_KEY')
BASE_URL = "http://api.aviationstack.com/v1/flights"

def ingest_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Enforce Structured Directory Creation
    json_dir = Path("data/raw/raw_json")
    csv_dir = Path("data/raw/raw_csv")
    clean_placeholder = Path("data/clean")
    
    json_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    clean_placeholder.mkdir(parents=True, exist_ok=True)

    if not API_KEY:
        print("❌ Critical Error: AVIATIONSTACK_API_KEY environment variable is missing.")
        return

    print(f"📡 Requesting real-time flight data matrix at {timestamp}...")
    
    # 2. API Request Implementation
    params = {'access_key': API_KEY, 'limit': 100}
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        
        # 3. Preserve the Original Raw JSON Format
        json_file = json_dir / f"raw_flights_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
        print(f"📁 JSON Source Snapshot Saved: {json_file.name}")
        
        # 4. Flatten and Export To Uncleaned CSV File
        if 'data' in payload and len(payload['data']) > 0:
            df = pd.json_normalize(payload['data'])
            csv_file = csv_dir / f"raw_flights_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"📊 Flattened Raw CSV Snapshot Saved: {csv_file.name}")
            print(f"✨ Successfully collected {len(df)} flight items.")
        else:
            print("⚠️ API Response returned an empty flight dataset or authentication alert.")

    except requests.exceptions.RequestException as req_err:
        print(f"❌ Connection/HTTP Pipeline Failure: {req_err}")
    except Exception as general_err:
        print(f"❌ Runtime Processing Error: {general_err}")

if __name__ == "__main__":
    ingest_data()