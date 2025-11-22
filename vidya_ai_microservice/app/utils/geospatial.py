"""Geospatial helper utilities."""

from __future__ import annotations

import math
from typing import Optional

from ..schemas import GPSCoordinate


def haversine_distance_km(point_a: GPSCoordinate, point_b: GPSCoordinate) -> float:
    """Compute great-circle distance between two coordinates."""

    radius = 6371.0
    lat1 = math.radians(point_a.lat)
    lon1 = math.radians(point_a.lon)
    lat2 = math.radians(point_b.lat)
    lon2 = math.radians(point_b.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def gps_deviation(metadata_location: Optional[GPSCoordinate], submission_location: Optional[GPSCoordinate]) -> Optional[float]:
    if metadata_location and submission_location:
        return haversine_distance_km(metadata_location, submission_location)
    return None


__all__ = ["gps_deviation", "haversine_distance_km"]
