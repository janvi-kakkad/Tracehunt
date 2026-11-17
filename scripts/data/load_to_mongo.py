"""
TraceHunt MongoDB Loader.
Loads all generated CSV datasets and analysis outputs into MongoDB collections.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.db import get_db, load_csv_to_collection

def main():
    print("=" * 60)
    print("Loading Datasets into MongoDB")
    print("=" * 60)

    dataset_dir = ROOT_DIR / "dataset"
    collections = ["people", "locations", "incidents"]
    
    for c in collections:
        csv_file = dataset_dir / f"{c}.csv"
        if csv_file.exists():
            cnt = load_csv_to_collection(c, csv_file)
            print(f"[+] Loaded {cnt:,} documents into '{c}' collection.")

    db = get_db()
    print(f"\n[+] Total anomalies in MongoDB:    {db['anomalies'].count_documents({}):,}")
    print(f"[+] Total case results in MongoDB: {db['case_results'].count_documents({}):,}")
    print("=" * 60)

if __name__ == "__main__":
    main()
