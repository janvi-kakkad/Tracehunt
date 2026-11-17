# TraceHunt: Master & Worker (Slave) Complete Connection Guide
## Step-by-Step Distributed Cluster Setup for Apache Hadoop & Apache Spark

> **Cluster Architecture:**
> - **Master Node:** Apple Mac (macOS) — Runs HDFS NameNode & Spark Master
> - **Worker / Slave Node:** Windows Laptop (Windows 10/11) — Runs HDFS DataNode & Spark Worker
> - **Prerequisite:** Hadoop 3.3.x and Apache Spark 3.5.x are installed on both laptops.

---

## Quick Reference: IP & Hostname Setup

Before running commands, note down the actual IP addresses of both machines on your shared Wi-Fi / LAN network:
- **Master IP (Mac):** e.g., `192.168.1.10` (or `10.21.6.150`)
- **Worker IP (Windows):** e.g., `192.168.1.20` (or `10.21.28.146`)

---

## STEP 1: Network Setup & Ping Test

Both laptops **must be on the same local Wi-Fi or Hotspot network** and be able to talk to each other.

### 1.1 Find IP Addresses
- **On Mac (Terminal):**
  ```bash
  ifconfig | grep "inet "
  # Look for 192.168.x.x or 10.x.x.x (note down as MASTER_IP)
  ```
- **On Windows (PowerShell or CMD):**
  ```powershell
  ipconfig
  # Look for "IPv4 Address" under Wireless LAN adapter (note down as WORKER_IP)
  ```

---

### 1.2 Setup Hostname Mapping (Bidirectional)

#### On Mac (Terminal):
Open `/etc/hosts`:
```bash
sudo nano /etc/hosts
```
Add the worker's line at the bottom:
```text
<WORKER_IP>   worker1
```
*(Save: `Ctrl + O`, `Enter`, Exit: `Ctrl + X`)*

#### On Windows (Run PowerShell as Administrator):
Open the hosts file in Notepad:
```powershell
notepad C:\Windows\System32\drivers\etc\hosts
```
Add the master's line at the bottom:
```text
<MASTER_IP>   master
```
*(Save and close Notepad)*

---

### 1.3 Test Network Connection
- **From Mac Terminal:**
  ```bash
  ping -c 3 <WORKER_IP>
  ```
- **From Windows PowerShell:**
  ```powershell
  ping <MASTER_IP>
  ```
*If ping fails, turn off "Public Network Firewall" on Windows temporarily or allow ICMP echo requests.*

---

## STEP 2: Configure Hadoop HDFS on Both Machines

### 2.1 Configuration on MASTER (Mac)

Navigate to `$HADOOP_HOME/etc/hadoop/`:

1. **Edit `core-site.xml`:**
   ```bash
   nano $HADOOP_HOME/etc/hadoop/core-site.xml
   ```
   Insert inside `<configuration>`:
   ```xml
   <configuration>
       <property>
           <name>fs.defaultFS</name>
           <value>hdfs://master:9000</value>
       </property>
   </configuration>
   ```

2. **Edit `hdfs-site.xml`:**
   ```bash
   nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
   ```
   Insert inside `<configuration>`:
   ```xml
   <configuration>
       <property>
           <name>dfs.replication</name>
           <value>1</value>
       </property>
       <property>
           <name>dfs.blocksize</name>
           <value>134217728</value>
       </property>
       <property>
           <name>dfs.namenode.name.dir</name>
           <value>file:///Users/JANVI/hadoop_data/hdfs/namenode</value>
       </property>
   </configuration>
   ```

3. **Edit `workers` file on Mac:**
   ```bash
   nano $HADOOP_HOME/etc/hadoop/workers
   ```
   Add the worker hostname:
   ```text
   worker1
   ```

---

### 2.2 Configuration on WORKER / SLAVE (Windows)

