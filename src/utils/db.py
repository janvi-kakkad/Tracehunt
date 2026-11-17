"""
MongoDB connection and collection utilities for TraceHunt.
Uses environment variables (MONGO_URI, MONGO_DB) with sensible local defaults.
"""

import os
import csv
from pathlib import Path

# MongoDB Configuration from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB", "tracehunt")

def get_client():
    """Return a PyMongo MongoClient instance."""
    try:
        from pymongo import MongoClient
        return MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    except Exception as e:
        raise RuntimeError(f"MongoDB client unavailable: {e}")

def get_db():
    """Return the TraceHunt database instance."""
    client = get_client()
    return client[MONGO_DB_NAME]

def load_csv_to_collection(collection_name: str, csv_path: Path, drop_first: bool = True):
    """Load a CSV file into a specified MongoDB collection."""
    db = get_db()
    col = db[collection_name]
    if drop_first:
        col.drop()
        
    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
            if len(records) >= 5000:
                col.insert_many(records)
                records = []
        if records:
            col.insert_many(records)
    return col.count_documents({})
