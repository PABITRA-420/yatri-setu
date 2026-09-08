"""
Yatri Setu Real-Data Ingestion Layer (Milestone 6B).

All ingestors produce normalized Observation records with strict
data provenance: source, provider_mode, timestamp, confidence, data_quality.

Provider Modes:
  REAL      – Connected to a live external or first-party API
  MOCK      – Deterministic simulation; no external dependency
  CACHED    – Previously fetched real data served from cache
  ESTIMATED – Derived / inferred from correlated signals
  MISSING   – Signal unavailable; flagged for alerting
"""
from app.services.ingestion.base_ingestor import (
    ProviderMode,
    BaseIngestor,
    IngestedObservation,
)

__all__ = ["ProviderMode", "BaseIngestor", "IngestedObservation"]