On Windows, navigate to `C:\hadoop\etc\hadoop\` (or your `$HADOOP_HOME\etc\hadoop\`):

1. **Verify Windows Binaries (`winutils.exe` & `hadoop.dll`):**
   - Ensure `winutils.exe` and `hadoop.dll` exist in `C:\hadoop\bin\`.
   - Ensure `hadoop.dll` is copied to `C:\Windows\System32\`.

2. **Edit `core-site.xml` on Windows:**
   Open in Notepad: `C:\hadoop\etc\hadoop\core-site.xml`:
   ```xml
   <configuration>
       <property>
           <name>fs.defaultFS</name>
           <value>hdfs://master:9000</value>
       </property>
   </configuration>
   ```
   *(Note: This points to the **master** IP/hostname!)*

3. **Edit `hdfs-site.xml` on Windows:**
   Open in Notepad: `C:\hadoop\etc\hadoop\hdfs-site.xml`:
   ```xml
   <configuration>
       <property>
           <name>dfs.replication</name>
           <value>1</value>
       </property>
       <property>
           <name>dfs.datanode.data.dir</name>
           <value>file:///C:/hadoop_data/hdfs/datanode</value>
       </property>
   </configuration>
   ```

---

## STEP 3: Start Hadoop HDFS Cluster

### 3.1 On Master (Mac) — Start NameNode
1. **Format NameNode (Run ONCE only on fresh setup):**
   ```bash
   hdfs namenode -format
   ```
2. **Start NameNode daemon:**
   ```bash
   $HADOOP_HOME/bin/hdfs --daemon start namenode
   ```
3. **Verify Master Java Process:**
   ```bash
   jps
   ```
   *Output must show: `NameNode`*

---

### 3.2 On Worker (Windows) — Start DataNode
1. Open PowerShell or CMD (Run as Administrator):
   ```powershell
   hdfs --daemon start datanode
   ```
   *(Or run via `.cmd`)*:
   ```powershell
   %HADOOP_HOME%\bin\hdfs.cmd --daemon start datanode
   ```
2. **Verify Worker Java Process:**
   ```powershell
   jps
   ```
   *Output must show: `DataNode`*

---

### 3.3 Verify HDFS Distributed Connection
1. **From Mac Terminal, check DataNode report:**
   ```bash
   hdfs dfsadmin -report
   ```
   *Look for: `Live datanodes (1)` with the Windows worker IP listed!*

2. **Open HDFS Web Console in browser:**
   ```
   http://localhost:9870/
   ```
   Click on the **"Datanodes"** tab. You will see your Windows laptop listed as an active, healthy DataNode!

---

## STEP 4: Start Apache Spark Cluster (Master + Worker)

### 4.1 On Master (Mac) — Start Spark Standalone Master

1. **Start Spark Master daemon:**
   ```bash
   $SPARK_HOME/sbin/start-master.sh -h <MASTER_IP> -p 7077 --webui-port 8080
   ```
   *(Replace `<MASTER_IP>` with your actual Mac IP, e.g., `10.21.6.150` or `192.168.1.10`)*

2. **Verify Process:**
   ```bash
   jps
   ```
   *Output must show: `Master`*

3. **Check Spark Master Web UI:**
   Open in your Mac browser:
   ```
   http://localhost:8080/
   ```
   You will see:
   - **URL:** `spark://<MASTER_IP>:7077`
   - **Alive Workers:** `0` (until we connect the Windows worker)

---

### 4.2 On Worker (Windows) — Connect Spark Worker to Master

In Windows PowerShell, run the Spark worker class pointing to the Mac Master's Spark URL:

```powershell
$MASTER_URL = "spark://<MASTER_IP>:7077"

& "$env:SPARK_HOME\bin\spark-class.cmd" org.apache.spark.deploy.worker.Worker $MASTER_URL
```

*Example with explicit IP:*
```powershell
& "C:\spark\bin\spark-class.cmd" org.apache.spark.deploy.worker.Worker spark://10.21.6.150:7077
```

**What you will see in Windows terminal:**
```text
Successfully registered with master spark://10.21.6.150:7077
```

**Verify Process on Windows:**
In another PowerShell window:
```powershell
jps
```
*Output must show: `Worker`*

---

### 4.3 Verify Spark Cluster Connection on Web UI
Refresh your Mac browser at:
```
http://localhost:8080/
```
You will now see:
- **Alive Workers: 1**
- Worker ID: `worker-YYYYMMDD...-<WORKER_IP>`
- Cores: `4` (or your Windows CPU core count)
- Memory: `8.0 GB` (or available Windows RAM)

