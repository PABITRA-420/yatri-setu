"""
ML Dataset Builder (Milestone 6B & Milestone 10 / Prompt 3).

Consolidates historical observations from genuine PostgreSQL/SQLite storage
and/or synthetic benchmark generators into a clean ML-ready training matrix
with strict data provenance and leakage prevention.

Dataset Modes:
  REAL       – All records from genuine persisted observations (no synthetic injection).
  SYNTHETIC  – All records from the deterministic synthetic generator (Seed 42).
  MIXED      – Combination of REAL + SYNTHETIC records with transparent per-record provenance.

IMPORTANT RULES:
  - Synthetic records are NEVER presented as real data.
  - In REAL mode, unmeasured signals remain NULL; no synthetic substitution occurs.
  - Strict leakage prevention: Target timestamps are separated from Feature timestamps.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel
from app.models.historical import DatasetMetadata, SignalProvenanceRecord
from app.data.historical_dataset import generate_historical_dataset
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.ml.dataset_splitter import ChronologicalDatasetSplitter

logger = logging.getLogger(__name__)


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
    metadata: Optional[DatasetMetadata] = None
    built_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""


class MLDatasetBuilder:
    """
    Builds ML-ready feature matrices from available historical observations
    with support for REAL, SYNTHETIC, and MIXED dataset modes, leakage prevention,
    and signal-level provenance tracking.
    """

    MINIMUM_RECORDS_FOR_ML = 365  # Minimum observations needed to justify ML training

    def __init__(self):
        self._feature_builder = StandardFeatureBuilder()
        self._splitter = ChronologicalDatasetSplitter()

    def build_synthetic_dataset(self, target_horizon: int = 0) -> DatasetBuildResult:
        """
        Build an ML dataset from the deterministic synthetic historical dataset (Seed 42).

        NOTE: This dataset is for DEVELOPMENT and BENCHMARKING only.
        The resulting DatasetBuildResult.dataset_mode is explicitly 'SYNTHETIC'.
        """
        observations = generate_historical_dataset()

        if target_horizon <= 0:
            feature_rows = self._feature_builder.build_features(observations)
            targets = [row["target_pressure"] for row in feature_rows]
            split_result = self._splitter.split(observations)
            dates = [obs.date for obs in observations]
            destinations = sorted(set(obs.destination_id for obs in observations))
            leakage_verified = True
        else:
            # Pair observation at T with observation at T + target_horizon
            paired_obs, feature_rows, targets = self._pair_forecasting_observations(
                observations=observations,
                target_horizon=target_horizon
            )
            split_result = self._splitter.split(paired_obs)
            dates = [row["feature_timestamp"] for row in feature_rows]
            destinations = sorted(set(row["destination_id"] for row in feature_rows))
            leakage_verified = all(r["feature_timestamp"] < r["target_timestamp"] for r in feature_rows)

        feature_names = self._feature_builder.get_feature_names()

        meta = DatasetMetadata(
            dataset_mode="SYNTHETIC",
            destination_count=len(destinations),
            destinations=destinations,
            row_count=len(feature_rows),
            time_start=min(dates) if dates else "",
            time_end=max(dates) if dates else "",
            real_row_count=0,
            synthetic_row_count=len(feature_rows),
            mixed_row_count=0,
            signal_availability_percentages={
                "footfall": 100.0,
                "accommodation_occupancy": 100.0,
                "booking_demand": 100.0,
                "search_demand": 100.0,
                "traffic_pressure": 100.0,
                "weather_pressure": 100.0,
                "holiday_pressure": 100.0,
                "event_pressure": 100.0,
                "current_crowd_pressure": 100.0
            },
            provenance_counts={"SYNTHETIC": len(feature_rows) * 9},
            unavailable_signal_count=0,
            ml_eligible=False,  # Synthetic data is not eligible for production models
            target_horizon_days=target_horizon,
            leakage_prevention_verified=leakage_verified,
            notes=(
                "SYNTHETIC DEMO DATA: Built from deterministic synthetic generator (Seed 42). "
                "This dataset is for development and baseline evaluation only. "
                "ML models trained on this data MUST be labeled 'TRAINED ON SYNTHETIC DATA' "
                "and MUST NOT be presented as production-grade models."
            )

        )

        return DatasetBuildResult(
            total_records=len(feature_rows),
            dataset_mode="SYNTHETIC",
            date_range={"start": min(dates) if dates else "", "end": max(dates) if dates else ""},
            destinations=destinations,
            feature_names=feature_names,
            features=feature_rows,
            targets=targets,
            split=split_result,
            real_record_count=0,
            synthetic_record_count=len(feature_rows),
            missing_signal_count=0,
            metadata=meta,
            notes=meta.notes,
        )

    def build_historical_dataset(
        self,
        destinations: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        target_horizon: int = 1,
        db: Optional[Session] = None
    ) -> DatasetBuildResult:
        """
        Build an ML dataset containing ONLY genuine persisted observations.
        NEVER silently injects synthetic data. Missing signals remain None.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            query = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            )

            if destinations:
                clean_dests = [d.lower().strip() for d in destinations]
                query = query.filter(HistoricalObservationModel.destination_id.in_(clean_dests))
            if start_date:
                query = query.filter(HistoricalObservationModel.date_bucket >= start_date)
            if end_date:
                query = query.filter(HistoricalObservationModel.date_bucket <= end_date)

            models = query.order_by(
                HistoricalObservationModel.date_bucket.asc(),
                HistoricalObservationModel.destination_id.asc()
            ).all()

            if not models:
                meta = DatasetMetadata(
                    dataset_mode="REAL",
                    destination_count=0,
                    destinations=[],
                    row_count=0,
                    time_start="",
                    time_end="",
                    real_row_count=0,
                    synthetic_row_count=0,
                    mixed_row_count=0,
                    signal_availability_percentages={},
                    provenance_counts={},
                    unavailable_signal_count=0,
                    ml_eligible=False,
                    target_horizon_days=target_horizon,
                    leakage_prevention_verified=True,
                    notes="REAL DATASET: Zero genuine historical observations available in storage; no synthetic rows injected."
                )
                return DatasetBuildResult(
                    total_records=0,
                    dataset_mode="REAL",
                    date_range={"start": "", "end": ""},
                    destinations=[],
                    feature_names=self._feature_builder.get_feature_names(),
                    features=[],
                    targets=[],
                    split={"train": [], "validation": [], "test": [], "train_count": 0, "validation_count": 0, "test_count": 0},
                    real_record_count=0,
                    synthetic_record_count=0,
                    missing_signal_count=0,
                    metadata=meta,
                    notes=meta.notes
                )

            # Forecasting pairing with leakage prevention
            paired_obs, feature_rows, targets = self._pair_forecasting_observations(
                observations=models,
                target_horizon=target_horizon
            )

            split_result = self._splitter.split(paired_obs) if paired_obs else {}
            dates = [r["feature_timestamp"] for r in feature_rows]
            unique_dests = sorted(set(r["destination_id"] for r in feature_rows))
            feature_names = self._feature_builder.get_feature_names()

            # Calculate signal availability & provenance counts
            signal_avail, prov_counts, missing_slots = self._audit_dataset_signals(models)

            leakage_verified = all(r["feature_timestamp"] < r["target_timestamp"] for r in feature_rows) if target_horizon > 0 else True

            meta = DatasetMetadata(
                dataset_mode="REAL",
                destination_count=len(unique_dests),
                destinations=unique_dests,
                row_count=len(feature_rows),
                time_start=min(dates) if dates else "",
                time_end=max(dates) if dates else "",
                real_row_count=len(feature_rows),
                synthetic_row_count=0,
                mixed_row_count=0,
                signal_availability_percentages=signal_avail,
                provenance_counts=prov_counts,
                unavailable_signal_count=missing_slots,
                ml_eligible=len(feature_rows) >= self.MINIMUM_RECORDS_FOR_ML,
                target_horizon_days=target_horizon,
                leakage_prevention_verified=leakage_verified,
                notes=(
                    f"REAL HISTORICAL DATASET: {len(feature_rows)} time-aligned observations. "
                    f"Target horizon H={target_horizon} days. Zero synthetic data injected."
                )
            )

            return DatasetBuildResult(
                total_records=len(feature_rows),
                dataset_mode="REAL",
                date_range={"start": min(dates) if dates else "", "end": max(dates) if dates else ""},
                destinations=unique_dests,
                feature_names=feature_names,
                features=feature_rows,
                targets=targets,
                split=split_result,
                real_record_count=len(feature_rows),
                synthetic_record_count=0,
                missing_signal_count=missing_slots,
                metadata=meta,
                notes=meta.notes
            )
        finally:
            if close_db and db:
                db.close()

    def build_mixed_dataset(
        self,
        destinations: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        target_horizon: int = 1,
        db: Optional[Session] = None
    ) -> DatasetBuildResult:
        """
        Build a combined dataset merging genuine historical observations with
        synthetic benchmark records ONLY when explicitly requested.
        Preserves signal and row-level provenance.
        """
        # 1. Fetch real dataset
        real_result = self.build_historical_dataset(
            destinations=destinations,
            start_date=start_date,
            end_date=end_date,
            target_horizon=target_horizon,
            db=db
        )

        # 2. Fetch synthetic dataset
        synth_result = self.build_synthetic_dataset(target_horizon=target_horizon)

        # Filter synthetic by destinations if specified
        synth_features = synth_result.features
        synth_targets = synth_result.targets
        if destinations:
            clean_dests = set(d.lower().strip() for d in destinations)
            filtered_features = []
            filtered_targets = []
            for f, t in zip(synth_features, synth_targets):
                if f["destination_id"] in clean_dests:
                    filtered_features.append(f)
                    filtered_targets.append(t)
            synth_features = filtered_features
            synth_targets = filtered_targets

        # 3. Combine features and targets with explicit origin tagging
        combined_features = []
        for row in real_result.features:
            r = dict(row)
            r["row_provenance"] = "REAL"
            combined_features.append(r)

        for row in synth_features:
            r = dict(row)
            r["row_provenance"] = "SYNTHETIC"
            combined_features.append(r)

        combined_targets = list(real_result.targets) + list(synth_targets)
        combined_dests = sorted(set(real_result.destinations + synth_result.destinations))

        all_dates = [r["feature_timestamp"] for r in combined_features]

        meta = DatasetMetadata(
            dataset_mode="MIXED",
            destination_count=len(combined_dests),
            destinations=combined_dests,
            row_count=len(combined_features),
            time_start=min(all_dates) if all_dates else "",
            time_end=max(all_dates) if all_dates else "",
            real_row_count=len(real_result.features),
            synthetic_row_count=len(synth_features),
            mixed_row_count=len(combined_features),
            signal_availability_percentages={
                "real_signal_availability": real_result.metadata.signal_availability_percentages if real_result.metadata else {},
                "synthetic_signal_availability": synth_result.metadata.signal_availability_percentages if synth_result.metadata else {}
            },
            provenance_counts={
                "REAL_ROWS": len(real_result.features),
                "SYNTHETIC_ROWS": len(synth_features)
            },
            unavailable_signal_count=real_result.missing_signal_count,
            ml_eligible=False,  # Mixed datasets require explicit evaluation
            target_horizon_days=target_horizon,
            leakage_prevention_verified=True,
            notes=(
                f"MIXED DATASET: {len(real_result.features)} genuine historical rows + "
                f"{len(synth_features)} synthetic benchmark rows. Provenance is preserved on every row."
            )
        )

        return DatasetBuildResult(
            total_records=len(combined_features),
            dataset_mode="MIXED",
            date_range={"start": min(all_dates) if all_dates else "", "end": max(all_dates) if all_dates else ""},
            destinations=combined_dests,
            feature_names=self._feature_builder.get_feature_names() + ["row_provenance"],
            features=combined_features,
            targets=combined_targets,
            split={"train_count": len(combined_features), "validation_count": 0, "test_count": 0},
            real_record_count=len(real_result.features),
            synthetic_record_count=len(synth_features),
            missing_signal_count=real_result.missing_signal_count,
            metadata=meta,
            notes=meta.notes
        )

    def _pair_forecasting_observations(
        self,
        observations: List[Any],
        target_horizon: int
    ) -> Tuple[List[Any], List[Dict[str, Any]], List[float]]:
        """
        Aligns observations chronologically per destination, setting the target
        at date T to the observed crowd pressure at date T + target_horizon.
        Enforces strict leakage prevention: features at T contain NO information from T + target_horizon.
        """
        def get_date(o: Any) -> str:
            return getattr(o, "date", None) or getattr(o, "date_bucket", "")

        def get_dest(o: Any) -> str:
            return (getattr(o, "destination_id", "")).lower().strip()

        # Group by destination
        by_dest: Dict[str, List[Any]] = {}
        for obs in observations:
            dest = get_dest(obs)
            if dest:
                by_dest.setdefault(dest, []).append(obs)

        paired_obs: List[Any] = []
        feature_rows: List[Dict[str, Any]] = []
        targets: List[float] = []

        for dest, obs_list in by_dest.items():
            # Sort chronologically
            sorted_obs = sorted(obs_list, key=lambda x: get_date(x))
            date_map = {get_date(o): o for o in sorted_obs}

            for obs in sorted_obs:
                t_date_str = get_date(obs)
                if not t_date_str:
                    continue

                if target_horizon == 0:
                    # Same day regression
                    row = self._feature_builder.build_feature_row(
                        obs=obs,
                        feature_timestamp=t_date_str,
                        target_timestamp=t_date_str,
                        target_horizon_days=0
                    )
                    paired_obs.append(obs)
                    feature_rows.append(row)
                    targets.append(row["target_pressure"])
                else:
                    # Forecasting H days ahead
                    try:
                        t_date = datetime.strptime(t_date_str, "%Y-%m-%d").date()
                        future_date = t_date + timedelta(days=target_horizon)
                        future_date_str = future_date.strftime("%Y-%m-%d")
                    except ValueError:
                        continue

                    # Look up future ground truth observation
                    future_obs = date_map.get(future_date_str)
                    if future_obs is not None:
                        future_target = getattr(future_obs, "current_crowd_pressure", None)
                        if future_target is None:
                            future_target = getattr(future_obs, "observed_pressure", None)

                        if future_target is not None:
                            # CRITICAL LEAKAGE CHECK: verify future_date > t_date
                            assert future_date_str > t_date_str, "Temporal leakage violation!"

                            # Build feature row ONLY using information from observation at T
                            row = self._feature_builder.build_feature_row(
                                obs=obs,
                                target_pressure=future_target,
                                feature_timestamp=t_date_str,
                                target_timestamp=future_date_str,
                                target_horizon_days=target_horizon
                            )
                            paired_obs.append(obs)
                            feature_rows.append(row)
                            targets.append(future_target)

        return paired_obs, feature_rows, targets

    def _audit_dataset_signals(
        self,
        observations: List[HistoricalObservationModel]
    ) -> Tuple[Dict[str, float], Dict[str, int], int]:
        """Audits signal availability and provenance mode distribution across rows."""
        total = len(observations)
        if total == 0:
            return {}, {}, 0

        signals = [
            "footfall",
            "accommodation_occupancy",
            "booking_demand",
            "search_demand",
            "traffic_pressure",
            "weather_pressure",
            "holiday_pressure",
            "event_pressure",
            "current_crowd_pressure"
        ]

        avail_counts = {s: 0 for s in signals}
        prov_counts: Dict[str, int] = {}
        missing_slots = 0

        for obs in observations:
            for sig in signals:
                val = getattr(obs, sig, None)
                if val is not None:
                    avail_counts[sig] += 1
                else:
                    missing_slots += 1

            if obs.signal_provenance_json and isinstance(obs.signal_provenance_json, dict):
                for _, prov in obs.signal_provenance_json.items():
                    mode = prov.get("provider_mode", "UNKNOWN") if isinstance(prov, dict) else getattr(prov, "provider_mode", "UNKNOWN")
                    prov_counts[mode] = prov_counts.get(mode, 0) + 1

        pcts = {k: round((v / total) * 100.0, 1) for k, v in avail_counts.items()}
        return pcts, prov_counts, missing_slots

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

    def get_dataset_metadata(self, result: DatasetBuildResult) -> DatasetMetadata:
        """Returns standard DatasetMetadata for audit and inspection."""
        if result.metadata:
            return result.metadata

        return DatasetMetadata(
            dataset_mode=result.dataset_mode,
            destination_count=len(result.destinations),
            destinations=result.destinations,
            row_count=result.total_records,
            time_start=result.date_range.get("start", ""),
            time_end=result.date_range.get("end", ""),
            real_row_count=result.real_record_count,
            synthetic_row_count=result.synthetic_record_count,
            mixed_row_count=result.total_records if result.dataset_mode == "MIXED" else 0,
            ml_eligible=result.total_records >= self.MINIMUM_RECORDS_FOR_ML and result.dataset_mode == "REAL",
            notes=result.notes
        )


# Module-level singleton
ml_dataset_builder = MLDatasetBuilder()
