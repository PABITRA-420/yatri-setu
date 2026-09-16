from fastapi import APIRouter
from app.api.v1 import (
    destinations, itinerary, homestays, safety,
    hosts, experiences, panchayat, impact, pressure, admin,
    ml_admin, ml_forecast, demand, trips,
)

api_router = APIRouter()
api_router.include_router(destinations.router)
api_router.include_router(itinerary.router)
api_router.include_router(homestays.router)
api_router.include_router(safety.router)
api_router.include_router(hosts.router)
api_router.include_router(experiences.router)
api_router.include_router(panchayat.router)
api_router.include_router(impact.router)
api_router.include_router(pressure.router)
api_router.include_router(admin.router)
api_router.include_router(ml_admin.router)
api_router.include_router(ml_forecast.router)
api_router.include_router(demand.router)
api_router.include_router(trips.router)
