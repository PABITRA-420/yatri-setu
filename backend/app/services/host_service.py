import uuid
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from app.models.host import (
    Host, HostVerification, VerificationEvent, HomestayListing,
    AvailabilityRecord, HostEarningBreakdown, HostOnboardingRequest,
    VoiceDraftRequest, VoiceDraftResponse
)

# Seed sample host "Pemba Sherpa" from Kalimpong for immediate demonstration
SEED_PEMBA_HOST = Host(
    id="host-kalim-01",
    name="Pemba Sherpa",
    phone="+91 98320 87123",
    email="pemba.sherpa@yatrisetu.org",
    village="Upper Cart Road Village",
    panchayat_name="Kalimpong Block II Panchayat",
    languages=["English", "Hindi", "Nepali", "Tibetan"],
    bio="Third-generation orchid grower and certified mountain guide. Dedicated to zero-waste village hospitality.",
    avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
    experience_years=8,
    verification=HostVerification(
        status="VERIFIED",
        id_proof_type="AADHAAR_PROTOTYPE",
        id_proof_number_masked="XXXX-XXXX-4192",
        panchayat_name="Kalimpong Block II Panchayat",
        block="Kalimpong II",
        district="Kalimpong",
        submitted_at="2026-08-10 11:30:00",
        verified_at="2026-08-12 16:45:00",
        reviewed_by="Panchayat Officer Pemba Norbu",
        review_notes="Physical homestay inspection completed. Spring water filtration and fire safety verified. Certified under West Bengal Rural Tourism scheme.",
        history=[
            VerificationEvent(
                status="SUBMITTED",
                timestamp="2026-08-10 11:30:00",
                actor="Host (Pemba Sherpa)",
                notes="Initial self-registration with prototype identity and tax declaration."
            ),
            VerificationEvent(
                status="UNDER_REVIEW",
                timestamp="2026-08-11 10:15:00",
                actor="Panchayat Officer Pemba Norbu",
                notes="Assigned for Gram Panchayat physical premise inspection."
            ),
            VerificationEvent(
                status="VERIFIED",
                timestamp="2026-08-12 16:45:00",
                actor="Panchayat Officer Pemba Norbu",
                notes="Sanitation, safety norms, and community fund agreement approved."
            ),
            VerificationEvent(
                status="PUBLISHED",
                timestamp="2026-08-12 17:00:00",
                actor="System Engine",
                notes="Listing published with 'Panchayat Verified' green trust badge."
            )
        ]
    ),
    created_at="2026-08-10 11:30:00"
)

SEED_PEMBA_LISTING = HomestayListing(
    id="hs-kalim-01",
    host_id="host-kalim-01",
    destination_id="kalimpong",
    destination_name="Kalimpong",
    title="Pineview Orchid Retreat & Homestay",
    tagline="Eco-friendly heritage villa surrounded by 400+ exotic Himalayan orchids",
    address="Atisha Road, Upper Cart Road, Kalimpong - 734301",
    village="Upper Cart Road Village",
    panchayat_name="Kalimpong Block II Panchayat",
    price_per_night_inr=2100,
    room_type="Traditional Wooden Suite",
    max_guests=4,
    rooms_count=3,
    amenities=[
        "Organic Farm Dining",
        "Orchid Nursery Access",
        "Solar Water Heating",
        "High-Speed Wi-Fi",
        "Mountain View Balcony"
    ],
    sustainability_attributes=[
        "100% Single-Use Plastic Free",
        "Spring Water Filtration (Zero Bottled Water)",
        "Rainwater Harvesting System",
        "100% Composted Organic Waste"
    ],
    images=[
        "https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80"
    ],
    special_activity="Orchid cultivation workshop & Nepali organic cooking",
    rating=4.95,
    reviews_count=42,
    verification_status="VERIFIED",
    is_published=True,
    community_fund_contribution_percent=5
)

