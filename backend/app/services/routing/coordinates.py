"""
Destination coordinates and naming constants for Yatri Setu circuit routing.
"""

from typing import Dict, Tuple

CIRCUIT_COORDINATES: Dict[str, Tuple[float, float]] = {
    "darjeeling": (27.0410, 88.2663),
    "kalimpong": (27.0594, 88.4695),
    "lava": (27.0864, 88.6603),
    "lolegaon": (27.0142, 88.5583),
    "rishop": (27.1065, 88.6496),
    "mirik": (26.9011, 88.1755),
}

CIRCUIT_NAMES: Dict[str, str] = {
    "darjeeling": "Darjeeling",
    "kalimpong": "Kalimpong",
    "lava": "Lava",
    "lolegaon": "Lolegaon",
    "rishop": "Rishop",
    "mirik": "Mirik",
}
