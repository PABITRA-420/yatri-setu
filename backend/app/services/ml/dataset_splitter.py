"""
Dataset Splitter — Strict Chronological Partitioning (Milestone 6A/6B).

Ensures time-series observations are partitioned without temporal leakage.
NEVER random-shuffles observations. Maintains causal train → validation → test ordering.

Split boundaries (2023 synthetic dataset):
  TRAIN:      2023-01-01 to 2023-08-31  (~66.6% of records)
  VALIDATION: 2023-09-01 to 2023-10-31  (~16.7% of records)
  TEST:       2023-11-01 to 2023-12-31  (~16.7% of records)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.dataset_evaluation import HistoricalObservation


class BaseDatasetSplitter(ABC):
    """Abstract splitter interface."""

    @abstractmethod
    def split(self, observations: List[HistoricalObservation]) -> Dict[str, Any]:
        """Splits observation list into train, validation, and test subsets with metadata."""


class ChronologicalDatasetSplitter(BaseDatasetSplitter):
    """
    Strict time-ordered dataset splitter.

    Guarantees:
    - No random shuffling (preserves temporal causality)
    - Causal boundaries: train data always precedes validation, which precedes test
    - Feature leakage is impossible: no future data appears in any preceding split
    - Documents split dates and sample counts for full reproducibility
    """

    def __init__(
        self,
        train_end_date: str = "2023-08-31",
        val_end_date: str = "2023-10-31"
    ):
        self.train_end_date = train_end_date
        self.val_end_date = val_end_date

    def split(self, observations: List[HistoricalObservation]) -> Dict[str, Any]:
        """
        Partition observations chronologically into train / validation / test.

        Returns a rich metadata dict including:
          - train_obs, validation_obs, test_obs: the three observation lists
          - train_count, validation_count, test_count: sizes
          - train_start, train_end, val_start, val_end, test_start, test_end: date boundaries
          - train_indices, validation_indices, test_indices: original positional indices
          - no_shuffle_verified: always True (chronological ordering enforced)
        """
        def get_date(o: Any) -> str:
            return getattr(o, "date", None) or getattr(o, "date_bucket", "")

        def get_dest(o: Any) -> str:
            return getattr(o, "destination_id", "")

        # Sort observations strictly chronologically (date + destination)
        sorted_obs = sorted(observations, key=lambda x: (get_date(x), get_dest(x)))

        # Determine effective split dates
        all_dates = sorted(set(get_date(o) for o in sorted_obs if get_date(o)))
        train_cutoff = self.train_end_date
        val_cutoff = self.val_end_date

        if all_dates:
            min_d, max_d = all_dates[0], all_dates[-1]
            # If dates are completely outside the default 2023 range, calculate chronological quantile cutoffs
            if min_d > self.val_end_date or max_d < self.train_end_date:
                t_idx = int(len(all_dates) * 0.70)
                v_idx = int(len(all_dates) * 0.85)
                train_cutoff = all_dates[min(t_idx, len(all_dates) - 1)]
                val_cutoff = all_dates[min(v_idx, len(all_dates) - 1)]

        train_obs: List[Any] = []
        val_obs: List[Any] = []
        test_obs: List[Any] = []

        train_indices: List[int] = []
        val_indices: List[int] = []
        test_indices: List[int] = []

        for i, obs in enumerate(sorted_obs):
            o_date = get_date(obs)
            if o_date <= train_cutoff:
                train_obs.append(obs)
                train_indices.append(i)
            elif o_date <= val_cutoff:
                val_obs.append(obs)
                val_indices.append(i)
            else:
                test_obs.append(obs)
                test_indices.append(i)

        train_dates = [get_date(o) for o in train_obs]
        val_dates = [get_date(o) for o in val_obs]
        test_dates = [get_date(o) for o in test_obs]


        return {
            # Observation subsets
            "train": train_obs,
            "validation": val_obs,
            "test": test_obs,
            # Counts
            "train_count": len(train_obs),
            "validation_count": len(val_obs),
            "test_count": len(test_obs),
            # Date boundaries
            "train_start": min(train_dates) if train_dates else None,
            "train_end": max(train_dates) if train_dates else None,
            "val_start": min(val_dates) if val_dates else None,
            "val_end": max(val_dates) if val_dates else None,
            "test_start": min(test_dates) if test_dates else None,
            "test_end": max(test_dates) if test_dates else None,
            # Indices
            "train_indices": train_indices,
            "validation_indices": val_indices,
            "test_indices": test_indices,
            # Integrity guarantees
            "no_shuffle_verified": True,
            "split_method": "CHRONOLOGICAL_CAUSAL",
            "split_boundaries": {
                "train_end": self.train_end_date,
                "val_end": self.val_end_date,
            },
        }
