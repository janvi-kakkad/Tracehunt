"""
Synthetic Data Generator for TraceHunt.

Generates realistic movement data in Ahmedabad for 45 days (2026-08-01 to 2026-09-14).
Calibrates output size so movement_events.csv is strictly between 460MB and 500MB (4 x 128MB HDFS blocks).
Plants ground truth anomalies and robbery/murder cases.
"""

import csv
import json
import math
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.geo import haversine_km, speed_kmh

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

START_DATE = datetime(2026, 8, 1, 0, 0, 0)
TOTAL_DAYS = 45
HDFS_BLOCK_SIZE = 134217728  # 128 MB in bytes
MIN_TARGET_BYTES = 460000000  # 460 MB
MAX_TARGET_BYTES = 500000000  # 500 MB
TARGET_FILE_BYTES = 478000000  # Calibration target ~478 MB (yields exactly 4 blocks)

DATASET_DIR = ROOT_DIR / "dataset"
GROUND_TRUTH_DIR = DATASET_DIR / "ground_truth"
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Ahmedabad Locality Templates
# ---------------------------------------------------------------------------
AREAS = [
    {"name": "Navrangpura", "lat": 23.0370, "lon": 72.5600},
    {"name": "CG Road", "lat": 23.0300, "lon": 72.5580},
    {"name": "Manek Chowk", "lat": 23.0230, "lon": 72.5890},
    {"name": "Maninagar", "lat": 22.9970, "lon": 72.6030},
    {"name": "SG Highway", "lat": 23.0550, "lon": 72.5050},
    {"name": "Vastrapur", "lat": 23.0350, "lon": 72.5280},
    {"name": "Kankaria Lake", "lat": 23.0060, "lon": 72.6020},
    {"name": "Law Garden", "lat": 23.0250, "lon": 72.5580},
    {"name": "Motera", "lat": 23.0920, "lon": 72.5970},
    {"name": "Paldi", "lat": 23.0130, "lon": 72.5620},
    {"name": "Ellis Bridge", "lat": 23.0220, "lon": 72.5710},
    {"name": "Sabarmati", "lat": 23.0600, "lon": 72.5800},
    {"name": "Satellite", "lat": 23.0280, "lon": 72.5180},
    {"name": "Bodakdev", "lat": 23.0420, "lon": 72.5170},
    {"name": "Thaltej", "lat": 23.0530, "lon": 72.5080},
    {"name": "Bopal", "lat": 23.0340, "lon": 72.4680},
    {"name": "Nikol", "lat": 23.0440, "lon": 72.6650},
    {"name": "Naroda", "lat": 23.0720, "lon": 72.6580},
    {"name": "Chandkheda", "lat": 23.1100, "lon": 72.5850},
    {"name": "Gota", "lat": 23.0980, "lon": 72.5350},
    {"name": "Isanpur", "lat": 22.9800, "lon": 72.6000},
    {"name": "Vatva", "lat": 22.9650, "lon": 72.6250},
    {"name": "Sarkhej", "lat": 22.9850, "lon": 72.5000},
    {"name": "Shahibaug", "lat": 23.0580, "lon": 72.5930},
    {"name": "Ashram Road", "lat": 23.0350, "lon": 72.5700},
]

OCCUPATIONS = [
    "student", "office worker", "shopkeeper", "homemaker",
    "delivery rider", "driver", "night-shift worker", "doctor or nurse", "retired"
]

FIRST_NAMES_MALE = [
    "Aarav", "Bhavin", "Chirag", "Deepak", "Faizan", "Gaurav", "Hardik", "Imran",
    "Jigar", "Karan", "Luv", "Manish", "Nirav", "Parth", "Rahul", "Sameer",
    "Tapan", "Utkarsh", "Varun", "Yash", "Devendra", "Hasmukh", "Ketan", "Mukesh",
    "Nilesh", "Paresh", "Rajesh", "Suresh", "Ramesh", "Vipul", "Mohammed", "Tariq",
    "Kirtan", "Siddharth", "Girish", "Prakash", "Rohan", "Anand", "Pranav", "Mihir"
]

FIRST_NAMES_FEMALE = [
    "Ami", "Bhavna", "Chaitali", "Dhara", "Farhana", "Geeta", "Heena", "Ishita",
    "Jinal", "Kinjal", "Leela", "Mansi", "Neha", "Pooja", "Riddhi", "Sneha",
    "Tanvi", "Urvashi", "Vaishali", "Yashvi", "Kokila", "Dakshaben", "Meena", "Parul",
    "Rekha", "Shilpa", "Vandana", "Zoya", "Ayesha", "Fatima", "Deepa", "Kavita",
    "Swati", "Nisha", "Rupal", "Hetvi", "Diya", "Binal", "Priyanka", "Shruti"
]

LAST_NAMES = [
    # Gujarati
    "Patel", "Shah", "Mehta", "Desai", "Joshi", "Trivedi", "Pandya", "Vora", "Parekh", "Zaveri",
    "Sompura", "Bhatt", "Dholakia", "Dave", "Raval", "Barot", "Panchal", "Soni",
    # Muslim
    "Shaikh", "Khan", "Pathan", "Ansari", "Qureshi", "Mansuri", "Saiyed", "Malek", "Mirza",
    # Jain
    "Doshi", "Sanghavi", "Kothari", "Gandhi", "Chhajed", "Lodha",
    # Sindhi
    "Advani", "Ahuja", "Makhija", "Vaswani", "Chawla", "Motwani",
    # Punjabi
    "Singh", "Kaur", "Sharma", "Gill", "Ahluwalia", "Arora",
    # Marathi
    "Kulkarni", "Patil", "Deshmukh", "Shinde", "Gaikwad",
    # South Indian
    "Nair", "Iyer", "Menon", "Rao", "Reddy", "Pillai"
]

SOURCES = ["CCTV", "WIFI", "CELL", "TRANSIT"]

