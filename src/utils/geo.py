"""
Geographical and distance utilities for TraceHunt.
Uses the Haversine formula to calculate distances between coordinates.
"""
import math

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def speed_kmh(dist_km: float, time_diff_sec: float) -> float:
    """Calculate speed in km/h given distance in km and time in seconds."""
    if time_diff_sec <= 0:
        return 9999.0  # Instantaneous movement / infinite speed
    return (dist_km / time_diff_sec) * 3600.0