# Seed realistic earnings records for host dashboard demo
SEED_PEMBA_EARNINGS: List[HostEarningBreakdown] = [
    HostEarningBreakdown(
        booking_id="YS-BK-A4190B",
        homestay_id="hs-kalim-01",
        homestay_name="Pineview Orchid Retreat & Homestay",
        guest_name="Arjun Sengupta",
        check_in_date="2026-09-01",
        check_out_date="2026-09-04",
        nights=3,
        gross_booking_value=6300,
        platform_fee=315, # 5%
        community_fund_contribution=315, # 5%
        net_host_earning=5670, # 90%
        payout_status="DISBURSED",
        created_at="2026-09-01 14:20:00"
    ),
    HostEarningBreakdown(
        booking_id="YS-BK-B8210C",
        homestay_id="hs-kalim-01",
        homestay_name="Pineview Orchid Retreat & Homestay",
        guest_name="Sneha & Rahul Roy",
        check_in_date="2026-09-08",
        check_out_date="2026-09-10",
        nights=2,
        gross_booking_value=4200,
        platform_fee=210,
        community_fund_contribution=210,
        net_host_earning=3780,
        payout_status="IN_ESCROW_CONFIRMED",
        created_at="2026-09-04 09:12:00"
    ),
    HostEarningBreakdown(
        booking_id="YS-BK-C1902D",
        homestay_id="hs-kalim-01",
        homestay_name="Pineview Orchid Retreat & Homestay",
        guest_name="Dr. Vikram Deshmukh",
        check_in_date="2026-09-15",
        check_out_date="2026-09-19",
        nights=4,
        gross_booking_value=8400,
        platform_fee=420,
        community_fund_contribution=420,
        net_host_earning=7560,
        payout_status="IN_ESCROW_CONFIRMED",
        created_at="2026-09-06 18:30:00"
    )
]

