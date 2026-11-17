#!/usr/bin/env bash
# Upload TraceHunt CSV datasets to HDFS with 128MB blocksize and replication 2
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [ -f "${PROJECT_ROOT}/config/cluster.env" ]; then
    source "${PROJECT_ROOT}/config/cluster.env"
fi

HDFS_DIR="/tracehunt/raw"
BLOCKSIZE=134217728  # 128 MB
REPLICATION=1

echo "=================================================="
echo "Uploading Datasets to HDFS (${HDFS_DIR})"
echo "Block size: ${BLOCKSIZE} bytes | Replication: ${REPLICATION}"
echo "=================================================="

# Create HDFS directories
hdfs dfs -mkdir -p "${HDFS_DIR}"

# Upload files with designated block size and replication
for FILE in people.csv locations.csv incidents.csv movement_events.csv; do
    LOCAL_PATH="${PROJECT_ROOT}/dataset/${FILE}"
    if [ -f "${LOCAL_PATH}" ]; then
        echo "[*] Uploading ${FILE}..."
        hdfs dfs -D dfs.blocksize=${BLOCKSIZE} -D dfs.replication=${REPLICATION} -put -f "${LOCAL_PATH}" "${HDFS_DIR}/${FILE}"
    fi
done

echo ""
echo "[*] Verifying HDFS block count on movement_events.csv:"
hdfs fsck "${HDFS_DIR}/movement_events.csv" -files -blocks -locations

echo ""
echo "[+] All datasets uploaded successfully to HDFS."
