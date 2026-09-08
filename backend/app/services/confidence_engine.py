"""
Confidence Engine for Destination Pressure Intelligence (Milestone 5).
Calculates multi-dimensional crowd confidence from:
1. Signal availability (missing signals detection)
2. Data freshness
3. Provider reliability (MOCK vs CACHED vs REAL)
4. Cross-signal agreement (inter-signal variance)
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import math
from app.services.data_sources.base import DataSourceReading
from app.models.observation import DataQuality


class ConfidenceEngine:
    """
    Evaluates evidence quality and reliability across multi-signal data sources.
    Produces composite confidence (0.0 to 1.0) and qualitative health classifications.
    """

    TOTAL_EXPECTED_SIGNALS: int = 8

    def calculate_confidence(
        self,
        readings: List[DataSourceReading],
        total_expected: int = 8
    ) -> Dict[str, Any]:
        """
        Calculates multi-dimensional crowd confidence score.
        """
        if not readings:
            return {
                "confidence": 0.0,
                "signals_available": 0,
                "signals_total": total_expected,
                "data_quality": DataQuality.DEGRADED.value,
                "cross_signal_agreement": 0.0,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }

        # 1. Signal Availability Score
        available_readings = [r for r in readings if r.available]
        signals_available = len(available_readings)
        availability_ratio = min(1.0, signals_available / float(total_expected))

        # Exponential penalty if less than half signals available
        if availability_ratio < 0.5:
            availability_score = availability_ratio * 0.6
        else:
            availability_score = availability_ratio

        # 2. Provider Reliability Score
        # REAL: 0.98, CACHED: 0.90, MOCK: 0.85
        mode_weights = {
            "REAL": 0.98,
            "CACHED": 0.90,
            "MOCK": 0.85
        }
        reliability_scores = [
            mode_weights.get(r.provider_mode.upper(), 0.80) * r.confidence
            for r in available_readings
        ]
        provider_reliability = (
            sum(reliability_scores) / len(reliability_scores)
            if reliability_scores else 0.5
        )

        # 3. Data Freshness Score
        # For mock/simulation, data is fresh (1.0). In production, penalize staleness.
        freshness_score = 0.95

        # 4. Cross-Signal Agreement Score
        # Measure standard deviation across available core normalized pressure values
        values = [r.value for r in available_readings]
        if len(values) >= 3:
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = math.sqrt(variance)

            # Std dev of 0-15: high harmony (1.0)
            # Std dev of 15-35: moderate spread (0.85 - 0.70)
            # Std dev > 35: acute divergence (0.60)
            if std_dev <= 15.0:
                cross_signal_agreement = 1.0
            elif std_dev <= 35.0:
                cross_signal_agreement = max(0.65, 1.0 - ((std_dev - 15.0) / 20.0) * 0.35)
            else:
                cross_signal_agreement = 0.60
        else:
            cross_signal_agreement = 0.75

        # Composite Confidence Formula
        raw_composite = (
            (0.35 * availability_score) +
            (0.25 * provider_reliability) +
            (0.20 * freshness_score) +
            (0.20 * cross_signal_agreement)
        )

        confidence = round(max(0.05, min(0.99, raw_composite)), 2)

        # Determine Data Quality tier
        if confidence >= 0.85 and signals_available >= 7:
            data_quality = DataQuality.HIGH.value
        elif confidence >= 0.70 and signals_available >= 5:
            data_quality = DataQuality.MEDIUM.value
        elif confidence >= 0.50 and signals_available >= 3:
            data_quality = DataQuality.LOW.value
        else:
            data_quality = DataQuality.DEGRADED.value

        return {
            "confidence": confidence,
            "signals_available": signals_available,
            "signals_total": total_expected,
            "data_quality": data_quality,
            "cross_signal_agreement": round(cross_signal_agreement, 2),
            "availability_score": round(availability_score, 2),
            "provider_reliability": round(provider_reliability, 2),
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }


confidence_engine = ConfidenceEngine()
