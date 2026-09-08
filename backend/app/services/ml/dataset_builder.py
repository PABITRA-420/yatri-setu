"""
ML Dataset Builder (Milestone 6B).

Consolidates historical observations from the synthetic dataset and/or real
ingestors into a clean ML-ready training matrix with full data provenance.

Dataset Modes:
  SYNTHETIC  – All records from the deterministic synthetic generator (Seed 42).
  REAL       – All records from live real ingestors (requires live connections).
  MIXED      – Combination of REAL + SYNTHETIC records with clear per-record provenance.

IMPORTANT:
  - Synthetic records are NEVER presented as real data.
  - Each returned record preserves source, provider_mode, and data_quality.
  - ML models MUST NOT be trained exclusively on synthetic data without disclosure.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from app.data.historical_dataset import generate_historical_dataset
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.ml.dataset_splitter import ChronologicalDatasetSplitter


@dataclass
class DatasetBuildResult:
    """
    Result of a complete ML dataset build operation with provenance tracking.
    """
    total_records: int
    dataset_mode: str  # "SYNTHETIC" | "REAL" | "MIXED"
    date_range: Dict[str, str]
    destinations: List[str]
    feature_names: List[str]
    features: List[Dict[str, Any]]           # Feature rows (X)
    targets: List[float]                     # Target values (y)
    split: Dict[str, Any]                    # TRAIN / VALIDATION / TEST indices and metadata
    real_record_count: int = 0
    synthetic_record_count: int = 0
    missing_signal_count: int = 0
    built_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


class MLDatasetBuilder:
    """
    Builds ML-ready feature matrices from the available historical observation data.

    Currently supports:
      1. SYNTHETIC mode: Uses the deterministic 2023 synthetic dataset (Seed 42).
      2. REAL mode: Would use real ingestor data when available (not yet wired).

    The system is explicitly designed to be upgraded to MIXED mode once real
    ingestor data accumulates sufficient records for ML training.
    """

    MINIMUM_RECORDS_FOR_ML = 365  # Minimum observations needed to justify ML training

    def __init__(self):
        self._feature_builder = StandardFeatureBuilder()
        self._splitter = ChronologicalDatasetSplitter()

    def build_synthetic_dataset(self) -> DatasetBuildResult:
        """
        Build an ML dataset from the deterministic synthetic historical dataset.

        NOTE: This dataset is for DEVELOPMENT and EVALUATION only.
        DO NOT train a production-facing ML model exclusively from this data.
        The resulting DatasetBuildResult.dataset_mode is explicitly 'SYNTHETIC'.
        """
        observations = generate_historical_dataset()

        feature_rows = self._feature_builder.build_features(observations)
        targets = [row["target_pressure"] for row in feature_rows]
        feature_names = self._feature_builder.get_feature_names()

        # Build split indices (chronological, no shuffling)
        split_result = self._splitter.split(observations)

        dates = [obs.date for obs in observations]
        destinations = sorted(set(obs.destination_id for obs in observations))

        return DatasetBuildResult(
            total_records=len(observations),
            dataset_mode="SYNTHETIC",
            date_range={"start": min(dates), "end": max(dates)},
            destinations=destinations,
            feature_names=feature_names,
            features=feature_rows,
            targets=targets,
            split=split_result,
            real_record_count=0,
            synthetic_record_count=len(observations),
            missing_signal_count=0,
            notes=(
                "SYNTHETIC DEMO DATA: Built from deterministic synthetic generator (Seed 42). "
                "This dataset is for development and baseline evaluation only. "
                "ML models trained on this data MUST be labeled 'TRAINED ON SYNTHETIC DATA' "
                "and MUST NOT be presented as production-grade models."
            ),
        )

    def get_dataset_summary(self, result: DatasetBuildResult) -> Dict[str, Any]:
        """Return a human-readable summary of the built dataset."""
        split = result.split
        return {
            "dataset_mode": result.dataset_mode,
            "total_records": result.total_records,
            "real_records": result.real_record_count,
            "synthetic_records": result.synthetic_record_count,
            "date_range": result.date_range,
            "destinations": result.destinations,
            "feature_count": len(result.feature_names),
            "feature_names": result.feature_names,
            "split_sizes": {
                "train": split.get("train_count", 0),
                "validation": split.get("validation_count", 0),
                "test": split.get("test_count", 0),
            },
            "split_dates": {
                "train": {"start": split.get("train_start"), "end": split.get("train_end")},
                "validation": {"start": split.get("val_start"), "end": split.get("val_end")},
                "test": {"start": split.get("test_start"), "end": split.get("test_end")},
            },
            "ml_eligible": result.total_records >= self.MINIMUM_RECORDS_FOR_ML,
            "notes": result.notes,
            "built_at": result.built_at.isoformat(),
        }


# Module-level singleton
ml_dataset_builder = MLDatasetBuilder()
