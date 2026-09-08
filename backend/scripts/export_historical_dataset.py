"""
Export script for Yatri Setu Historical Crowd Dataset (Milestone 6A).
Generates and writes data/historical/crowd_observations.csv.
"""

import sys
import os

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.data.historical_dataset import export_dataset_to_csv, get_historical_dataset


def main():
    root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
    out_path = os.path.join(root_dir, "data", "historical", "crowd_observations.csv")
    
    print(f"[Yatri Setu] Generating historical crowd dataset...")
    dataset = get_historical_dataset()
    print(f"[Yatri Setu] Generated {len(dataset)} records across 6 destinations.")
    
    saved_path = export_dataset_to_csv(out_path, dataset)
    print(f"[Yatri Setu] Successfully exported dataset to: {saved_path}")


if __name__ == "__main__":
    main()
