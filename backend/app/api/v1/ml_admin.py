"""
ML Admin API Endpoints (Milestone 6B).

GET /api/admin/ml/status          — Active model info, dataset mode, training metrics
GET /api/admin/ml/feature-importance — Ranked feature importances from the trained model
POST /api/admin/ml/train           — Trigger a training run (admin only)
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.ml.model_registry import model_registry
from app.services.ml.xgboost_model import xgboost_crowd_model
from app.services.ml.training_service import ml_training_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/ml", tags=["ML Admin"])


# ─── Response Models ──────────────────────────────────────────────────────────

class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float
    rank: int


class FeatureImportanceResponse(BaseModel):
    model_name: str
    model_version: str
    backend: str
    dataset_mode: str
    features: List[FeatureImportanceItem]
    total_features: int
    note: str


class ModelMetrics(BaseModel):
    test_mae: Optional[float] = None
    test_rmse: Optional[float] = None
    test_directional_accuracy: Optional[float] = None
    val_mae: Optional[float] = None
    val_rmse: Optional[float] = None


class MLModelStatus(BaseModel):
    model_available: bool
    model_name: str
    model_version: str
    backend: str
    training_dataset: str
    dataset_mode: str
    is_trained: bool
    last_trained: Optional[str] = None
    metrics: Optional[ModelMetrics] = None
    baseline_model: str
    fallback_active: bool
    synthetic_data_warning: Optional[str] = None


class TrainRequest(BaseModel):
    dataset_mode: str = Field(
        default="SYNTHETIC",
        description="Dataset mode: SYNTHETIC | REAL | MIXED. Only SYNTHETIC is currently supported.",
    )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/status", response_model=MLModelStatus)
def get_ml_status():
    """
    Returns the current ML model status including training dataset provenance,
    metrics on the test set, and whether fallback to the baseline is active.
    """
    is_trained = xgboost_crowd_model.is_trained
    meta = xgboost_crowd_model.get_metadata()

    metrics = None
    last_trained = None
    dataset_mode = "NOT_TRAINED"
    training_dataset = "None"
    synthetic_warning = None

    if is_trained and meta:
        metrics = ModelMetrics(
            test_mae=meta.get("test_mae"),
            test_rmse=meta.get("test_rmse"),
            test_directional_accuracy=meta.get("test_directional_accuracy"),
            val_mae=meta.get("val_mae"),
            val_rmse=meta.get("val_rmse"),
        )
        last_trained = meta.get("training_date")
        dataset_mode = meta.get("dataset_mode", "UNKNOWN")
        training_dataset = meta.get("dataset_version", "Unknown")
        synthetic_warning = meta.get("synthetic_data_warning")

    return MLModelStatus(
        model_available=is_trained,
        model_name=xgboost_crowd_model.name,
        model_version=xgboost_crowd_model.version,
        backend=xgboost_crowd_model.backend,
        training_dataset=training_dataset,
        dataset_mode=dataset_mode,
        is_trained=is_trained,
        last_trained=last_trained,
        metrics=metrics,
        baseline_model="baseline_rule_v2 v2.0.0",
        fallback_active=not is_trained,
        synthetic_data_warning=synthetic_warning,
    )


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
def get_feature_importance():
    """
    Returns ranked feature importances from the trained tree-based model.
    Requires the ML model to be trained first (POST /api/admin/ml/train).
    """
    if not xgboost_crowd_model.is_trained:
        raise HTTPException(
            status_code=404,
            detail=(
                "ML model has not been trained yet. "
                "Call POST /api/admin/ml/train first to train the model."
            ),
        )

    importances = xgboost_crowd_model.feature_importances
    meta = xgboost_crowd_model.get_metadata()

    ranked = [
        FeatureImportanceItem(feature=name, importance=imp, rank=i + 1)
        for i, (name, imp) in enumerate(importances.items())
    ]

    return FeatureImportanceResponse(
        model_name=xgboost_crowd_model.name,
        model_version=xgboost_crowd_model.version,
        backend=xgboost_crowd_model.backend,
        dataset_mode=meta.get("dataset_mode", "UNKNOWN"),
        features=ranked,
        total_features=len(ranked),
        note=(
            "Feature importances are computed from the trained tree ensemble. "
            "Higher values indicate stronger predictive signal. "
            + (meta.get("synthetic_data_warning") or "")
        ),
    )


@router.post("/train")
def trigger_training(req: TrainRequest):
    """
    Triggers a full ML training run. Admin-only operation.
    Training is synchronous and may take 10–60 seconds depending on dataset size.
    Dataset mode must be 'SYNTHETIC' (REAL/MIXED not yet supported).
    """
    logger.info(f"Admin triggered ML training: dataset_mode={req.dataset_mode}")
    report = ml_training_service.train(dataset_mode=req.dataset_mode)
    if "error" in report:
        raise HTTPException(status_code=400, detail=report["error"])
    return report


@router.get("/models")
def list_registered_models():
    """Lists all models currently registered in the ModelRegistry."""
    return {"models": model_registry.list_models()}
