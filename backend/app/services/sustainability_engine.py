"""
Sustainability & Tourism Impact Engine for Yatri Setu (Smart India Hackathon 2026)
Computes deterministic 0-100 sustainability scorecard and local community economic impact.
Ensures SIH judges can inspect exactly how rural and alternative travel benefits local Himalayan ecosystems.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SustainabilityFactor(BaseModel):
    name: str
    category: str
    points_earned: int
    max_points: int
    description: str

class TourismImpact(BaseModel):
    estimated_local_spend_inr: int
    direct_village_economy_percent: int = Field(..., ge=0, le=100)
    local_businesses_supported: int
    crowd_pressure_reduction_percent: int
    community_fund_contribution_inr: int
    carbon_saved_vs_private_car_kg: float

class SustainabilityScorecard(BaseModel):
    sustainability_score: int = Field(..., ge=0, le=100)
    sustainability_classification: str # EXCELLENT, HIGH, MODERATE, NEEDS_IMPROVEMENT
    factors: List[SustainabilityFactor]
    tourism_impact: TourismImpact
    eco_summary: str

def calculate_sustainability(
    destination_id: str,
    total_budget_inr: int,
    crowd_score: int,
    num_days: int = 3,
    prefers_shared_transit: bool = True,
    homestay_selected: bool = True
) -> SustainabilityScorecard:
    """
    Deterministic calculation of sustainability scorecard and community impact.
    """
    factors: List[SustainabilityFactor] = []

    # 1. Homestay / Community Lodging Factor (Max 25 pts)
    if homestay_selected:
        homestay_pts = 25
        homestay_desc = "100% of lodging spend stays with verified village host family, preventing corporate capital flight."
    else:
        homestay_pts = 10
        homestay_desc = "Standard commercial hotel selected with partial local employment."
    factors.append(SustainabilityFactor(
        name="Community Homestay Lodging",
        category="Economic Retention",
        points_earned=homestay_pts,
        max_points=25,
        description=homestay_desc
    ))

    # 2. Local Food & Rural Artisan Sourcing (Max 20 pts)
    # Rural destinations like Lava, Lolegaon, Rishop, Kalimpong score high
    is_rural_circuit = destination_id.lower() in ["lava", "lolegaon", "rishop", "kalimpong", "mirik"]
    food_pts = 20 if is_rural_circuit else 15
    factors.append(SustainabilityFactor(
        name="Local Cuisine & Craft Cooperatives",
        category="Hyperlocal Supply Chain",
        points_earned=food_pts,
        max_points=20,
        description="Daily meals planned at certified village organic kitchens and Lepcha/Gorkha craft centers."
    ))

    # 3. Shared & Low-Emission Transit (Max 20 pts)
    if prefers_shared_transit:
        transit_pts = 20
        transit_desc = "Shared mountain jeeps and forest walking trails utilized, cutting per-passenger emissions by ~55%."
    else:
        transit_pts = 8
        transit_desc = "Private chartered mountain vehicle utilized with higher carbon footprint."
    factors.append(SustainabilityFactor(
        name="Low-Impact Mountain Mobility",
        category="Carbon Reduction",
        points_earned=transit_pts,
        max_points=20,
        description=transit_desc
    ))

    # 4. Overtourism Pressure Relief (Max 20 pts)
    # Crowd score <= 45 gives 20 pts; 46-70 gives 14 pts; > 70 gives 6 pts
    if crowd_score <= 45:
        crowd_pts = 20
        crowd_desc = "Disperses tourist traffic into high-capacity rural tranquility, alleviating pressure on congested hubs."
    elif crowd_score <= 70:
        crowd_pts = 14
        crowd_desc = "Moderate tourist density with balanced municipal waste and road load."
    else:
        crowd_pts = 6
        crowd_desc = "High destination density; careful off-peak scheduling required to minimize municipal strain."
    factors.append(SustainabilityFactor(
        name="Overtourism Alleviation",
        category="Tourist Flow Management",
        points_earned=crowd_pts,
        max_points=20,
        description=crowd_desc
    ))

    # 5. Eco-Practices & Heritage Stewardship (Max 15 pts)
    eco_pts = 15 if is_rural_circuit else 12
    factors.append(SustainabilityFactor(
        name="Zero-Plastic & Trail Stewardship",
        category="Ecological Conservation",
        points_earned=eco_pts,
        max_points=15,
        description="Commitment to local spring water refills, zero single-use plastics, and leave-no-trace trails."
    ))

    total_score = sum(f.points_earned for f in factors)

    if total_score >= 85:
        classification = "EXCELLENT"
    elif total_score >= 70:
        classification = "HIGH"
    elif total_score >= 50:
        classification = "MODERATE"
    else:
        classification = "NEEDS_IMPROVEMENT"

    # Deterministic Economic & Environmental Impact
    local_retention_ratio = 0.88 if is_rural_circuit else 0.72
    estimated_local_spend = int(total_budget_inr * local_retention_ratio)
    local_businesses = min(12, max(3, num_days * (3 if is_rural_circuit else 2)))
    crowd_reduction = max(10, 100 - crowd_score) if crowd_score > 60 else 75
    community_fund = int(total_budget_inr * 0.02) # 2% earmarked for Gram Panchayat conservation fund
    carbon_saved = round(num_days * (14.5 if prefers_shared_transit else 3.0), 1)

    impact = TourismImpact(
        estimated_local_spend_inr=estimated_local_spend,
        direct_village_economy_percent=int(local_retention_ratio * 100),
        local_businesses_supported=local_businesses,
        crowd_pressure_reduction_percent=crowd_reduction,
        community_fund_contribution_inr=community_fund,
        carbon_saved_vs_private_car_kg=carbon_saved
    )

    eco_summary = (
        f"This trip achieves an {classification} sustainability rating ({total_score}/100). "
        f"Approximately ₹{estimated_local_spend:,} ({int(local_retention_ratio * 100)}%) remains directly within "
        f"the local village ecosystem, supporting {local_businesses} indigenous livelihoods while saving "
        f"{carbon_saved} kg CO2."
    )

    return SustainabilityScorecard(
        sustainability_score=total_score,
        sustainability_classification=classification,
        factors=factors,
        tourism_impact=impact,
        eco_summary=eco_summary
    )
