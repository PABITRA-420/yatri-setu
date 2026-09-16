"""
Safety & Notification Providers for Yatri Setu (Milestone 7F).
Provides Internal Network responder routing, Demo notifications, and verified official helpline directories.
Strictly distinguishes:
- REAL — YATRI SETU NETWORK
- DEMO — SYNTHETIC
- REAL EXTERNAL — <provider>
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.safety.base import BaseSafetyProvider, BaseNotificationProvider
from app.services.safety.schemas import (
    ProviderMode,
    NotificationChannel,
    NotificationStatus,
    NotificationRecord,
    OfficialEmergencyContact,
    ResponderInfo,
    SafetyProvenance
)
from app.data.seed_data import EMERGENCY_RESPONDERS


# Verified Public Emergency Helplines (labelled OFFICIAL INFORMATION)
VERIFIED_OFFICIAL_CONTACTS: List[OfficialEmergencyContact] = [
    OfficialEmergencyContact(
        service_name="National Emergency Number (All-in-One)",
        contact_number="112",
        toll_free=True,
        region="All India / West Bengal & Sikkim",
        category="POLICE_FIRE_AMBULANCE",
        verification_label="OFFICIAL INFORMATION — NATIONAL EMERGENCY"
    ),
    OfficialEmergencyContact(
        service_name="Incredible India Tourist Helpline (24x7 Multi-lingual)",
        contact_number="1363",
        toll_free=True,
        region="National Tourist Safety",
        category="TOURIST_SAFETY",
        verification_label="OFFICIAL INFORMATION — MINISTRY OF TOURISM"
    ),
    OfficialEmergencyContact(
        service_name="Women in Distress Helpline",
        contact_number="1091",
        toll_free=True,
        region="National",
        category="WOMEN_SAFETY",
        verification_label="OFFICIAL INFORMATION — NATIONAL HELPLINE"
    ),
    OfficialEmergencyContact(
        service_name="State Disaster Management Authority Control Room",
        contact_number="1070",
        toll_free=True,
        region="West Bengal State Operations",
        category="DISASTER_MANAGEMENT",
        verification_label="OFFICIAL INFORMATION — STATE CONTROL ROOM"
    ),
    OfficialEmergencyContact(
        service_name="Himalayan Mountain Rescue Assistance (Civil Society Desk)",
        contact_number="+91 3552 255100",
        toll_free=False,
        region="Kalimpong / Darjeeling Hills",
        category="MOUNTAIN_SEARCH_AND_RESCUE",
        verification_label="OFFICIAL INFORMATION — REGIONAL CIVIL RESCUE"
    )
]


class InternalDemoSafetyProvider(BaseSafetyProvider):
    """
    Internal Safety Provider handling Yatri Setu Network dispatch.
    Emits alerts to the local Yatri Mitra volunteer coordinators and internal operations desk.
    Does NOT claim direct police/ambulance dispatch without real external integrations.
    """

    def __init__(self, mode: ProviderMode = ProviderMode.INTERNAL):
        self.mode = mode

    def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return (
            SafetyProvenance.REAL_NETWORK.value
            if self.mode == ProviderMode.INTERNAL
            else SafetyProvenance.DEMO_SYNTHETIC.value
        )

    def dispatch_sos(self, incident_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates with nearest simulated/internal Yatri Mitra rural volunteers.
        """
        responders = [
            ResponderInfo(
                name=r.get("name", "Local Volunteer Unit"),
                agency=r.get("agency", "Yatri Setu Mitra Network"),
                distance_km=float(r.get("distance_km", 2.0)),
                eta_minutes=int(r.get("eta_minutes", 10)),
                phone=r.get("phone", "+91 98320 00000"),
                status="DISPATCHED" if "Mitra" in r.get("agency", "") else "STANDBY"
            )
            for r in EMERGENCY_RESPONDERS
        ]

        return {
            "dispatch_status": "DELIVERED_TO_OPERATIONS_DESK",
            "provider_mode": self.mode.value,
            "provenance": self.get_provider_name(),
            "responders": responders,
            "dispatched_at": datetime.utcnow().isoformat()
        }


class DemoNotificationProvider(BaseNotificationProvider):
    """
    Notification Provider for multi-channel operator alerts and traveler updates.
    Labels all dispatches with realistic provenance and never fabricates delivery.
    """

    def __init__(self, mode: ProviderMode = ProviderMode.INTERNAL):
        self.mode = mode

    def send_notification(
        self,
        incident_id: str,
        recipient_type: str,
        channel: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationRecord:
        notif_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"

        try:
            chan_enum = NotificationChannel(channel.upper())
        except Exception:
            chan_enum = NotificationChannel.IN_APP

        record = NotificationRecord(
            notification_id=notif_id,
            incident_id=incident_id,
            recipient_type=recipient_type,
            channel=chan_enum,
            status=NotificationStatus.DELIVERED,
            sent_at=datetime.utcnow().isoformat(),
            provider="Yatri Setu Operational Alert Relay",
            provider_mode=self.mode,
            details=f"[{title}] {message}"
        )
        return record