class HostService:
    def __init__(self):
        self.hosts: Dict[str, Host] = {
            SEED_PEMBA_HOST.id: SEED_PEMBA_HOST
        }
        self.listings: Dict[str, HomestayListing] = {
            SEED_PEMBA_LISTING.id: SEED_PEMBA_LISTING
        }
        self.earnings: Dict[str, List[HostEarningBreakdown]] = {
            SEED_PEMBA_HOST.id: list(SEED_PEMBA_EARNINGS)
        }
        self.availability_store: Dict[str, Dict[str, AvailabilityRecord]] = {}
        self._init_availability(SEED_PEMBA_LISTING.id)

    def _init_availability(self, homestay_id: str):
        today = date.today()
        self.availability_store[homestay_id] = {}
        for i in range(30):
            d_str = (today + timedelta(days=i)).isoformat()
            self.availability_store[homestay_id][d_str] = AvailabilityRecord(
                homestay_id=homestay_id,
                date=d_str,
                is_available=True,
                price_override_inr=None
            )

    def get_host_by_id(self, host_id: str) -> Optional[Host]:
        return self.hosts.get(host_id)

    def get_default_host(self) -> Host:
        return self.hosts.get("host-kalim-01", SEED_PEMBA_HOST)

    def list_listings_by_host(self, host_id: str) -> List[HomestayListing]:
        return [l for l in self.listings.values() if l.host_id == host_id]

    def get_listing_by_id(self, listing_id: str) -> Optional[HomestayListing]:
        return self.listings.get(listing_id)

    def calculate_earnings(self, gross_value: int) -> Dict[str, int]:
        """
        Deterministic calculation:
        Gross = 100%
        Platform Fee = 5%
        Community Fund = 5%
        Net Host Income = 90%
        """
        platform_fee = int(round(gross_value * 0.05))
        community_fund = int(round(gross_value * 0.05))
        net_host = gross_value - platform_fee - community_fund
        return {
            "booking_value": gross_value,
            "platform_fee": platform_fee,
            "community_fund_contribution": community_fund,
            "host_earning": net_host
        }

    def get_host_earnings_summary(self, host_id: str) -> Dict[str, Any]:
        records = self.earnings.get(host_id, [])
        total_bookings = len(records)
        gross_value = sum(r.gross_booking_value for r in records)
        platform_fee = sum(r.platform_fee for r in records)
        community_contribution = sum(r.community_fund_contribution for r in records)
        net_host_income = sum(r.net_host_earning for r in records)

        return {
            "host_id": host_id,
            "total_bookings": total_bookings,
            "gross_value_inr": gross_value,
            "platform_fee_inr": platform_fee,
            "community_contribution_inr": community_contribution,
            "net_host_income_inr": net_host_income,
            "records": records
        }

    def register_host_and_listing(self, req: HostOnboardingRequest) -> Dict[str, Any]:
        """
        Full onboarding creating Host, HomestayListing, initial availability,
        and initial verification state SUBMITTED.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        host_id = f"host-{uuid.uuid4().hex[:6]}"
        listing_id = f"hs-{uuid.uuid4().hex[:6]}"

        dest_name_map = {
            "darjeeling": "Darjeeling",
            "kalimpong": "Kalimpong",
            "lava": "Lava",
            "lolegaon": "Lolegaon",
            "rishop": "Rishop",
            "mirik": "Mirik"
        }
        dest_name = dest_name_map.get(req.destination_id.lower().strip(), req.destination_id.title())

        verification = HostVerification(
            status="SUBMITTED",
            id_proof_type="AADHAAR_PROTOTYPE",
            id_proof_number_masked=f"XXXX-XXXX-{uuid.uuid4().int % 9000 + 1000}",
            panchayat_name=req.panchayat_name,
            block=f"{dest_name} Rural Block",
            district=dest_name if dest_name in ["Darjeeling", "Kalimpong"] else "Kalimpong",
            submitted_at=now_str,
            verified_at=None,
            reviewed_by=None,
            review_notes="Pending Gram Panchayat document verification & premise inspection.",
            history=[
                VerificationEvent(
                    status="SUBMITTED",
                    timestamp=now_str,
                    actor=f"Host ({req.name})",
                    notes="Self-onboarding submitted with prototype credentials."
                )
            ]
        )

        new_host = Host(
            id=host_id,
            name=req.name,
            phone=req.phone,
            email=req.email,
            village=req.village,
            panchayat_name=req.panchayat_name,
            languages=req.languages,
            bio=req.bio,
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
            experience_years=2,
            verification=verification,
            created_at=now_str
        )

        new_listing = HomestayListing(
            id=listing_id,
            host_id=host_id,
            destination_id=req.destination_id.lower().strip(),
            destination_name=dest_name,
            title=req.homestay_title,
            tagline=req.tagline,
            address=req.address,
            village=req.village,
            panchayat_name=req.panchayat_name,
            price_per_night_inr=req.price_per_night_inr,
            room_type=req.room_type,
            max_guests=req.max_guests,
            rooms_count=req.rooms_count,
            amenities=req.amenities or ["Homemade Traditional Meals", "Solar Heated Water"],
            sustainability_attributes=req.sustainability_attributes or [
                "Zero Single-Use Plastic",
                "Composted Organic Waste",
                "Direct Village Economic Retention"
            ],
            images=[
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"
            ],
            special_activity=req.special_activity or "Guided village farm walk & culinary sharing",
            rating=5.0,
            reviews_count=0,
            verification_status="SUBMITTED",
            is_published=False, # Must be verified before published to tourists
            community_fund_contribution_percent=5
        )

        self.hosts[host_id] = new_host
        self.listings[listing_id] = new_listing
        self.earnings[host_id] = []
        self._init_availability(listing_id)

        return {
            "host": new_host,
            "listing": new_listing,
            "message": "Host onboarding submitted successfully. Awaiting Gram Panchayat verification."
        }

    def get_availability(self, homestay_id: str) -> List[AvailabilityRecord]:
        if homestay_id not in self.availability_store:
            self._init_availability(homestay_id)
        records = list(self.availability_store[homestay_id].values())
        records.sort(key=lambda r: r.date)
        return records

    def toggle_availability(self, homestay_id: str, date_str: str, is_available: bool, price_override: Optional[int] = None) -> AvailabilityRecord:
        if homestay_id not in self.availability_store:
            self._init_availability(homestay_id)
        
        record = self.availability_store[homestay_id].get(date_str)
        if not record:
            record = AvailabilityRecord(
                homestay_id=homestay_id,
                date=date_str,
                is_available=is_available,
                price_override_inr=price_override
            )
        else:
            record.is_available = is_available
            if price_override is not None:
                record.price_override_inr = price_override

        self.availability_store[homestay_id][date_str] = record
        return record

    def parse_voice_listing(self, req: VoiceDraftRequest) -> VoiceDraftResponse:
        """
        AI Voice Listing Assistant:
        Takes host spoken text e.g.:
        'We have a two-room homestay near Lava. We provide homemade food and forest walks.'
        Converts it into a structured listing draft.
        
        STRICT GUARDRAILS:
        - AI must NOT invent prices
        - AI must NOT invent verification status (stays SUBMITTED)
        - AI must NOT invent identity or availability
        """
        text = req.spoken_text.lower()

        # Destination detection
        dest_map = {
            "darjeeling": ("darjeeling", "Darjeeling Village Cluster"),
            "kalimpong": ("kalimpong", "Kalimpong Ridge"),
            "lava": ("lava", "Lava Neora Foothills"),
            "lolegaon": ("lolegaon", "Lolegaon Canopy Valley"),
            "rishop": ("rishop", "Rishop Ridge"),
            "mirik": ("mirik", "Mirik Valley & Lake")
        }
        detected_dest_id = "lava"
        detected_village = "Lava Neora Foothills"
        for d_key, (d_id, v_name) in dest_map.items():
            if d_key in text:
                detected_dest_id = d_id
                detected_village = v_name
                break

        # Room count extraction
        room_count = 2
        numbers_word_map = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "single": 1, "double": 2, "triple": 3
        }
        for word, val in numbers_word_map.items():
            if f"{word}-room" in text or f"{word} room" in text or f"{word} rooms" in text:
                room_count = val
                break
        
        # Room type
        room_type = "Traditional Wooden Cottage"
        if "attic" in text:
            room_type = "Pine Wood Attic Room"
        elif "suite" in text:
            room_type = "Himalayan View Suite"
        elif "cottage" in text:
            room_type = "Mountain Log Cabin"

        # Amenities detection
        amenities = []
        if "homemade" in text or "food" in text or "meals" in text or "kitchen" in text:
            amenities.append("Authentic Homemade Village Meals")
        if "forest" in text or "walk" in text or "trail" in text:
            amenities.append("Guided Forest & Nature Trail Walks")
        if "wifi" in text or "internet" in text:
            amenities.append("High-Speed Wi-Fi")
        if "water" in text or "spring" in text:
            amenities.append("Pure Mountain Spring Water")
        if "balcony" in text or "view" in text:
            amenities.append("Panoramic Mountain View Balcony")
        if not amenities:
            amenities = ["Homemade Traditional Meals", "Forest Walking Trail Access", "Solar Hot Water"]

        # Sustainability attributes
        sustainability = [
            "100% Single-Use Plastic Free",
            "Direct Village Family Economy Support"
        ]
        if "organic" in text or "farm" in text:
            sustainability.append("Organic Kitchen Garden Dining")
        if "solar" in text:
            sustainability.append("Solar Powered Hot Water")

        # Experiences
        experiences = []
        if "forest" in text or "walk" in text:
            experiences.append("Neora Valley Pine Canopy Nature Walk")
        if "food" in text or "cooking" in text:
            experiences.append("Himalayan Organic Hearthside Cooking Class")
        if not experiences:
            experiences.append(f"{detected_village} Heritage & Agriculture Walk")

        capitalized_dest = detected_dest_id.title()
        suggested_title = f"{capitalized_dest} Pine & Valley Rural Homestay"
        suggested_tagline = f"Peaceful {room_count}-room village retreat offering home-cooked mountain hospitality"

        return VoiceDraftResponse(
            original_transcript=req.spoken_text,
            suggested_title=suggested_title,
            suggested_tagline=suggested_tagline,
            detected_destination_id=detected_dest_id,
            detected_village=detected_village,
            detected_room_type=room_type,
            suggested_rooms_count=room_count,
            detected_amenities=amenities,
            detected_sustainability_attributes=sustainability,
            suggested_experiences=experiences,
            price_requires_host_input=True,
            verification_status="SUBMITTED",
            warning_guardrail="AI has strictly NOT set pricing, identity, or verification. The host must inspect and approve all fields before submission."
        )

# Global singleton
host_service = HostService()
