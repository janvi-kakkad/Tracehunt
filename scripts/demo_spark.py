#!/usr/bin/env python3
"""
TraceHunt Live Distributed Spark Demo Script.
Demonstrates HDFS reading and parallel processing across the 3-node cluster.
"""

from pyspark.sql import SparkSession

def main():
    print("=" * 60)
    print("TraceHunt: Initializing Distributed Apache Spark Session")
    print("=" * 60)

    spark = SparkSession.builder \
        .appName("TraceHunt-Distributed-Demo") \
        .config("spark.executor.memory", "2g") \
        .config("spark.executor.cores", "2") \
        .config("spark.serializer", "org.apache.spark.serializer.JavaSerializer") \
        .config("spark.sql.adaptive.enabled", "false") \
        .getOrCreate()

    sc = spark.sparkContext
    print(f"\n[+] Spark Master URL    : {sc.master}")
    print(f"[+] Spark Application ID: {sc.applicationId}")

    import os
    import sys

    master_host = os.getenv("MASTER_HOST", "localhost")
    hdfs_port = os.getenv("HDFS_NAMENODE_PORT", "9000")
    default_path = os.getenv("HDFS_PATH", "/tracehunt/raw/movement_events.csv")
    
    # Allow custom HDFS URL or local fallback if specified in command line
    if len(sys.argv) > 1:
        hdfs_url = sys.argv[1]
    else:
        hdfs_url = f"hdfs://{master_host}:{hdfs_port}{default_path}"

    print(f"\n[*] Target HDFS/Data location: {hdfs_url}")

    df = spark.read.csv(hdfs_url, header=True, inferSchema=False)
    num_parts = df.rdd.getNumPartitions()
    print(f"[+] Total Distributed Partitions: {num_parts}")

    # =========================================================================
    # BDS PROOF: Inspect Connected Distributed Worker Executors
    # =========================================================================
    print("\n" + "=" * 60)
    print("PROVING DISTRIBUTED PROCESSING: Active Worker Node(s)")
    print("=" * 60)

    import urllib.request
    import json

    try:
        spark_json_url = f"http://{master_host}:8080/json/"
        with urllib.request.urlopen(spark_json_url, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            workers = data.get("workers", [])
            print(f"{'Worker ID':<42} | {'Host IP':<16} | {'Cores':<7} | {'RAM (MB)':<10}")
            print("-" * 80)
            for w in workers:
                print(f"{w.get('id', 'N/A'):<42} | {w.get('host', 'N/A'):<16} | {str(w.get('cores', 'N/A')):<7} | {str(w.get('memory', 'N/A')):<10}")
            print("-" * 80)
    except Exception as e:
        print(f"[!] Worker info: {e}")

    # =========================================================================
    # Task 1: Distributed HDFS Record Preview
    # =========================================================================
    print("\n" + "=" * 60)
    print("TASK 1: Distributed HDFS Record Extraction")
    print("=" * 60)
    df.select("event_id", "person_id", "location_id", "source", "timestamp").show(5, truncate=False)

    # =========================================================================
    # Task 2: Fast Distributed Aggregation - Top 5 Crime Hotspots
    # =========================================================================
    print("\n" + "=" * 60)
    print("TASK 2: Top 5 High-Activity Crime Hotspots (Parallel Aggregation)")
    print("=" * 60)

    from pyspark.sql import functions as F

    hotspots = df.limit(50000).groupBy("location_id") \
        .agg(
            F.count("event_id").alias("total_pings"),
            F.countDistinct("person_id").alias("unique_suspects")
        ) \
        .orderBy(F.desc("total_pings")) \
        .limit(5)

    hotspots.show(truncate=False)

    print("=" * 60)
    print("SUCCESS: Task completed across the distributed cluster!")
    print("Check Spark Web UI at: http://localhost:8081")
    print("=" * 60)

    spark.stop()

if __name__ == "__main__":
    main()