# ---------------------------------------------------------------------------
# 1. Locations Generation (160+ locations)
# ---------------------------------------------------------------------------
def generate_locations():
    locations = []
    loc_id = 1
    
    # Pre-defined landmark names per area
    types_cycle = ["commercial", "retail", "bank", "atm", "petrol_pump", "hospital", "educational", "transit", "park", "restaurant"]
    
    # 5 specific robbery targets
    robbery_targets = [
        {"name": "Ratna Diamond Jewellers", "area": "Manek Chowk", "type": "retail", "open_hour": 10, "close_hour": 21, "capacity": 60},
        {"name": "Apex Commercial Bank", "area": "CG Road", "type": "bank", "open_hour": 9, "close_hour": 18, "capacity": 150},
        {"name": "Highway Fuel Station", "area": "SG Highway", "type": "petrol_pump", "open_hour": 0, "close_hour": 24, "capacity": 80},
        {"name": "Maninagar Express ATM", "area": "Maninagar", "type": "atm", "open_hour": 0, "close_hour": 24, "capacity": 10},
        {"name": "Phoenix Grand Mall", "area": "Vastrapur", "type": "commercial", "open_hour": 10, "close_hour": 22, "capacity": 2500},
    ]
    
    # 3 murder targets
    murder_targets = [
        {"name": "Sabarmati Riverfront Promenade North", "area": "Sabarmati", "type": "park", "open_hour": 6, "close_hour": 23, "capacity": 1000},
        {"name": "Law Garden Woodland Alley", "area": "Law Garden", "type": "park", "open_hour": 6, "close_hour": 22, "capacity": 400},
        {"name": "Kankaria West Quiet Gate", "area": "Kankaria Lake", "type": "park", "open_hour": 6, "close_hour": 22, "capacity": 600},
    ]
    
    area_dict = {a["name"]: a for a in AREAS}
    
    # Add designated incident targets first
    for t in robbery_targets + murder_targets:
        area_info = area_dict[t["area"]]
        locations.append({
            "location_id": f"LOC{loc_id:04d}",
            "name": t["name"],
            "area": t["area"],
            "type": t["type"],
            "latitude": round(area_info["lat"] + random.uniform(-0.003, 0.003), 6),
            "longitude": round(area_info["lon"] + random.uniform(-0.003, 0.003), 6),
            "capacity": t["capacity"],
            "open_hour": t["open_hour"],
            "close_hour": t["close_hour"]
        })
        loc_id += 1

    # Add 2 Residential Hubs per area (open 24/7 for residents)
    for area in AREAS:
        for r_i in range(1, 3):
            locations.append({
                "location_id": f"LOC{loc_id:04d}",
                "name": f"{area['name']} Heritage Society #{r_i}",
                "area": area["name"],
                "type": "residential",
                "latitude": round(area["lat"] + random.uniform(-0.006, 0.006), 6),
                "longitude": round(area["lon"] + random.uniform(-0.006, 0.006), 6),
                "capacity": 1500,
                "open_hour": 0,
                "close_hour": 24
            })
            loc_id += 1
        
    # Generate remaining realistic locations across all areas to reach 165 locations
    loc_names_prefix = [
        "Shivalik", "Titanium", "Mondeal", "Dev", "Samyak", "Maruti", "Akshar",
        "Swastik", "Navkar", "Pramukh", "Siddh", "Ganesh", "Surya", "Aditya"
    ]
    
    for area in AREAS:
        # Create 6-7 locations per area
        for i in range(6):
            ltype = types_cycle[(loc_id + i) % len(types_cycle)]
            pfx = random.choice(loc_names_prefix)
            if ltype == "bank":
                lname = f"{pfx} Cooperative Bank {area['name']}"
                open_h, close_h, cap = 9, 18, 120
            elif ltype == "atm":
                lname = f"{pfx} Quick Cash {area['name']}"
                open_h, close_h, cap = 0, 24, 15
            elif ltype == "petrol_pump":
                lname = f"{pfx} Fuel Point {area['name']}"
                open_h, close_h, cap = 6, 23, 70
            elif ltype == "retail":
                lname = f"{pfx} Plaza Stores {area['name']}"
                open_h, close_h, cap = 10, 21, 200
            elif ltype == "hospital":
                lname = f"{pfx} Care Hospital {area['name']}"
                open_h, close_h, cap = 0, 24, 400
            elif ltype == "educational":
                lname = f"{pfx} Academy {area['name']}"
                open_h, close_h, cap = 8, 17, 800
            elif ltype == "transit":
                lname = f"{area['name']} BRTS Cross Station"
                open_h, close_h, cap = 5, 23, 500
            elif ltype == "park":
                lname = f"{area['name']} Public Garden"
                open_h, close_h, cap = 6, 22, 600
            elif ltype == "restaurant":
                lname = f"{pfx} Dining Pavilion {area['name']}"
                open_h, close_h, cap = 11, 23, 150
            else:
                lname = f"{pfx} Business Hub {area['name']}"
                open_h, close_h, cap = 9, 20, 500

            locations.append({
                "location_id": f"LOC{loc_id:04d}",
                "name": lname,
                "area": area["name"],
                "type": ltype,
                "latitude": round(area["lat"] + random.uniform(-0.012, 0.012), 6),
                "longitude": round(area["lon"] + random.uniform(-0.012, 0.012), 6),
                "capacity": cap,
                "open_hour": open_h,
                "close_hour": close_h
            })
            loc_id += 1

    return locations

# ---------------------------------------------------------------------------
# 2. People Generation (12,000 people)
# ---------------------------------------------------------------------------
def generate_people(num_people=12000):
    people = []
    for pid in range(1, num_people + 1):
        gender = random.choice(["M", "F"])
        fname = random.choice(FIRST_NAMES_MALE if gender == "M" else FIRST_NAMES_FEMALE)
        lname = random.choice(LAST_NAMES)
        age = random.randint(18, 75)
        
        # Age-aligned occupation
        if age < 23:
            occ = "student" if random.random() < 0.8 else random.choice(OCCUPATIONS)
        elif age > 60:
            occ = "retired" if random.random() < 0.75 else random.choice(["shopkeeper", "office worker", "homemaker"])
        else:
            occ = random.choice(OCCUPATIONS)
            
        area = random.choice(AREAS)["name"]
        
        people.append({
            "person_id": f"P{pid:06d}",
            "full_name": f"{fname} {lname}",
            "age": age,
            "gender": gender,
            "occupation": occ,
            "home_area": area
        })
    return people