---

## STEP 5: Upload Dataset to HDFS with 128 MB Block Size

Now that both HDFS and Spark are connected, upload your dataset from the Mac Master into the distributed HDFS cluster:

```bash
cd /Users/JANVI/Desktop/College/college/Sem_7/BDS_innovative

# 1. Create HDFS directory
hdfs dfs -mkdir -p /tracehunt/raw

# 2. Upload with 128 MB block size (forces 4 physical blocks)
hdfs dfs -D dfs.blocksize=134217728 -D dfs.replication=1 -put -f dataset/movement_events.csv /tracehunt/raw/movement_events.csv

# 3. Upload reference metadata files
hdfs dfs -put -f dataset/people.csv /tracehunt/raw/
hdfs dfs -put -f dataset/locations.csv /tracehunt/raw/
hdfs dfs -put -f dataset/incidents.csv /tracehunt/raw/
```

### Verify the 4-Block Split Across the DataNode:
```bash
hdfs fsck /tracehunt/raw/movement_events.csv -files -blocks -locations
```
**Expected Output:**
```text
Total size:    483017863 B
Total blocks (validated): 4 (avg. block size 120754465 B)
0. blk_1073741825 len=134217728 [worker1:9866]
1. blk_1073741826 len=134217728 [worker1:9866]
2. blk_1073741827 len=134217728 [worker1:9866]
3. blk_1073741828 len=80364679  [worker1:9866]
Status: HEALTHY
```

---

## STEP 6: Run Distributed Spark Processing Across the Cluster

Run the jobs on the Mac Master. Spark will dispatch tasks over Wi-Fi to the Windows worker executors!

### 6.1 Run Hotspot Aggregation Across Cluster:
```bash
MASTER_HOST="<MASTER_IP>" \
spark-submit \
  --master spark://<MASTER_IP>:7077 \
  --executor-memory 2G \
  --executor-cores 2 \
  scripts/demo_spark.py
```

### 6.2 Run Crime Case Investigation Across Cluster:
```bash
SPARK_MASTER_URL="spark://<MASTER_IP>:7077" \
/Users/JANVI/venv/bin/python scripts/spark_case_solver.py INC001
```
*(Or for all 8 cases)*:
```bash
SPARK_MASTER_URL="spark://<MASTER_IP>:7077" \
/Users/JANVI/venv/bin/python scripts/spark_case_solver.py --all
```

---

## STEP 7: Shutting Down the Cluster Cleanly

When finished with your presentation/testing, shut down in reverse order:

### On Windows (Worker):
```powershell
# Stop Spark Worker: Press CTRL + C in the Worker terminal

# Stop HDFS DataNode:
hdfs --daemon stop datanode
```

### On Mac (Master):
```bash
# 1. Stop Spark Master:
$SPARK_HOME/sbin/stop-master.sh

# 2. Stop HDFS NameNode:
$HADOOP_HOME/bin/hdfs --daemon stop namenode
```

---

## Troubleshooting Common Errors

| Error Symptom | Cause | Exact Fix |
| :--- | :--- | :--- |
| `java.net.SocketException: Host is down` | Mac or Windows IP changed or wrong IP in `core-site.xml` | Check `ifconfig` / `ipconfig`. Update `master` IP in `/etc/hosts` and `hosts` file. |
| `Connection refused: master:9000` | NameNode is not running on Mac | Run `$HADOOP_HOME/bin/hdfs --daemon start namenode` and check `jps`. |
| Windows says `winutils.exe not found` | Missing native Windows Hadoop C++ helper | Download `winutils.exe` and `hadoop.dll` for Hadoop 3.3.6 into `C:\hadoop\bin\` and copy `hadoop.dll` to `C:\Windows\System32\`. |
| Windows DataNode starts then stops immediately | Cluster ID mismatch after re-formatting NameNode | Delete `C:\hadoop_data\hdfs\datanode` directory on Windows and start datanode again. |
| Spark Worker connects but 0 tasks run | Port 7077 or 9866 blocked by firewall | Temporarily disable Windows Defender Firewall or allow inbound TCP rules for ports 7077, 9000, 9866. |
