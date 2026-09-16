import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from app.models.host import VerificationEvent
from app.models.panchayat import (
    PanchayatDashboard, PanchayatVerificationItem, PanchayatDecisionRequest,
    PanchayatDecisionResponse, CommunityFundProject
)
from app.services.host_service import host_service
from app.services.homestay_repository import homestay_repository

SEED_COMMUNITY_PROJECTS: List[CommunityFundProject] = [
    CommunityFundProject(
        id="proj-cf-01",
        title="Teesta Valley Ridge Trail Restoration & Stone Paving",
        category="Trail Restoration",
        budget_inr=185000,
        status="COMPLETED",
        completion_date="2026-07-15",
        impact_description="Restored 4.2 km traditional footpath connecting Upper Cart Road to orchid nurseries, eliminating mud hazards during monsoons."
    ),
    CommunityFundProject(
        id="proj-cf-02",
        title="Village Solar Street Lighting & Micro-Grid for Forest Paths",
        category="Solar Lighting",
        budget_inr=240000,
        status="COMPLETED",
        completion_date="2026-08-01",
        impact_description="Installed 28 standalone dusk-to-dawn solar LED streetlamps along village homestay paths, enhancing tourist safety at night."
    ),
    CommunityFundProject(
        id="proj-cf-03",
        title="Zero-Plastic Himalayan Water Refill Kiosks (4 Locations)",
        category="Spring Water Rejuvenation",
        budget_inr=120000,
        status="IN_PROGRESS",
        completion_date="2026-10-10",
        impact_description="UV-filtered natural spring kiosks preventing an estimated 14,000 single-use plastic bottles annually."
    ),
    CommunityFundProject(
        id="proj-cf-04",
        title="Community Composting & Organic Solid Waste Digester",
        category="Plastic Waste Management",
        budget_inr=95000,
        status="PROPOSED",
        completion_date="2026-11-30",
        impact_description="Decentralized organic waste digester serving 18 village homestays and producing bio-fertilizer for local terraced orchards."
    )
]

SEED_VERIFICATION_QUEUE: List[PanchayatVerificationItem] = [
    PanchayatVerificationItem(
        listing_id="hs-kalim-01",
        host_id="host-kalim-01",
        host_name="Pemba Sherpa",
        host_phone="+91 98320 87123",
        homestay_title="Pineview Orchid Retreat & Homestay",
        destination_id="kalimpong",
        destination_name="Kalimpong",
        village="Upper Cart Road Village",
        panchayat_name="Kalimpong Block II Panchayat",
        submitted_at="2026-08-10 11:30:00",
        verification_status="VERIFIED",
        id_proof_type="AADHAAR_PROTOTYPE",
        id_proof_masked="XXXX-XXXX-4192",
        rooms_count=3,
        price_per_night_inr=2100,
        amenities=["Organic Farm Dining", "Orchid Nursery Access", "Solar Water Heating", "High-Speed Wi-Fi"],
        sustainability_attributes=["100% Single-Use Plastic Free", "Spring Water Filtration", "Rainwater Harvesting"],
        history=[
            VerificationEvent(
                status="SUBMITTED",
                timestamp="2026-08-10 11:30:00",
                actor="Host (Pemba Sherpa)",
                notes="Initial self-registration submitted."
            ),
            VerificationEvent(
                status="VERIFIED",
                timestamp="2026-08-12 16:45:00",
                actor="Panchayat Officer Pemba Norbu",
                notes="Site visited. Fire safety equipment and sanitation inspected."
            )
        ]
    ),
    PanchayatVerificationItem(
        listing_id="hs-lava-02",
        host_id="host-lava-02",
        host_name="Tenzin Bhutia",
        host_phone="+91 94340 55102",
        homestay_title="Neora Valley Cloud Mist Lodge",
        destination_id="lava",
        destination_name="Lava",
        village="Algarah-Lava Forest Fringe",
        panchayat_name="Lava Forest Range Panchayat",
        submitted_at="2026-09-04 15:10:00",
        verification_status="UNDER_REVIEW",
        id_proof_type="AADHAAR_PROTOTYPE",
        id_proof_masked="XXXX-XXXX-7721",
        rooms_count=2,
        price_per_night_inr=1750,
        amenities=["Wood Fireplace", "Homecooked Lepcha Meals", "Birding Balcony"],
        sustainability_attributes=["Zero Single-Use Plastic", "Locally Sourced Organic Produce"],
        history=[
            VerificationEvent(
                status="SUBMITTED",
                timestamp="2026-09-04 15:10:00",
                actor="Host (Tenzin Bhutia)",
                notes="Submitted for village panchayat review."
            ),
            VerificationEvent(
                status="UNDER_REVIEW",
                timestamp="2026-09-05 10:00:00",
                actor="Panchayat Officer Pemba Norbu",
                notes="Scheduled for field inspection and waste management audit."
            )
        ]
    ),
    PanchayatVerificationItem(
        listing_id="hs-lole-03",
        host_id="host-lole-03",
        host_name="Nima Rai",
        host_phone="+91 97330 91823",
        homestay_title="Canopy View Heritage Homestay",
        destination_id="lolegaon",
        destination_name="Lolegaon",
        village="Kaffer Forest Hamlet",
        panchayat_name="Lolegaon Heritage Panchayat",
        submitted_at="2026-09-05 09:30:00",
        verification_status="SUBMITTED",
        id_proof_type="AADHAAR_PROTOTYPE",
        id_proof_masked="XXXX-XXXX-3349",
        rooms_count=3,
        price_per_night_inr=1900,
        amenities=["Pine Deck", "Traditional Hearth", "Cardamom Garden Tours"],
        sustainability_attributes=["Gravity Spring Water", "Zero Single-Use Plastic"],
        history=[
            VerificationEvent(
                status="SUBMITTED",
                timestamp="2026-09-05 09:30:00",
                actor="Host (Nima Rai)",
                notes="Registration submitted with Gram Panchayat endorsement form."
            )
        ]
    )
]

