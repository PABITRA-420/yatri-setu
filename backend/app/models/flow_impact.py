from typing import List
from pydantic import BaseModel

class DestinationFlowImpact(BaseModel):
    destination_id: str
    destination_name: str
    is_congested_hub: bool
    redirected_tourists_count: int
    estimated_bookings: int
    estimated_local_revenue_inr: int
    experience_bookings: int
    crowd_pressure_reduction_percent: float
    community_fund_generated_inr: int
    beneficiary_villages: List[str]
    narrative_summary: str
    key_metrics: List[dict]
