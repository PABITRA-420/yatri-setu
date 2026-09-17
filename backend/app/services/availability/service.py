"""
Availability Service for Yatri Setu (Milestone 7E).
Maintains date-aware accommodation inventory snapshots and atomic room reservation ledger.
"""

from datetime import datetime, date
import threading
from typing import Dict, Optional, Tuple

from app.data.seed_data import DESTINATIONS_DATA
from app.services.homestay_repository import homestay_repository, HomestayRepository
from app.services.capacity.service import capacity_service
from app.services.availability.schemas import (
    AvailabilityStatus,
    HomestayAvailabilitySnapshot,
    DestinationAvailabilitySnapshot,
)


def classify_availability_status(available_units: int, total_units: int) -> AvailabilityStatus:
    if total_units <= 0:
        return AvailabilityStatus.UNKNOWN
    if available_units <= 0:
        return AvailabilityStatus.FULL
    ratio = available_units / total_units
    if ratio <= 0.25:
        return AvailabilityStatus.LIMITED
    return AvailabilityStatus.AVAILABLE


class AvailabilityService:
    def __init__(self, hs_repo: Optional[HomestayRepository] = None):
        self._hs_repo = hs_repo or homestay_repository
        self._lock = threading.Lock()
        # Key: (homestay_id, date_str) -> booked_units: int
        self._ledger: Dict[Tuple[str, str], int] = {}
        # Homestay default rooms configuration (2-4 rooms per authentic mountain property)
        self._default_property_rooms = 3

    def _get_homestay_total_rooms(self, homestay_id: str) -> int:
        """Determines authoritative total rooms for a homestay."""
        rec = self._hs_repo.get_raw_record(homestay_id)
        if not rec:
            return 2
        # If record has room count or max guests
        if hasattr(rec, "rooms_count") and rec.rooms_count:
            return rec.rooms_count
        if hasattr(rec, "max_guests") and rec.max_guests:
            return max(1, (rec.max_guests + 1) // 2)
        return self._default_property_rooms

    def get_homestay_availability(
        self,
        homestay_id: str,
        target_date: Optional[str] = None
    ) -> HomestayAvailabilitySnapshot:
        """Retrieves date-aware availability snapshot for a specific homestay."""
        clean_hs_id = self._hs_repo._resolve_id(homestay_id)
        rec = self._hs_repo.get_raw_record(clean_hs_id)
        if not rec:
            now_iso = datetime.utcnow().isoformat()
            d_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")
            return HomestayAvailabilitySnapshot(
                homestay_id=clean_hs_id,
                destination_id="unknown",
                date=d_str,
                total_units=0,
                available_units=0,
                occupied_units=0,
                reserved_units=0,
                availability_status=AvailabilityStatus.UNKNOWN,
                source="AUTHORITATIVE_HOMESTAY_LEDGER",
                provider_mode="REAL",
                data_quality="DEGRADED",
                updated_at=now_iso
            )

        d_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")
        total_units = self._get_homestay_total_rooms(clean_hs_id)

        with self._lock:
            booked = self._ledger.get((clean_hs_id, d_str), 0)

        reserved_units = 0
        occupied = min(total_units, booked)
        avail = max(0, total_units - occupied - reserved_units)
        status = classify_availability_status(avail, total_units)

        return HomestayAvailabilitySnapshot(
            homestay_id=rec.id,
            destination_id=rec.destination_id,
            date=d_str,
            total_units=total_units,
            available_units=avail,
            occupied_units=occupied,
            reserved_units=reserved_units,
            availability_status=status,
            source="AUTHORITATIVE_HOMESTAY_LEDGER",
            provider_mode="REAL",
            data_quality="HIGH",
            updated_at=datetime.utcnow().isoformat()
        )

    def get_destination_availability(
        self,
        destination_id: str,
        target_date: Optional[str] = None
    ) -> DestinationAvailabilitySnapshot:
        """Retrieves aggregated date-specific availability across destination accommodations."""
        clean_dest_id = destination_id.lower().strip()
        dest_dict = next((d for d in DESTINATIONS_DATA if d["id"] == clean_dest_id), None)
        dest_name = dest_dict["name"] if dest_dict else clean_dest_id.capitalize()

        d_str = target_date or datetime.utcnow().strftime("%Y-%m-%d")

        # Baseline capacity from M7D
        cap = capacity_service.get_destination_capacity(clean_dest_id)
        total_regional_units = cap.total_units
        baseline_occupied = cap.occupied_units

        # Aggregate any dynamic ledger bookings for this date
        with self._lock:
            active_homestays = [
                r.id for r in self._hs_repo._records.values()
                if r.destination_id == clean_dest_id and r.is_published
            ]
            dynamic_booked = sum(self._ledger.get((hs_id, d_str), 0) for hs_id in active_homestays)

        occupied_total = min(total_regional_units, baseline_occupied + dynamic_booked)
        avail_total = max(0, total_regional_units - occupied_total)
        occ_rate = occupied_total / max(1, total_regional_units)
        status = classify_availability_status(avail_total, total_regional_units)

        return DestinationAvailabilitySnapshot(
            destination_id=clean_dest_id,
            destination_name=dest_name,
            date=d_str,
            total_units=total_regional_units,
            available_units=avail_total,
            occupied_units=occupied_total,
            occupancy_rate=round(occ_rate, 3),
            availability_status=status,
            data_quality="HIGH",
            source="YATRI_SETU_AVAILABILITY_LEDGER",
            provider_mode="REAL",
            updated_at=datetime.utcnow().isoformat()
        )

    def _persist_availability(self, homestay_id: str, target_date: str, total_units: int, booked_units: int) -> None:
        """Helper to synchronize availability ledger row with SQLAlchemy model."""
        try:
            from app.core.database import SessionLocal
            from app.models.entities import AvailabilityModel
            t_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            db = SessionLocal()
            try:
                avail_rec = db.query(AvailabilityModel).filter(
                    AvailabilityModel.homestay_id == homestay_id,
                    AvailabilityModel.date == t_date
                ).first()
                avail_rooms = max(0, total_units - booked_units)
                is_avail = (avail_rooms > 0)
                if not avail_rec:
                    db.add(AvailabilityModel(
                        id=f"av-{homestay_id}-{target_date}",
                        homestay_id=homestay_id,
                        date=t_date,
                        total_units=total_units,
                        booked_units=booked_units,
                        is_available=is_avail,
                        rooms_available=avail_rooms
                    ))
                else:
                    avail_rec.total_units = total_units
                    avail_rec.booked_units = booked_units
                    avail_rec.rooms_available = avail_rooms
                    avail_rec.is_available = is_avail
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass

    def reserve_units(self, homestay_id: str, target_date: str, units: int = 1) -> bool:
        """
        Atomically decrements available units for homestay on target date.
        Returns True if reservation succeeded, False if insufficient units.
        """
        clean_hs_id = self._hs_repo._resolve_id(homestay_id)
        total_rooms = self._get_homestay_total_rooms(clean_hs_id)

        with self._lock:
            current_booked = self._ledger.get((clean_hs_id, target_date), 0)
            if current_booked + units > total_rooms:
                return False  # Overbooking prevented
            new_booked = current_booked + units
            self._ledger[(clean_hs_id, target_date)] = new_booked
            self._persist_availability(clean_hs_id, target_date, total_rooms, new_booked)
            return True

    def release_units(self, homestay_id: str, target_date: str, units: int = 1) -> None:
        """Atomically restores available units when booking is cancelled."""
        clean_hs_id = self._hs_repo._resolve_id(homestay_id)
        with self._lock:
            current_booked = self._ledger.get((clean_hs_id, target_date), 0)
            new_booked = max(0, current_booked - units)
            self._ledger[(clean_hs_id, target_date)] = new_booked
            total_rooms = self._get_homestay_total_rooms(clean_hs_id)
            self._persist_availability(clean_hs_id, target_date, total_rooms, new_booked)


availability_service = AvailabilityService()