class PanchayatService:
    def __init__(self):
        self.verifications: Dict[str, PanchayatVerificationItem] = {
            v.listing_id: v for v in SEED_VERIFICATION_QUEUE
        }
        self.projects: List[CommunityFundProject] = list(SEED_COMMUNITY_PROJECTS)
        self.community_fund_balance_inr = 385000

    def get_dashboard(self) -> PanchayatDashboard:
        # Sync with host_service listings if new ones were onboarded
        for listing in host_service.listings.values():
            if listing.id not in self.verifications:
                host = host_service.get_host_by_id(listing.host_id)
                self.verifications[listing.id] = PanchayatVerificationItem(
                    listing_id=listing.id,
                    host_id=listing.host_id,
                    host_name=host.name if host else "Host",
                    host_phone=host.phone if host else "+91 98000 00000",
                    homestay_title=listing.title,
                    destination_id=listing.destination_id,
                    destination_name=listing.destination_name,
                    village=listing.village,
                    panchayat_name=listing.panchayat_name,
                    submitted_at=listing.verification_status,
                    verification_status=listing.verification_status,
                    id_proof_type="AADHAAR_PROTOTYPE",
                    id_proof_masked="XXXX-XXXX-8812",
                    rooms_count=listing.rooms_count,
                    price_per_night_inr=listing.price_per_night_inr,
                    amenities=listing.amenities,
                    sustainability_attributes=listing.sustainability_attributes,
                    history=[
                        VerificationEvent(
                            status="SUBMITTED",
                            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            actor="Host Participant",
                            notes="Onboarded via Yatri Setu portal."
                        )
                    ]
                )

        items = list(self.verifications.values())
        verified_count = sum(1 for v in items if v.verification_status in ["VERIFIED", "PUBLISHED"])
        pending_count = sum(1 for v in items if v.verification_status in ["SUBMITTED", "UNDER_REVIEW"])
        
        return PanchayatDashboard(
            panchayat_name="Kalimpong District Gram Panchayat Apex Nodal",
            block="Kalimpong II & Neora Valley Circles",
            district="Kalimpong",
            state="West Bengal",
            verified_homestays_count=verified_count + 14, # seeded across villages
            pending_verifications_count=pending_count,
            local_guides_count=26,
            total_experiences_count=18,
            tourist_arrivals_this_month=642,
            local_booking_revenue_inr=1845000,
            community_fund_balance_inr=self.community_fund_balance_inr,
            tourism_pressure_relief_index=0.34, # 34% crowd relief diverted from Darjeeling
            community_projects=self.projects,
            recent_verifications=items
        )

    def list_verifications(self, status: Optional[str] = None) -> List[PanchayatVerificationItem]:
        # Sync listings
        for listing in host_service.listings.values():
            if listing.id not in self.verifications:
                host = host_service.get_host_by_id(listing.host_id)
                self.verifications[listing.id] = PanchayatVerificationItem(
                    listing_id=listing.id,
                    host_id=listing.host_id,
                    host_name=host.name if host else "Host",
                    host_phone=host.phone if host else "+91 98000 00000",
                    homestay_title=listing.title,
                    destination_id=listing.destination_id,
                    destination_name=listing.destination_name,
                    village=listing.village,
                    panchayat_name=listing.panchayat_name,
                    submitted_at="2026-09-06",
                    verification_status=listing.verification_status,
                    id_proof_type="AADHAAR_PROTOTYPE",
                    id_proof_masked="XXXX-XXXX-9901",
                    rooms_count=listing.rooms_count,
                    price_per_night_inr=listing.price_per_night_inr,
                    amenities=listing.amenities,
                    sustainability_attributes=listing.sustainability_attributes,
                    history=[]
                )

        items = list(self.verifications.values())
        if status:
            return [v for v in items if v.verification_status.upper() == status.upper()]
        return items

    def process_decision(
        self,
        listing_id: str,
        req: PanchayatDecisionRequest
    ) -> PanchayatDecisionResponse:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        v_item = self.verifications.get(listing_id)
        if not v_item:
            # Check host_service listings
            listing = host_service.get_listing_by_id(listing_id)
            if not listing:
                raise ValueError(f"Listing ID {listing_id} not found in verification queue.")
            host = host_service.get_host_by_id(listing.host_id)
            v_item = PanchayatVerificationItem(
                listing_id=listing.id,
                host_id=listing.host_id,
                host_name=host.name if host else "Host",
                host_phone=host.phone if host else "+91 98000 00000",
                homestay_title=listing.title,
                destination_id=listing.destination_id,
                destination_name=listing.destination_name,
                village=listing.village,
                panchayat_name=listing.panchayat_name,
                submitted_at=now_str,
                verification_status=listing.verification_status,
                id_proof_type="AADHAAR_PROTOTYPE",
                id_proof_masked="XXXX-XXXX-9901",
                rooms_count=listing.rooms_count,
                price_per_night_inr=listing.price_per_night_inr,
                amenities=listing.amenities,
                sustainability_attributes=listing.sustainability_attributes,
                history=[]
            )
            self.verifications[listing_id] = v_item

        previous_status = v_item.verification_status
        new_status = "VERIFIED" if req.action.upper() == "APPROVE" else "REJECTED"

        event = VerificationEvent(
            status=new_status,
            timestamp=now_str,
            actor=req.reviewer_name,
            notes=req.reason
        )
        v_item.verification_status = new_status
        v_item.history.append(event)

        # Update underlying host and listing if present
        listing = host_service.get_listing_by_id(listing_id)
        if listing:
            listing.verification_status = new_status
            listing.is_published = (new_status == "VERIFIED")
            host = host_service.get_host_by_id(listing.host_id)
            if host:
                host.verification.status = new_status
                if new_status == "VERIFIED":
                    host.verification.verified_at = now_str
                host.verification.reviewed_by = req.reviewer_name
                host.verification.review_notes = req.reason
                host.verification.history.append(event)

        # Update authoritative homestay repository record
        updated = homestay_repository.update_verification_status(listing_id, new_status)
        if not updated and listing:
            # Register newly onboarded listing into repository if not already seeded
            host_obj = host_service.get_host_by_id(listing.host_id)
            rec = homestay_repository.register_onboarding(
                listing_id=listing.id,
                host_id=listing.host_id,
                host_name=host_obj.name if host_obj else "Host",
                destination_id=listing.destination_id,
                destination_name=listing.destination_name,
                title=listing.title,
                tagline=listing.tagline,
                address=listing.address,
                village=listing.village,
                panchayat_name=listing.panchayat_name,
                price_per_night_inr=listing.price_per_night_inr,
                room_type=listing.room_type,
                max_guests=listing.max_guests,
                rooms_count=listing.rooms_count,
                amenities=listing.amenities,
                special_activity=listing.special_activity,
                images=listing.images
            )
            rec.verification_status = new_status
            rec.is_published = (new_status in ("VERIFIED", "PUBLISHED"))

        return PanchayatDecisionResponse(
            listing_id=listing_id,
            previous_status=previous_status,
            new_status=new_status,
            updated_at=now_str,
            reviewer_name=req.reviewer_name,
            decision_notes=req.reason
        )

    def get_analytics(self) -> Dict[str, Any]:
        """
        Panchayat Rural Tourism & Economic Flow Analytics:
        Provides breakdown of tourist redirection from crowded Darjeeling
        into village homestay clusters and community fund allocations.
        """
        return {
            "summary": {
                "total_redirected_tourists": 438,
                "total_village_homestay_bookings": 182,
                "local_revenue_generated_inr": 1845000,
                "community_fund_accrued_inr": 92250, # 5% of gross
                "crowd_pressure_reduction_darjeeling_percent": 34.2
            },
            "village_distribution": [
                {
                    "village": "Upper Cart Road & Deolo (Kalimpong)",
                    "verified_homestays": 6,
                    "tourist_arrivals": 184,
                    "local_spend_inr": 720000,
                    "fund_contribution_inr": 36000
                },
                {
                    "village": "Lava Neora Foothills",
                    "verified_homestays": 4,
                    "tourist_arrivals": 128,
                    "local_spend_inr": 510000,
                    "fund_contribution_inr": 25500
                },
                {
                    "village": "Rishop Ridge & Tiffin Dara",
                    "verified_homestays": 3,
                    "tourist_arrivals": 96,
                    "local_spend_inr": 395000,
                    "fund_contribution_inr": 19750
                },
                {
                    "village": "Lolegaon Canopy Valley",
                    "verified_homestays": 2,
                    "tourist_arrivals": 30,
                    "local_spend_inr": 220000,
                    "fund_contribution_inr": 11000
                }
            ],
            "community_fund_expenditure": {
                "total_collected_inr": 520000,
                "total_spent_on_projects_inr": 425000,
                "reserve_balance_inr": self.community_fund_balance_inr,
                "active_projects_count": len(self.projects)
            }
        }

# Global singleton
panchayat_service = PanchayatService()