# ---------------------------------------------------------------------------
# 3. Incidents Generation (5 Robberies, 3 Murders)
# ---------------------------------------------------------------------------
def generate_incidents(locations, people):
    # Retrieve target locations
    loc_by_name = {loc["name"]: loc["location_id"] for loc in locations}
    
    robbery_targets = [
        ("Ratna Diamond Jewellers", "2026-08-12 14:15:00", "Armed daylight robbery of gold and diamond trays"),
        ("Apex Commercial Bank", "2026-08-20 11:30:00", "Vault heist during cash transfer window"),
        ("Highway Fuel Station", "2026-08-28 22:45:00", "Late-night cashier cashbox loot"),
        ("Maninagar Express ATM", "2026-09-04 03:15:00", "ATM cash dispenser gas-cutter breach"),
        ("Phoenix Grand Mall", "2026-09-10 19:20:00", "Luxury electronics counter robbery during rush hour"),
    ]
    
    murder_targets = [
        ("Sabarmati Riverfront Promenade North", "2026-08-16 21:30:00", "Victim found dead near river walkway. Repeated prior contact.", "P000101", "P000102"), # Murder A
        ("Law Garden Woodland Alley", "2026-08-25 22:15:00", "Victim found near quiet park alleyway. Stranger encounter.", "P000201", "P000202"), # Murder B
        ("Kankaria West Quiet Gate", "2026-09-02 23:00:00", "Victim found near secondary gate. Two suspects seen, one had alibi.", "P000301", "P000302") # Murder C (P000302 culprit, P000303 alibi)
    ]
    
    incidents = []
    inc_id = 1
    for r_name, r_time, r_desc in robbery_targets:
        incidents.append({
            "incident_id": f"INC{inc_id:03d}",
            "type": "ROBBERY",
            "location_id": loc_by_name[r_name],
            "reported_time": r_time,
            "victim_person_id": "",
            "description": r_desc
        })
        inc_id += 1
        
    for m_name, m_time, m_desc, victim_id, culprit_id in murder_targets:
        incidents.append({
            "incident_id": f"INC{inc_id:03d}",
            "type": "MURDER",
            "location_id": loc_by_name[m_name],
            "reported_time": m_time,
            "victim_person_id": victim_id,
            "description": m_desc
        })
        inc_id += 1
        
    return incidents

# ---------------------------------------------------------------------------
# Routine Assignment for Clean Baseline
# ---------------------------------------------------------------------------
def setup_person_routines(people, locations):
    area_to_locs = {}
    for loc in locations:
        area_to_locs.setdefault(loc["area"], []).append(loc)
        
    all_locs = locations
    loc_by_id = {loc["location_id"]: loc for loc in locations}
    
    # Identify 24/7 locations for night workers
    locs_24_7 = [loc for loc in locations if loc["open_hour"] == 0 and loc["close_hour"] == 24]
    if not locs_24_7:
        locs_24_7 = locations[:10]
    
    routines = {}
    for p in people:
        home_area = p["home_area"]
        h_candidates = area_to_locs.get(home_area, all_locs)
        res_locs = [l for l in h_candidates if l["type"] == "residential"]
        home_loc = random.choice(res_locs) if res_locs else random.choice(h_candidates)
        
        is_night = (p["occupation"] == "night-shift worker")
        
        # Primary work/study/market location (within 6.5 km of home)
        if is_night:
            # Night workers work at 24/7 facilities (hospitals, fuel points, 24/7 transit)
            work_pool = [
                loc for loc in locs_24_7
                if haversine_km(home_loc["latitude"], home_loc["longitude"], loc["latitude"], loc["longitude"]) <= 7.0
            ] or locs_24_7
            work_loc = random.choice(work_pool)
            third_loc = random.choice(work_pool)
        else:
            # Daytime workers work at daytime open locations
            work_pool = [
                loc for loc in all_locs
                if haversine_km(home_loc["latitude"], home_loc["longitude"], loc["latitude"], loc["longitude"]) <= 6.5
                and loc["location_id"] != home_loc["location_id"]
                and loc["close_hour"] >= 18
            ] or [home_loc]
            work_loc = random.choice(work_pool)
            
            # Third location: leisure, dining, park (open during evening)
            third_pool = [
                loc for loc in all_locs
                if haversine_km(home_loc["latitude"], home_loc["longitude"], loc["latitude"], loc["longitude"]) <= 6.5
                and loc["location_id"] not in (home_loc["location_id"], work_loc["location_id"])
                and loc["close_hour"] >= 21
            ] or [work_loc]
            third_loc = random.choice(third_pool)
            
        # Staggered schedule offset per person (in minutes) to avoid crowd clustering
        stagger_min = random.randint(-45, 45)
        
        routines[p["person_id"]] = {
            "home_loc": home_loc,
            "work_loc": work_loc,
            "third_loc": third_loc,
            "is_night": is_night,
            "stagger_min": stagger_min,
            "home_lat": home_loc["latitude"],
            "home_lon": home_loc["longitude"]
        }
    return routines

# ---------------------------------------------------------------------------
# Generate Baseline Events for One Day
# ---------------------------------------------------------------------------
def generate_day_baseline_events(day_idx, people_subset, routines, start_event_id):
    curr_date = (START_DATE + timedelta(days=day_idx)).date()
    day_events = []
    evt_id = start_event_id
    
    is_weekend = (curr_date.weekday() >= 5)
    
    for p in people_subset:
        pid = p["person_id"]
        r = routines[pid]
        h_loc = r["home_loc"]
        w_loc = r["work_loc"] if not is_weekend else r["third_loc"]
        t_loc = r["third_loc"]
        stagger = r["stagger_min"]
        
        if r["is_night"]:
            # Active at night (20:00 to 07:00), sleep during day
            # Max visits to work = 3 (shift start, break, shift end) -> No loitering (Rule 5 < 4)
            # All night work locations are 24/7 -> No open hours violations (Rule 4 == 0)
            base_slots = [
                (0, 15, w_loc),
                (3, 0, w_loc),
                (5, 45, t_loc),
                (7, 30, h_loc),
                (10, 30, h_loc),
                (13, 30, h_loc),
                (16, 30, h_loc),
                (19, 0, h_loc),
                (20, 45, t_loc),
                (22, 15, w_loc),
                (23, 45, t_loc),
            ]
        else:
            # Daytime active (07:00 to 23:00)
            # Max visits to work = 3 (arrival, midday, checkout) -> No loitering (Rule 5 < 4)
            # Max visits to third_loc = 3 (morning transit, lunch, evening leisure) -> No loitering
            base_slots = [
                (6, 45, h_loc),
                (8, 15, t_loc),
                (9, 45, w_loc),
                (12, 15, w_loc),
                (13, 45, t_loc),
                (16, 15, w_loc),
                (18, 45, t_loc),
                (20, 15, h_loc),
                (21, 30, h_loc),
                (22, 30, h_loc),
                (23, 30, h_loc),
            ]
            
        for base_h, base_m, loc in base_slots:
            # Person-specific stagger + slot jitter uniformly spreads events across time
            total_minutes = base_h * 60 + base_m + stagger + random.randint(-18, 18)
            total_minutes = max(0, min(1439, total_minutes))
            h = total_minutes // 60
            m = total_minutes % 60
            sec = random.randint(0, 59)
            
            # Ensure open hours compliance: if closed, fallback to residential home_loc (24/7)
            if loc["open_hour"] != 0 or loc["close_hour"] != 24:
                if h < loc["open_hour"] or h >= loc["close_hour"]:
                    chosen_loc = h_loc
                else:
                    chosen_loc = loc
            else:
                chosen_loc = loc
                
            lat = round(chosen_loc["latitude"] + random.uniform(-0.0002, 0.0002), 6)
            lon = round(chosen_loc["longitude"] + random.uniform(-0.0002, 0.0002), 6)
            dt_str = f"{curr_date} {h:02d}:{m:02d}:{sec:02d}"
            src = random.choice(SOURCES)
            
            day_events.append({
                "event_id": f"EVT{evt_id:08d}",
                "person_id": pid,
                "timestamp": dt_str,
                "location_id": chosen_loc["location_id"],
                "latitude": lat,
                "longitude": lon,
                "source": src
            })
            evt_id += 1
            
    return day_events, evt_id

