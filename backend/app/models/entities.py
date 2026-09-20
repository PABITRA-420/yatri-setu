"""
SQLAlchemy Entity Models for Yatri Setu (Milestone 5)
Supports PostgreSQL (with PostGIS coordinates) and local SQLite fallback.
Defines all 16 core platform entities.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base

# 1. Destination Entity
class DestinationModel(Base):
    __tablename__ = "destinations"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    state = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom_wkt = Column(String(128), nullable=True) # Point(lng lat) PostGIS-compatible WKT
    carrying_capacity = Column(Integer, default=5000)
    current_pressure = Column(Float, default=20.0)
    is_rural = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    attractions = relationship("AttractionModel", back_populates="destination", cascade="all, delete-orphan")
    homestays = relationship("HomestayModel", back_populates="destination", cascade="all, delete-orphan")
    historical_observations = relationship("HistoricalObservationModel", back_populates="destination", cascade="all, delete-orphan")


# 2. Attraction Entity
class AttractionModel(Base):
    __tablename__ = "attractions"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    category = Column(String(64), default="scenic")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geom_wkt = Column(String(128), nullable=True)
    capacity_per_hour = Column(Integer, default=500)

    destination = relationship("DestinationModel", back_populates="attractions")


# 3. Host Entity
class HostModel(Base):
    __tablename__ = "hosts"

    id = Column(String(64), primary_key=True, index=True)
    full_name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    panchayat_name = Column(String(128), nullable=False)
    village = Column(String(128), nullable=False)
    state = Column(String(64), nullable=False)
    verification_status = Column(String(32), default="VERIFIED")
    created_at = Column(DateTime, default=datetime.utcnow)

    homestays = relationship("HomestayModel", back_populates="host")


# 4. Homestay Entity
class HomestayModel(Base):
    __tablename__ = "homestays"

    id = Column(String(64), primary_key=True, index=True)
    host_id = Column(String(64), ForeignKey("hosts.id"), nullable=False, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    title = Column(String(128), nullable=True)
    tagline = Column(String(256), nullable=True)
    address = Column(String(256), nullable=True)
    room_type = Column(String(64), default="Standard Room")
    total_rooms = Column(Integer, default=2)
    max_guests = Column(Integer, default=6)
    price_per_night = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, default=5.0)
    reviews_count = Column(Integer, default=0)
    panchayat_verified = Column(Boolean, default=True)
    verification_status = Column(String(32), default="VERIFIED")
    is_published = Column(Boolean, default=True)
    village = Column(String(128), nullable=True)
    panchayat_name = Column(String(128), nullable=True)
    special_activity = Column(String(256), nullable=True)
    amenities_json = Column(JSON, nullable=True)
    images_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    host = relationship("HostModel", back_populates="homestays")
    destination = relationship("DestinationModel", back_populates="homestays")
    bookings = relationship("BookingModel", back_populates="homestay")


# 5. Experience Entity
class ExperienceModel(Base):
    __tablename__ = "experiences"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    title = Column(String(128), nullable=False)
    category = Column(String(64), default="cultural")
    price_inr = Column(Float, nullable=False)
    duration_hours = Column(Float, default=2.5)
    sustainability_score = Column(Float, default=90.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# 6. Booking Entity
class BookingModel(Base):
    __tablename__ = "bookings"

    id = Column(String(64), primary_key=True, index=True)
    homestay_id = Column(String(64), ForeignKey("homestays.id"), nullable=False, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    guest_name = Column(String(128), nullable=False)
    traveler_phone = Column(String(32), nullable=True)
    traveler_email = Column(String(128), nullable=True)
    emergency_contact = Column(String(32), nullable=True)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    guests_count = Column(Integer, default=2)
    rooms_booked = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    host_earning = Column(Float, nullable=False) # 90%
    platform_fee = Column(Float, nullable=False) # 5%
    community_fund = Column(Float, nullable=False) # 5%
    status = Column(String(32), default="CONFIRMED")
    failure_reason = Column(String(64), nullable=True)
    failure_detail = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True, index=True)
    digital_pass_qr_payload = Column(Text, nullable=True)
    transitions_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    homestay = relationship("HomestayModel", back_populates="bookings")


# 7. Availability Entity
class AvailabilityModel(Base):
    __tablename__ = "availability"
    __table_args__ = (
        UniqueConstraint("homestay_id", "date", name="uq_homestay_date_inventory"),
    )

    id = Column(String(64), primary_key=True, index=True)
    homestay_id = Column(String(64), ForeignKey("homestays.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    total_units = Column(Integer, default=2)
    booked_units = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    rooms_available = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 8. Unified CrowdObservation Entity
class CrowdObservationModel(Base):
    __tablename__ = "crowd_observations"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    signal_type = Column(String(64), nullable=False, index=True)
    raw_value = Column(Float, nullable=False)
    normalized_value = Column(Float, nullable=False) # 0 to 100
    unit = Column(String(32), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String(128), nullable=False)
    provider_mode = Column(String(16), default="MOCK") # MOCK, REAL, CACHED
    confidence = Column(Float, default=0.9)
    data_quality = Column(String(16), default="HIGH") # HIGH, MEDIUM, LOW, DEGRADED
    metadata_json = Column(JSON, nullable=True)


# 9. CrowdPrediction Entity (for Forecast Accuracy calculation)
class CrowdPredictionModel(Base):
    __tablename__ = "crowd_predictions"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, index=True)
    predicted_pressure = Column(Float, nullable=False)
    actual_pressure = Column(Float, nullable=True)
    absolute_error = Column(Float, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)


# 10. WeatherObservation Entity
class WeatherObservationModel(Base):
    __tablename__ = "weather_observations"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    temperature_c = Column(Float, nullable=False)
    condition = Column(String(64), nullable=False)
    comfort_index = Column(Float, default=80.0)
    provider_mode = Column(String(16), default="MOCK")
    timestamp = Column(DateTime, default=datetime.utcnow)


# 11. TrafficObservation Entity
class TrafficObservationModel(Base):
    __tablename__ = "traffic_observations"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    corridor_name = Column(String(128), nullable=False)
    delay_minutes = Column(Float, default=0.0)
    congestion_level = Column(String(32), default="NORMAL")
    provider_mode = Column(String(16), default="MOCK")
    timestamp = Column(DateTime, default=datetime.utcnow)


# 12. DemandObservation Entity (Leading Indicator)
class DemandObservationModel(Base):
    __tablename__ = "demand_observations"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    search_count = Column(Integer, default=100)
    unique_searchers = Column(Integer, default=80)
    booking_conversion = Column(Float, default=0.12)
    period_change_percent = Column(Float, default=5.0)
    trend = Column(String(32), default="STABLE") # RISING, STABLE, DECLINING
    timestamp = Column(DateTime, default=datetime.utcnow)


# 13. Event Entity
class EventModel(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    expected_footfall = Column(Integer, default=1000)
    radius_km = Column(Float, default=10.0)
    category = Column(String(64), default="cultural")
    source = Column(String(128), default="District Tourism Office")
    confidence = Column(Float, default=0.9)


# 14. Holiday Entity
class HolidayModel(Base):
    __tablename__ = "holidays"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    holiday_type = Column(String(32), default="NATIONAL") # NATIONAL, REGIONAL, FESTIVAL, LONG_WEEKEND
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    surge_multiplier = Column(Float, default=1.3)
    applicable_states = Column(String(128), default="West Bengal, Sikkim")


# 15. Intervention Entity
class InterventionModel(Base):
    __tablename__ = "interventions"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    intervention_type = Column(String(64), nullable=False)
    intensity = Column(Float, default=0.5)
    target_absorber_id = Column(String(64), nullable=True)
    simulated_reduction = Column(Float, default=0.0)
    redirected_visitors = Column(Integer, default=0)
    economic_gain_inr = Column(Float, default=0.0)
    applied_at = Column(DateTime, default=datetime.utcnow)


# 16. SafetyIncident Entity
class SafetyIncidentModel(Base):
    __tablename__ = "safety_incidents"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    trip_id = Column(String(64), nullable=True)
    traveler_session_id = Column(String(128), nullable=True)
    user_name = Column(String(128), nullable=True)
    user_phone = Column(String(32), nullable=True, index=True)
    incident_type = Column(String(64), default="SOS") # MEDICAL, SOS, WEATHER_HAZARD, ROAD_BLOCK
    severity = Column(String(32), default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(32), default="DELIVERED") # CREATED, DELIVERED, ACKNOWLEDGED, RESPONDING, ESCALATED, RESOLVED
    notes = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    idempotency_key = Column(String(128), nullable=True, index=True)
    audit_trail_json = Column(JSON, nullable=True)
    notifications_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# 17. First-Party Demand Event Entity (Milestone 7A)
class DemandEventModel(Base):
    __tablename__ = "demand_events"

    id = Column(String(64), primary_key=True, index=True)
    destination_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True) # search, booking, availability, trip_start, destination_selection, alternative_acceptance
    session_id = Column(String(128), nullable=True, index=True)
    user_id = Column(String(128), nullable=True, index=True)
    metadata_json = Column(JSON, nullable=True)
    source = Column(String(128), default="YATRI_SETU_NETWORK", nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# 18. Historical Tourism & Crowd Observation Entity (Milestone 10 / Prompt 3)
class HistoricalObservationModel(Base):
    __tablename__ = "historical_crowd_observations"

    id = Column(String(64), primary_key=True, index=True) # Deterministic hash: {destination_id}:{date_bucket}:{dataset_mode}
    destination_id = Column(String(64), ForeignKey("destinations.id"), nullable=False, index=True)
    observed_at = Column(DateTime, nullable=False, index=True)
    date_bucket = Column(String(10), nullable=False, index=True) # YYYY-MM-DD canonical daily alignment

    # Signals are explicitly nullable - missing signals remain NULL/None, never manufactured
    footfall = Column(Float, nullable=True)
    accommodation_occupancy = Column(Float, nullable=True)
    booking_demand = Column(Float, nullable=True)
    search_demand = Column(Float, nullable=True)
    traffic_pressure = Column(Float, nullable=True)
    weather_pressure = Column(Float, nullable=True)
    holiday_pressure = Column(Float, nullable=True)
    event_pressure = Column(Float, nullable=True)
    current_crowd_pressure = Column(Float, nullable=True) # Computed by Crowd Engine V2

    # Calendar & Event Context
    is_weekend = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    holiday_name = Column(String(128), nullable=True)
    active_events_count = Column(Integer, default=0)

    # Signal-level provenance & quality auditing
    signal_provenance_json = Column(JSON, nullable=True) # Dict of signal_name -> {source, provider_mode, confidence, is_available}
    data_status = Column(String(32), default="PARTIAL") # COMPLETE, PARTIAL, DEGRADED, UNAVAILABLE, SYNTHETIC
    dataset_mode = Column(String(32), default="REAL", index=True) # REAL, SYNTHETIC, MIXED
    composite_confidence = Column(Float, default=0.0)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    # Relationships & Constraints
    destination = relationship("DestinationModel", back_populates="historical_observations")

    __table_args__ = (
        Index("idx_hist_dest_observed_at", "destination_id", "observed_at"),
        UniqueConstraint("destination_id", "date_bucket", "dataset_mode", name="uq_dest_date_bucket_mode"),
    )
