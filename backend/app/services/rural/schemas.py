"""
Milestone 7G: Panchayat + Host + Local Economy Intelligence Schemas.
Normalized models for hosts, Panchayats/local operators, local economy impact,
capacity advisories, and host/Panchayat notifications.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class HostVerificationStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"


class HostActiveStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AuthorityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CONFIGURED = "CONFIGURED"
    DEMO = "DEMO"


class PanchayatNotificationSeverity(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class PanchayatNotificationStatus(str, Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class PaymentProviderMode(str, Enum):
    DEMO = "DEMO"
    UNAVAILABLE = "UNAVAILABLE"
    REAL = "REAL"


class EconomicProvenance(str, Enum):
    REAL = "REAL — YATRI SETU NETWORK"
    DEMO = "DEMO — SYNTHETIC"
    ESTIMATED = "ESTIMATED — MODELLED"
    SIMULATED = "SIMULATED — PLANNING SCENARIO"
    MIXED = "MIXED"


class HostProfile(BaseModel):
    host_id: str
    homestay_ids: List[str] = Field(default_factory=list)
    destination_id: str
    display_name: str
    phone_masked: str = "XXXX-XXXX"
    email_masked: str = "host@yatrisetu.org"
    village: str
    panchayat_name: str
    verification_status: HostVerificationStatus = HostVerificationStatus.VERIFIED
    verification_method: str = "PANCHAYAT_PHYSICAL_INSPECTION"
    active_status: HostActiveStatus = HostActiveStatus.ACTIVE
    joined_at: str
    last_updated: str
    contact_visibility: str = "VERIFIED_GUESTS_ONLY"
    language_support: List[str] = Field(default_factory=list)
    experience_categories: List[str] = Field(default_factory=list)
    source: str = "REAL HOST REGISTRATION"
    provider_mode: str = "DEMO"
    data_quality: str = "VALIDATED"


class LocalAuthorityProfile(BaseModel):
    authority_id: str
    destination_id: str
    destination_name: str
    name: str
    jurisdiction: str
    status: AuthorityStatus = AuthorityStatus.ACTIVE
    notification_channels: List[str] = Field(default_factory=lambda: ["DASHBOARD", "CIVIC_ADVISORY"])
    contact_information: Dict[str, str] = Field(default_factory=dict)
    source: str = "OFFICIAL INFORMATION"
    provider_mode: str = "CONFIGURED"
    data_quality: str = "ADMIN_VERIFIED"


class PanchayatNotification(BaseModel):
    notification_id: str
    authority_id: str
    destination_id: str
    severity: PanchayatNotificationSeverity
    title: str
    message: str
    trigger_type: str = "CAPACITY_WARNING"  # CAPACITY_WARNING, FLOW_ADVISORY, SAFETY_ESCALATION, WEATHER_ALERT
    source: str = "DEMO — PANCHAYAT NOTIFICATION"
    status: PanchayatNotificationStatus = PanchayatNotificationStatus.NEW
    created_at: str
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None


class HostNotification(BaseModel):
    notification_id: str
    host_id: str
    homestay_id: Optional[str] = None
    type: str  # BOOKING_CONFIRMED, BOOKING_CANCELLED, CAPACITY_SIGNAL, PAYOUT_UPDATE, VERIFICATION_STATUS
    title: str
    message: str
    created_at: str
    is_read: bool = False


class HostBookingSnapshot(BaseModel):
    total_reservations: int = 0
    confirmed_stays: int = 0
    cancellations: int = 0
    cancellation_rate_percent: float = 0.0
    occupied_room_nights: int = 0
    available_inventory_units: int = 0
    occupancy_rate_percent: float = 0.0


class HostDemandSnapshot(BaseModel):
    availability_checks: int = 0
    booking_initiations: int = 0
    confirmed_bookings: int = 0
    booking_conversion_rate: float = 0.0
    interest_trend: str = "STEADY"


class HostEconomicSummary(BaseModel):
    gross_booking_value: int = 0
    cancelled_value: int = 0
    confirmed_value: int = 0
    platform_commission: int = 0
    platform_commission_label: str = "CONFIGURED ASSUMPTION (5%)"
    community_fund_contribution: int = 0
    community_fund_label: str = "COMMUNITY FUND (5%)"
    taxes_or_fees: str = "NOT MODELED"
    estimated_host_payout: int = 0
    payout_notice: str = "Estimated from confirmed booking value; payment settlement is not connected."
    provenance: str = "REAL BOOKING DATA + CONFIGURED COMMISSION"


class HostDashboardData(BaseModel):
    profile: HostProfile
    active_homestays: List[Dict[str, Any]] = Field(default_factory=list)
    booking_snapshot: HostBookingSnapshot
    demand_snapshot: HostDemandSnapshot
    economic_summary: HostEconomicSummary
    recent_notifications: List[HostNotification] = Field(default_factory=list)
    provenance: str = "MIXED (REAL TELEMETRY + DEMO SEED)"


class DestinationLocalEconomy(BaseModel):
    destination_id: str
    destination_name: str
    active_hosts_count: int = 0
    verified_hosts_count: int = 0
    participating_homestays_count: int = 0
    host_participation_rate: float = 1.0  # active / eligible
    confirmed_bookings: int = 0
    occupied_room_nights: int = 0
    gross_booking_value_inr: int = 0
    estimated_local_payout_inr: int = 0
    community_fund_accrued_inr: int = 0
    cancellations_count: int = 0
    outbound_referrals_count: int = 0
    provenance: str = "REAL — YATRI SETU NETWORK"


class PanchayatDashboardData(BaseModel):
    authority: LocalAuthorityProfile
    tourism_flow: Dict[str, Any]
    rural_ecosystem: Dict[str, Any]
    local_economy: DestinationLocalEconomy
    safety_summary: Dict[str, Any]
    notifications: List[PanchayatNotification] = Field(default_factory=list)
    capacity_warning: Optional[Dict[str, Any]] = None
    provenance: str = "AGGREGATE FIRST-PARTY + MODELLED"


class RuralAdminSummary(BaseModel):
    total_active_hosts: int = 0
    total_verified_hosts: int = 0
    total_active_homestays: int = 0
    total_confirmed_bookings: int = 0
    total_room_nights: int = 0
    total_gross_booking_value_inr: int = 0
    total_estimated_host_payout_inr: int = 0
    total_cancellations: int = 0
    destinations: List[DestinationLocalEconomy] = Field(default_factory=list)
    provenance: str = "REAL — YATRI SETU NETWORK"


class AuditLogRecord(BaseModel):
    log_id: str
    actor: str
    action: str
    timestamp: str
    entity_type: str
    entity_id: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    details: Optional[str] = None
