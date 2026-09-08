from fastapi import APIRouter
from app.models.flow_impact import DestinationFlowImpact
from app.services.flow_impact_service import flow_impact_service

router = APIRouter(prefix="/impact", tags=["Tourism Flow & Economic Impact"])

@router.get("/destination/{destination_id}", response_model=DestinationFlowImpact)
def get_destination_flow_impact(destination_id: str):
    """
    Returns redistribution analytics, showing tourists diverted from high-pressure hubs
    to rural destinations and the resulting local revenue and community funds generated.
    """
    return flow_impact_service.calculate_destination_impact(destination_id)