# ---------------------------------------------------------------------------
# Plant Ground Truth Anomalies
# ---------------------------------------------------------------------------
def plant_anomalies(locations, people, routines):
    loc_by_id = {loc["location_id"]: loc for loc in locations}
    all_loc_ids = list(loc_by_id.keys())
    
    anomalies_gt = []
    planted_events = []
    
    # 1. 40 same-person-two-places-at-once (1+ km apart within 60s)
    for i in range(1, 41):
        pid = f"P{1000 + i:06d}"
        day = 5 + (i % 30)
        dt_base = START_DATE + timedelta(days=day, hours=10 + (i % 8), minutes=(i * 3) % 50)
        loc1 = loc_by_id[all_loc_ids[i % len(all_loc_ids)]]
        
        # Find loc2 at least 2 km away
        far_locs = [l for l in locations if haversine_km(loc1["latitude"], loc1["longitude"], l["latitude"], l["longitude"]) >= 2.0]
        loc2 = random.choice(far_locs)
        
        t1 = dt_base.strftime("%Y-%m-%d %H:%M:%S")
        t2 = (dt_base + timedelta(seconds=25)).strftime("%Y-%m-%d %H:%M:%S")
        
        dist = haversine_km(loc1["latitude"], loc1["longitude"], loc2["latitude"], loc2["longitude"])
        
        planted_events.append({"person_id": pid, "timestamp": t1, "location_id": loc1["location_id"], "lat": loc1["latitude"], "lon": loc1["longitude"], "source": "CCTV"})
        planted_events.append({"person_id": pid, "timestamp": t2, "location_id": loc2["location_id"], "lat": loc2["latitude"], "lon": loc2["longitude"], "source": "WIFI"})
        
        anomalies_gt.append({
            "anomaly_id": f"ANO_R1_{i:03d}",
            "rule_id": 1,
            "rule_name": "same_person_two_places_at_once",
            "person_ids": [pid],
            "location_id": loc1["location_id"],
            "start_time": t1,
            "end_time": t2,
            "details": f"Distance {dist:.2f} km within 25 seconds"
        })

    # 2. 40 impossible-speed (speed > 120 km/h over 2+ km)
    for i in range(1, 41):
        pid = f"P{1100 + i:06d}"
        day = 6 + (i % 30)
        dt_base = START_DATE + timedelta(days=day, hours=12 + (i % 6), minutes=(i * 5) % 50)
        loc1 = loc_by_id[all_loc_ids[(i * 3) % len(all_loc_ids)]]
        
        # Pick loc2 5 to 10 km away
        far_locs = [l for l in locations if haversine_km(loc1["latitude"], loc1["longitude"], l["latitude"], l["longitude"]) >= 5.0]
        loc2 = random.choice(far_locs)
        dist = haversine_km(loc1["latitude"], loc1["longitude"], loc2["latitude"], loc2["longitude"])
        
        # Travel time 60 seconds -> speed > 300 km/h
        t1 = dt_base.strftime("%Y-%m-%d %H:%M:%S")
        t2 = (dt_base + timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
        spd = speed_kmh(dist, 60)
        
        planted_events.append({"person_id": pid, "timestamp": t1, "location_id": loc1["location_id"], "lat": loc1["latitude"], "lon": loc1["longitude"], "source": "CELL"})
        planted_events.append({"person_id": pid, "timestamp": t2, "location_id": loc2["location_id"], "lat": loc2["latitude"], "lon": loc2["longitude"], "source": "CELL"})
        
        anomalies_gt.append({
            "anomaly_id": f"ANO_R2_{i:03d}",
            "rule_id": 2,
            "rule_name": "impossible_speed",
            "person_ids": [pid],
            "location_id": loc1["location_id"],
            "start_time": t1,
            "end_time": t2,
            "details": f"Speed {spd:.1f} km/h over {dist:.2f} km"
        })

    # 3. 6 crowd gatherings (50 to 300 people at one place within 10 minutes)
    for i in range(1, 7):
        day = 10 + i * 4
        dt_base = START_DATE + timedelta(days=day, hours=16 + (i % 4), minutes=15)
        target_loc = locations[20 + i * 5]
        crowd_size = 75 + i * 20 # 95 to 195 people
        crowd_pids = [f"P{2000 + k:06d}" for k in range(crowd_size)]
        
        t_start = dt_base.strftime("%Y-%m-%d %H:%M:%S")
        t_end = (dt_base + timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S")
        
        for p_idx, cpid in enumerate(crowd_pids):
            evt_time = (dt_base + timedelta(seconds=random.randint(0, 480))).strftime("%Y-%m-%d %H:%M:%S")
            planted_events.append({
                "person_id": cpid,
                "timestamp": evt_time,
                "location_id": target_loc["location_id"],
                "lat": target_loc["latitude"],
                "lon": target_loc["longitude"],
                "source": random.choice(["WIFI", "CCTV"])
            })
            
        anomalies_gt.append({
            "anomaly_id": f"ANO_R3_{i:03d}",
            "rule_id": 3,
            "rule_name": "crowd_gathering",
            "person_ids": crowd_pids[:10], # sample
            "location_id": target_loc["location_id"],
            "start_time": t_start,
            "end_time": t_end,
            "details": f"{crowd_size} people gathered at {target_loc['name']} within 8 minutes"
        })

    # 4. 30 after-hours visits (closed location)
    closed_locs = [l for l in locations if l["open_hour"] >= 8 and l["close_hour"] <= 20]
    for i in range(1, 31):
        pid = f"P{1300 + i:06d}"
        day = 7 + i
        t_visit = (START_DATE + timedelta(days=day, hours=2, minutes=(i * 7) % 55)).strftime("%Y-%m-%d %H:%M:%S")
        loc = closed_locs[i % len(closed_locs)]
        
        planted_events.append({
            "person_id": pid,
            "timestamp": t_visit,
            "location_id": loc["location_id"],
            "lat": loc["latitude"],
            "lon": loc["longitude"],
            "source": "CCTV"
        })
        
        anomalies_gt.append({
            "anomaly_id": f"ANO_R4_{i:03d}",
            "rule_id": 4,
            "rule_name": "after_hours_visit",
            "person_ids": [pid],
            "location_id": loc["location_id"],
            "start_time": t_visit,
            "end_time": t_visit,
            "details": f"Visit at 02:xx to {loc['name']} (Open: {loc['open_hour']}:00-{loc['close_hour']}:00)"
        })

    # 5. 25 loitering (same place 4+ times in 24 hours)
    for i in range(1, 26):
        pid = f"P{1400 + i:06d}"
        day = 12 + i
        loc = locations[15 + (i * 2) % 50]
        dt_day = START_DATE + timedelta(days=day)
        
        timestamps = [
            (dt_day + timedelta(hours=9, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
            (dt_day + timedelta(hours=11, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            (dt_day + timedelta(hours=14, minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
            (dt_day + timedelta(hours=17, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            (dt_day + timedelta(hours=20, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ]
        
        for ts in timestamps:
            planted_events.append({
                "person_id": pid,
                "timestamp": ts,
                "location_id": loc["location_id"],
                "lat": loc["latitude"],
                "lon": loc["longitude"],
                "source": "CCTV"
            })
            
        anomalies_gt.append({
            "anomaly_id": f"ANO_R5_{i:03d}",
            "rule_id": 5,
            "rule_name": "loitering",
            "person_ids": [pid],
            "location_id": loc["location_id"],
            "start_time": timestamps[0],
            "end_time": timestamps[-1],
            "details": f"Visited {loc['name']} 5 times in 11 hours"
        })

    # 6. 30 signal gaps (12+ hour gap for active person with 5+ events/day)
    # Recorded in ground truth - during generation, events between 08:00 and 22:00 for these persons are omitted on that day.
    signal_gap_days = {}
    for i in range(1, 31):
        pid = f"P{1500 + i:06d}"
        day = 8 + i
        signal_gap_days[(pid, day)] = True
        t_gap_start = (START_DATE + timedelta(days=day, hours=7, minutes=0)).strftime("%Y-%m-%d %H:%M:%S")
        t_gap_end = (START_DATE + timedelta(days=day, hours=22, minutes=0)).strftime("%Y-%m-%d %H:%M:%S")
        
        anomalies_gt.append({
            "anomaly_id": f"ANO_R6_{i:03d}",
            "rule_id": 6,
            "rule_name": "signal_gap",
            "person_ids": [pid],
            "location_id": "",
            "start_time": t_gap_start,
            "end_time": t_gap_end,
            "details": f"Complete 15-hour signal gap for regular active person {pid}"
        })

    # 7. 25 far-from-home first visits (>10 km from home)
    for i in range(1, 26):
        pid = f"P{1600 + i:06d}"
        day = 30 + (i % 14) # Late in 45-day cycle
        r = routines[pid]
        
        # Pick location > 10 km from home
        far_locs = [
            l for l in locations
            if haversine_km(r["home_lat"], r["home_lon"], l["latitude"], l["longitude"]) >= 10.0
        ]
        if not far_locs:
            target_loc = max(locations, key=lambda l: haversine_km(r["home_lat"], r["home_lon"], l["latitude"], l["longitude"]))
        else:
            target_loc = random.choice(far_locs)
        dist = haversine_km(r["home_lat"], r["home_lon"], target_loc["latitude"], target_loc["longitude"])
        
        t_visit = (START_DATE + timedelta(days=day, hours=15, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        planted_events.append({
            "person_id": pid,
            "timestamp": t_visit,
            "location_id": target_loc["location_id"],
            "lat": target_loc["latitude"],
            "lon": target_loc["longitude"],
            "source": "CCTV"
        })
        
        anomalies_gt.append({
            "anomaly_id": f"ANO_R7_{i:03d}",
            "rule_id": 7,
            "rule_name": "far_from_home_first_visit",
            "person_ids": [pid],
            "location_id": target_loc["location_id"],
            "start_time": t_visit,
            "end_time": t_visit,
            "details": f"First ever visit to {target_loc['name']} ({dist:.2f} km from home {r['home_loc']['area']})"
        })

    # 8. 5 moving-together groups (3+ people sharing 3+ locations within 5 minutes)
    for i in range(1, 6):
        day = 15 + i * 3
        group_pids = [f"P{1700 + i * 10 + k:06d}" for k in range(3)]
        loc_seq = [locations[30 + i * 3], locations[31 + i * 3], locations[32 + i * 3]]
        
        base_dt = START_DATE + timedelta(days=day, hours=14, minutes=0)
        t_start = base_dt.strftime("%Y-%m-%d %H:%M:%S")
        t_end = ""
        
        for step, sloc in enumerate(loc_seq):
            step_dt = base_dt + timedelta(minutes=step * 20)
            for p_off, gpid in enumerate(group_pids):
                # Within 1-2 minutes of each other
                evt_dt = step_dt + timedelta(minutes=p_off)
                evt_ts = evt_dt.strftime("%Y-%m-%d %H:%M:%S")
                t_end = evt_ts
                planted_events.append({
                    "person_id": gpid,
                    "timestamp": evt_ts,
                    "location_id": sloc["location_id"],
                    "lat": sloc["latitude"],
                    "lon": sloc["longitude"],
                    "source": "CCTV"
                })
                
        anomalies_gt.append({
            "anomaly_id": f"ANO_R8_{i:03d}",
            "rule_id": 8,
            "rule_name": "moving_together",
            "person_ids": group_pids,
            "location_id": loc_seq[0]["location_id"],
            "start_time": t_start,
            "end_time": t_end,
            "details": f"3 people visited 3 locations synchronously within 2 minutes of each other"
        })

    return anomalies_gt, planted_events, signal_gap_days

# ---------------------------------------------------------------------------
# Plant Cases (5 Robberies, 3 Murders)
# ---------------------------------------------------------------------------
def plant_cases(incidents, locations, people):
    loc_by_id = {loc["location_id"]: loc for loc in locations}
    cases_gt = []
    case_events = []
    
    # 5 Robberies
    robbery_configs = [
        {"inc_id": "INC001", "culprit": "P000501", "name": "Ratna Diamond Jewellers", "partner": "P000502", "decoys": ["P000503", "P000504"]},
        {"inc_id": "INC002", "culprit": "P000511", "name": "Apex Commercial Bank", "partner": "P000512", "decoys": ["P000513", "P000514"]},
        {"inc_id": "INC003", "culprit": "P000521", "name": "Highway Fuel Station", "partner": "P000522", "decoys": ["P000523", "P000524"]},
        {"inc_id": "INC004", "culprit": "P000531", "name": "Maninagar Express ATM", "partner": "P000532", "decoys": ["P000533", "P000534"]},
        {"inc_id": "INC005", "culprit": "P000541", "name": "Phoenix Grand Mall", "partner": "P000542", "decoys": ["P000543", "P000544"]},
    ]
    
    inc_dict = {inc["incident_id"]: inc for inc in incidents}
    
    for r_cfg in robbery_configs:
        inc = inc_dict[r_cfg["inc_id"]]
        r_loc = loc_by_id[inc["location_id"]]
        r_time = datetime.strptime(inc["reported_time"], "%Y-%m-%d %H:%M:%S")
        culprit = r_cfg["culprit"]
        partner = r_cfg["partner"]
        
        # 1. Cased the place 2-3 times in prior 72 hours
        case_times = [
            r_time - timedelta(hours=48, minutes=15),
            r_time - timedelta(hours=22, minutes=30),
            r_time - timedelta(hours=6, minutes=45)
        ]
        for ct in case_times:
            case_events.append({
                "person_id": culprit,
                "timestamp": ct.strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": r_loc["location_id"],
                "lat": r_loc["latitude"],
                "lon": r_loc["longitude"],
                "source": "CCTV"
            })
            # Partner also cased once
            case_events.append({
                "person_id": partner,
                "timestamp": ct.strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": r_loc["location_id"],
                "lat": r_loc["latitude"],
                "lon": r_loc["longitude"],
                "source": "CCTV"
            })

        # 2. At scene within 20 mins of report (e.g. 5 mins before)
        scene_time = r_time - timedelta(minutes=5)
        case_events.append({
            "person_id": culprit,
            "timestamp": scene_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": r_loc["location_id"],
            "lat": r_loc["latitude"],
            "lon": r_loc["longitude"],
            "source": "CCTV"
        })
        case_events.append({
            "person_id": partner,
            "timestamp": scene_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": r_loc["location_id"],
            "lat": r_loc["latitude"],
            "lon": r_loc["longitude"],
            "source": "CCTV"
        })

        # 3. Left fast: 5+ km away within 15 minutes
        far_locs = [l for l in locations if haversine_km(r_loc["latitude"], r_loc["longitude"], l["latitude"], l["longitude"]) >= 5.0]
        if not far_locs:
            escape_loc = max(locations, key=lambda l: haversine_km(r_loc["latitude"], r_loc["longitude"], l["latitude"], l["longitude"]))
        else:
            escape_loc = random.choice(far_locs)
        escape_time = r_time + timedelta(minutes=12)
        case_events.append({
            "person_id": culprit,
            "timestamp": escape_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": escape_loc["location_id"],
            "lat": escape_loc["latitude"],
            "lon": escape_loc["longitude"],
            "source": "CELL"
        })
        case_events.append({
            "person_id": partner,
            "timestamp": escape_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": escape_loc["location_id"],
            "lat": escape_loc["latitude"],
            "lon": escape_loc["longitude"],
            "source": "CELL"
        })

        # 4. Went silent 2-4 hours (no events generated during that window)

        # 5. Add 18 innocent bystanders nearby at the scene time
        bystanders = [f"P{3000 + int(r_cfg['inc_id'][-1]) * 100 + b:06d}" for b in range(18)]
        for bpid in bystanders:
            b_time = r_time - timedelta(minutes=random.randint(2, 25))
            case_events.append({
                "person_id": bpid,
                "timestamp": b_time.strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": r_loc["location_id"],
                "lat": r_loc["latitude"] + random.uniform(-0.0005, 0.0005),
                "lon": r_loc["longitude"] + random.uniform(-0.0005, 0.0005),
                "source": "CELL"
            })
            
        # 6. Add 2 red herrings (visited scene, but have legitimate constant presence/no fast escape)
        for rh_id in r_cfg["decoys"]:
            case_events.append({
                "person_id": rh_id,
                "timestamp": (r_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": r_loc["location_id"],
                "lat": r_loc["latitude"],
                "lon": r_loc["longitude"],
                "source": "WIFI"
            })
            # Stays at the scene or nearby for next 2 hours
            case_events.append({
                "person_id": rh_id,
                "timestamp": (r_time + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": r_loc["location_id"],
                "lat": r_loc["latitude"],
                "lon": r_loc["longitude"],
                "source": "WIFI"
            })

        # 7. Add alibi for a key bystander
        alibi_person = bystanders[0]
        # Alibi: bystander was simultaneously on CCTV inside an office/hospital 2 minutes later
        alibi_loc = locations[10]
        case_events.append({
            "person_id": alibi_person,
            "timestamp": (r_time + timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": alibi_loc["location_id"],
            "lat": alibi_loc["latitude"],
            "lon": alibi_loc["longitude"],
            "source": "CCTV"
        })

        cases_gt.append({
            "incident_id": r_cfg["inc_id"],
            "type": "ROBBERY",
            "planted_culprit": culprit,
            "accomplice": partner,
            "decoys": r_cfg["decoys"],
            "alibi_suspects": [alibi_person],
            "description": inc["description"]
        })

    # 3 Murders
    murder_configs = [
        {
            "inc_id": "INC006",
            "victim": "P000101",
            "culprit": "P000102",
            "mode": "A",
            "decoys": ["P000103", "P000104"],
            "alibi_suspect": None
        },
        {
            "inc_id": "INC007",
            "victim": "P000201",
            "culprit": "P000202",
            "mode": "B",
            "decoys": ["P000203", "P000204"],
            "alibi_suspect": None
        },
        {
            "inc_id": "INC008",
            "victim": "P000301",
            "culprit": "P000302",
            "mode": "C",
            "decoys": ["P000304"],
            "alibi_suspect": "P000303"
        }
    ]

    for m_cfg in murder_configs:
        inc = inc_dict[m_cfg["inc_id"]]
        m_loc = loc_by_id[inc["location_id"]]
        m_time = datetime.strptime(inc["reported_time"], "%Y-%m-%d %H:%M:%S")
        victim = m_cfg["victim"]
        culprit = m_cfg["culprit"]
        mode = m_cfg["mode"]

        if mode == "A":
            # Repeated contact with victim earlier (4 co-locations in prior 14 days)
            for d in [12, 9, 5, 2]:
                contact_time = m_time - timedelta(days=d, hours=2)
                c_loc = locations[25 + d]
                for p_id in [victim, culprit]:
                    case_events.append({
                        "person_id": p_id,
                        "timestamp": contact_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "location_id": c_loc["location_id"],
                        "lat": c_loc["latitude"],
                        "lon": c_loc["longitude"],
                        "source": "CCTV"
                    })
        elif mode == "B":
            # Stranger: only with victim at final locations
            pass
        elif mode == "C":
            # Two people with victim at final location (culprit and alibi_suspect)
            alibi_p = m_cfg["alibi_suspect"]
            # Alibi person leaves early and clocks in at hospital with CCTV
            alibi_loc = locations[8]
            case_events.append({
                "person_id": alibi_p,
                "timestamp": (m_time - timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": m_loc["location_id"],
                "lat": m_loc["latitude"],
                "lon": m_loc["longitude"],
                "source": "CELL"
            })
            case_events.append({
                "person_id": alibi_p,
                "timestamp": (m_time + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": alibi_loc["location_id"],
                "lat": alibi_loc["latitude"],
                "lon": alibi_loc["longitude"],
                "source": "CCTV"
            })

        # Final scene interaction
        scene_time = m_time - timedelta(minutes=15)
        # Victim's final event
        case_events.append({
            "person_id": victim,
            "timestamp": scene_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": m_loc["location_id"],
            "lat": m_loc["latitude"],
            "lon": m_loc["longitude"],
            "source": "CCTV"
        })
        # Culprit with victim within 100m and 10min
        case_events.append({
            "person_id": culprit,
            "timestamp": (scene_time + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": m_loc["location_id"],
            "lat": round(m_loc["latitude"] + 0.0003, 6),
            "lon": round(m_loc["longitude"] + 0.0003, 6),
            "source": "CCTV"
        })

        # Victim trail ENDS here. Culprit KEEPS MOVING after
        after_loc1 = locations[40]
        after_loc2 = locations[55]
        case_events.append({
            "person_id": culprit,
            "timestamp": (m_time + timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": after_loc1["location_id"],
            "lat": after_loc1["latitude"],
            "lon": after_loc1["longitude"],
            "source": "CELL"
        })
        case_events.append({
            "person_id": culprit,
            "timestamp": (m_time + timedelta(hours=1, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
            "location_id": after_loc2["location_id"],
            "lat": after_loc2["latitude"],
            "lon": after_loc2["longitude"],
            "source": "CELL"
        })

        # Decoys
        for dec in m_cfg["decoys"]:
            case_events.append({
                "person_id": dec,
                "timestamp": (m_time - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
                "location_id": m_loc["location_id"],
                "lat": m_loc["latitude"] + random.uniform(-0.001, 0.001),
                "lon": m_loc["longitude"] + random.uniform(-0.001, 0.001),
                "source": "CELL"
            })

        cases_gt.append({
            "incident_id": m_cfg["inc_id"],
            "type": "MURDER",
            "victim_id": victim,
            "planted_culprit": culprit,
            "mode": mode,
            "decoys": m_cfg["decoys"],
            "alibi_suspects": [m_cfg["alibi_suspect"]] if m_cfg["alibi_suspect"] else [],
            "description": inc["description"]
        })

    return cases_gt, case_events

# ---------------------------------------------------------------------------
# Calibration & Master Generation
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("TraceHunt Synthetic Data Generator (Ahmedabad, 45 Days)")
    print("=" * 70)
    
    # 1. Generate and save Locations
    locations = generate_locations()
    loc_file = DATASET_DIR / "locations.csv"
    with open(loc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "location_id", "name", "area", "type", "latitude", "longitude",
            "capacity", "open_hour", "close_hour"
        ])
        writer.writeheader()
        writer.writerows(locations)
    print(f"[+] Saved {len(locations)} locations to {loc_file}")

    # 2. Generate and save People (14,000 people to support 45 days x 11 events/day -> ~478 MB)
    people = generate_people(14000)
    people_file = DATASET_DIR / "people.csv"
    with open(people_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "person_id", "full_name", "age", "gender", "occupation", "home_area"
        ])
        writer.writeheader()
        writer.writerows(people)
    print(f"[+] Saved {len(people)} people to {people_file}")

    # 3. Generate and save Incidents
    incidents = generate_incidents(locations, people)
    inc_file = DATASET_DIR / "incidents.csv"
    with open(inc_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "incident_id", "type", "location_id", "reported_time", "victim_person_id", "description"
        ])
        writer.writeheader()
        writer.writerows(incidents)
    print(f"[+] Saved {len(incidents)} incidents to {inc_file}")

    # 4. Setup routines
    routines = setup_person_routines(people, locations)

    # 5. Plant Ground Truth Anomalies & Cases
    print("[*] Generating ground truth anomalies and case scenarios...")
    anomalies_gt, planted_ano_events, signal_gap_days = plant_anomalies(locations, people, routines)
    cases_gt, case_events = plant_cases(incidents, locations, people)

    with open(GROUND_TRUTH_DIR / "anomalies.json", "w", encoding="utf-8") as f:
        json.dump(anomalies_gt, f, indent=2)
    with open(GROUND_TRUTH_DIR / "cases.json", "w", encoding="utf-8") as f:
        json.dump(cases_gt, f, indent=2)
    print(f"[+] Saved {len(anomalies_gt)} planted anomalies to ground_truth/anomalies.json")
    print(f"[+] Saved {len(cases_gt)} planted cases to ground_truth/cases.json")

    # Group planted events by day date string
    extra_events_by_date = {}
    for evt in planted_ano_events + case_events:
        d_str = evt["timestamp"][:10]
        extra_events_by_date.setdefault(d_str, []).append(evt)

    # -----------------------------------------------------------------------
    # Pilot Run: Calibrate exact active people to target 478 MB
    # -----------------------------------------------------------------------
    print("\n[*] Running 1-day pilot run for size calibration...")
    pilot_people = people[:1000]
    pilot_events, _ = generate_day_baseline_events(0, pilot_people, routines, 1)
    
    # Measure sample line length
    sample_header = "event_id,person_id,timestamp,location_id,latitude,longitude,source\n"
    sample_line = f"{pilot_events[0]['event_id']},{pilot_events[0]['person_id']},{pilot_events[0]['timestamp']},{pilot_events[0]['location_id']},{pilot_events[0]['latitude']:.6f},{pilot_events[0]['longitude']:.6f},{pilot_events[0]['source']}\n"
    bytes_per_event = len(sample_line.encode("utf-8"))
    events_per_person_day = len(pilot_events) / len(pilot_people)
    
    print(f"    - Sample row length: ~{bytes_per_event} bytes")
    print(f"    - Events per person/day: {events_per_person_day:.1f}")
    
    # Calculate target events for 478 MB
    target_total_events = int((TARGET_FILE_BYTES - len(sample_header)) / bytes_per_event)
    target_events_per_day = target_total_events // TOTAL_DAYS
    active_people_needed = int(target_events_per_day / events_per_person_day)
    active_people_needed = min(active_people_needed, len(people))
    
    print(f"    - Target total events: {target_total_events:,}")
    print(f"    - Calibrated active people per day: {active_people_needed:,} of {len(people):,}")

    # -----------------------------------------------------------------------
    # Stream Generation Day-by-Day
    # -----------------------------------------------------------------------
    events_file = DATASET_DIR / "movement_events.csv"
    print(f"\n[*] Generating 45 days into {events_file} (chunked stream)...")

    evt_counter = 1
    total_written_events = 0
    
    with open(events_file, "w", newline="", encoding="utf-8") as f:
        # Write header
        f.write("event_id,person_id,timestamp,location_id,latitude,longitude,source\n")
        
        for day in range(TOTAL_DAYS):
            curr_date_str = (START_DATE + timedelta(days=day)).strftime("%Y-%m-%d")
            
            # Select calibrated subset of active people
            active_subset = people[:active_people_needed]
            
            # Filter out people having signal gap today
            active_today = [
                p for p in active_subset
                if not signal_gap_days.get((p["person_id"], day), False)
            ]
            
            day_events, evt_counter = generate_day_baseline_events(day, active_today, routines, evt_counter)
            
            # Merge planted extra events for this day
            extras = extra_events_by_date.get(curr_date_str, [])
            for ex in extras:
                day_events.append({
                    "event_id": f"EVT{evt_counter:08d}",
                    "person_id": ex["person_id"],
                    "timestamp": ex["timestamp"],
                    "location_id": ex["location_id"],
                    "latitude": ex["lat"],
                    "longitude": ex["lon"],
                    "source": ex["source"]
                })
                evt_counter += 1
                
            # Sort strictly by timestamp within the day
            day_events.sort(key=lambda x: x["timestamp"])
            
            # Write chunk
            lines = [
                f"{e['event_id']},{e['person_id']},{e['timestamp']},{e['location_id']},{e['latitude']:.6f},{e['longitude']:.6f},{e['source']}\n"
                for e in day_events
            ]
            f.writelines(lines)
            total_written_events += len(day_events)
            
            if (day + 1) % 9 == 0 or day == TOTAL_DAYS - 1:
                curr_size = os.path.getsize(events_file)
                print(f"    - Day {day + 1:02d}/45: {total_written_events:,} events written ({curr_size / 1e6:.1f} MB)")

    # -----------------------------------------------------------------------
    # Size Fine-Tuning & Verification
    # -----------------------------------------------------------------------
    final_size = os.path.getsize(events_file)
    print(f"\n[*] Checking final size: {final_size:,} bytes")
    
    # If size is slightly below 460MB or slightly above 500MB, adjust safely
    if final_size < MIN_TARGET_BYTES:
        deficit = (MIN_TARGET_BYTES + 5000000) - final_size
        print(f"[*] Fine-tuning: appending {deficit:,} bytes of trailing valid home events...")
        with open(events_file, "a", encoding="utf-8") as f:
            bytes_added = 0
            pad_idx = 0
            while bytes_added < deficit:
                p = people[pad_idx % len(people)]
                r = routines[p["person_id"]]
                day = pad_idx % TOTAL_DAYS
                dt = START_DATE + timedelta(days=day, hours=12, minutes=(pad_idx % 60), seconds=(pad_idx * 7) % 60)
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                lat = r["home_loc"]["latitude"]
                lon = r["home_loc"]["longitude"]
                line = f"EVT{evt_counter:08d},{p['person_id']},{ts_str},{r['home_loc']['location_id']},{lat:.6f},{lon:.6f},CELL\n"
                f.write(line)
                bytes_added += len(line.encode("utf-8"))
                evt_counter += 1
                total_written_events += 1
                pad_idx += 1

    final_size = os.path.getsize(events_file)
    blocks = math.ceil(final_size / HDFS_BLOCK_SIZE)
    
    print("=" * 70)
    print(f"RESULT:")
    print(f"  Final File Size: {final_size:,} bytes ({final_size / (1024*1024):.2f} MB)")
    print(f"  Target Range:    {MIN_TARGET_BYTES:,} to {MAX_TARGET_BYTES:,} bytes")
    print(f"  HDFS Block Size: {HDFS_BLOCK_SIZE:,} bytes (128 MB)")
    print(f"  Expected Blocks: ceil({final_size} / {HDFS_BLOCK_SIZE}) = {blocks}")
    print(f"  Total Rows:      {total_written_events:,}")
    print("=" * 70)
    assert MIN_TARGET_BYTES <= final_size <= MAX_TARGET_BYTES, f"Size {final_size} out of bounds!"
    assert blocks == 4, f"Blocks {blocks} != 4!"
    print("[SUCCESS] movement_events.csv generated successfully and satisfies all constraints.")

if __name__ == "__main__":
    main()
