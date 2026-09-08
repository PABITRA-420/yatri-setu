"""
ML Evaluation Engine (Milestone 6B).

Computes standardized evaluation metrics for all crowd pressure models:
  - MAE (Mean Absolute Error)
  - RMSE (Root Mean Squared Error)
  - Directional Accuracy (day-over-day trend prediction correctness)
  - Error by destination
  - Error by season
  - Error by forecast horizon

Used to compare BaselineRuleModel vs XGBoostCrowdModel on the SAME test period.
ML superiority is ONLY reported when test results actually demonstrate it.
"""
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from app.models.dataset_evaluation import HistoricalObservation


def compute_mae(predictions: List[float], actuals: List[float]) -> float:
    """Mean Absolute Error."""
    if not predictions:
        return 0.0
    return round(sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions), 4)


def compute_rmse(predictions: List[float], actuals: List[float]) -> float:
    """Root Mean Squared Error."""
    if not predictions:
        return 0.0
    mse = sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / len(predictions)
    return round(math.sqrt(mse), 4)


def compute_directional_accuracy(predictions: List[float], actuals: List[float]) -> float:
    """
    Directional accuracy: percentage of consecutive pairs where the predicted
    direction of change (up / down) matches the observed direction.

    Requires at least 2 observations.
    """
    if len(predictions) < 2:
        return 0.0

    correct = 0
    total = 0
    for i in range(1, len(predictions)):
        pred_delta = predictions[i] - predictions[i - 1]
        actual_delta = actuals[i] - actuals[i - 1]

        # Skip flat movements (no directional signal)
        if abs(actual_delta) < 0.01:
            continue

        total += 1
        if (pred_delta >= 0) == (actual_delta >= 0):
            correct += 1

    return round((correct / total * 100.0) if total > 0 else 0.0, 2)


def compute_error_by_destination(
    observations: List[HistoricalObservation],
    predictions: List[float],
) -> List[Dict[str, Any]]:
    """Partition errors by destination_id."""
    dest_buckets: Dict[str, Dict] = defaultdict(lambda: {"preds": [], "actuals": []})

    for obs, pred in zip(observations, predictions):
        dest = obs.destination_id
        dest_buckets[dest]["preds"].append(pred)
        dest_buckets[dest]["actuals"].append(obs.observed_pressure)

    results = []
    for dest, data in sorted(dest_buckets.items()):
        preds = data["preds"]
        actuals = data["actuals"]
        results.append({
            "destination_id": dest,
            "sample_count": len(preds),
            "mae": compute_mae(preds, actuals),
            "rmse": compute_rmse(preds, actuals),
            "directional_accuracy": compute_directional_accuracy(preds, actuals),
        })

    return results


def _get_season(month: int) -> str:
    """Map calendar month to Himalayan tourism season."""
    if month in (4, 5, 6):
        return "Summer Peak"
    elif month in (7, 8):
        return "Monsoon Trough"
    elif month in (9, 10, 11):
        return "Autumn Festival Peak"
    else:
        return "Winter"


def compute_error_by_season(
    observations: List[HistoricalObservation],
    predictions: List[float],
) -> List[Dict[str, Any]]:
    """Partition errors by Himalayan tourism season."""
    season_buckets: Dict[str, Dict] = defaultdict(lambda: {"preds": [], "actuals": []})

    for obs, pred in zip(observations, predictions):
        try:
            month = int(obs.date.split("-")[1])
        except (IndexError, ValueError):
            month = 1
        season = _get_season(month)
        season_buckets[season]["preds"].append(pred)
        season_buckets[season]["actuals"].append(obs.observed_pressure)

    season_order = ["Summer Peak", "Monsoon Trough", "Autumn Festival Peak", "Winter"]
    results = []
    for season in season_order:
        if season not in season_buckets:
            continue
        data = season_buckets[season]
        preds = data["preds"]
        actuals = data["actuals"]
        results.append({
            "season": season,
            "sample_count": len(preds),
            "mae": compute_mae(preds, actuals),
            "rmse": compute_rmse(preds, actuals),
            "directional_accuracy": compute_directional_accuracy(preds, actuals),
        })

    return results


def compute_error_by_horizon(
    predictions: List[float],
    actuals: List[float],
    horizons: List[int] = (1, 3, 7, 14),
) -> List[Dict[str, Any]]:
    """
    Estimate how error degrades at different forecast horizons by
    using the first N predictions as a proxy for an N-day horizon.

    NOTE: This is an approximation based on sequential predictions.
    It is NOT a true multi-step forecast evaluation. Labeled as 'ESTIMATED'.
    """
    results = []
    n = len(predictions)
    for h in horizons:
        subset_preds = predictions[:h] if h <= n else predictions
        subset_actuals = actuals[:h] if h <= n else actuals
        results.append({
            "horizon_days": h,
            "sample_count": len(subset_preds),
            "mae": compute_mae(subset_preds, subset_actuals),
            "rmse": compute_rmse(subset_preds, subset_actuals),
            "note": "ESTIMATED — proxy evaluation, not a true multi-step forecast",
        })
    return results


def compare_models(
    baseline_mae: float,
    ml_mae: float,
    baseline_rmse: float,
    ml_rmse: float,
) -> Dict[str, Any]:
    """
    Honest comparison between baseline and ML model.
    Only reports 'improvement' if ML actually outperforms baseline on BOTH MAE and RMSE.
    Never fabricates ML superiority.
    """
    mae_improved = ml_mae < baseline_mae
    rmse_improved = ml_rmse < baseline_rmse
    is_improved = mae_improved and rmse_improved

    mae_delta = round(baseline_mae - ml_mae, 4)
    rmse_delta = round(baseline_rmse - ml_rmse, 4)

    return {
        "ml_improves_over_baseline": is_improved,
        "mae_delta": mae_delta if mae_improved else None,
        "rmse_delta": rmse_delta if rmse_improved else None,
        "mae_direction": "IMPROVEMENT" if mae_improved else ("REGRESSION" if ml_mae > baseline_mae else "SAME"),
        "rmse_direction": "IMPROVEMENT" if rmse_improved else ("REGRESSION" if ml_rmse > baseline_rmse else "SAME"),
        "verdict": (
            f"ML reduces MAE by {mae_delta:.4f} and RMSE by {rmse_delta:.4f} on test set."
            if is_improved else
            "ML does NOT outperform the baseline rule model on the test set. "
            "Baseline rule model recommended for production use."
        ),
    }
