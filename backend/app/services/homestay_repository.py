"""
Authoritative Homestay Repository (Milestone 7A Hardening).
Provides a single source of truth for homestay entities across:
- Tourist listings & detail views
- Host listings & onboarding
- Panchayat verification workflows
- Tourist booking flow

Ensures consistent homestay_id, destination_id, host_id, and verification_status.
Only VERIFIED and PUBLISHED homestays are visible to tourist endpoints.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from app.models.homestay import Homestay, HostInfo

logger = logging.getLogger(__name__)


class AuthoritativeHomestayRecord:
    def __init__(
        self,
        id: str,
        destination_id: str,
        destination_name: str,
        title: str,
        tagline: str,
        address: str,
        price_per_night_inr: int,
        rating: float,
        reviews_count: int,
        room_type: str,
        max_guests: int,
        amenities: List[str],
        images: List[str],
        host_id: str,
        host_name: str,
        host_avatar: str,
        host_experience_years: int,
        host_languages: List[str],
        host_about: str,
        host_response_rate: str,
        community_fund_contribution_percent: int,
        special_activity: str,
        verification_status: str = "VERIFIED", # SUBMITTED, UNDER_REVIEW, VERIFIED, REJECTED, PUBLISHED
        is_published: bool = True,
        village: Optional[str] = None,
        panchayat_name: Optional[str] = None,
    ):
        self.id = id
        self.destination_id = destination_id.lower().strip()
        self.destination_name = destination_name
        self.title = title
        self.tagline = tagline
        self.address = address
        self.price_per_night_inr = price_per_night_inr
        self.rating = rating
        self.reviews_count = reviews_count
        self.room_type = room_type
        self.max_guests = max_guests
        self.amenities = amenities
        self.images = images
        self.host_id = host_id
        self.host_name = host_name
        self.host_avatar = host_avatar
        self.host_experience_years = host_experience_years
        self.host_languages = host_languages
        self.host_about = host_about
        self.host_response_rate = host_response_rate
        self.community_fund_contribution_percent = community_fund_contribution_percent
        self.special_activity = special_activity
        self.verification_status = verification_status
        self.is_published = is_published
        self.village = village
        self.panchayat_name = panchayat_name

    def to_tourist_homestay(self) -> Homestay:
        is_ver = self.verification_status in ("VERIFIED", "PUBLISHED")
        return Homestay(
            id=self.id,
            destination_id=self.destination_id,
            destination_name=self.destination_name,
            title=self.title,
            tagline=self.tagline,
            address=self.address,
            price_per_night_inr=self.price_per_night_inr,
            rating=self.rating,
            reviews_count=self.reviews_count,
            room_type=self.room_type,
            max_guests=self.max_guests,
            amenities=self.amenities,
            images=self.images,
            host=HostInfo(
                name=self.host_name,
                avatar_url=self.host_avatar,
                experience_years=self.host_experience_years,
                languages=self.host_languages,
                about=self.host_about,
                verified_panchayat=is_ver,
                response_rate=self.host_response_rate,
            ),
            community_fund_contribution_percent=self.community_fund_contribution_percent,
            special_activity=self.special_activity,
            verified=is_ver,
            panchayat_verified=is_ver,
            sustainable_stay_badge=True,
            host_id=self.host_id,
            verification_status=self.verification_status,
        )


class HomestayRepository:
    def __init__(self):
        self._records: Dict[str, AuthoritativeHomestayRecord] = {}
        self._aliases: Dict[str, str] = {}
        self._seed_authoritative_records()
        try:
            self.sync_to_db()
        except Exception:
            pass

    def _seed_authoritative_records(self):
        # 1. Kalimpong - Pineview Orchid Retreat (Host: Pemba Sherpa)
        hs_kalim_01 = AuthoritativeHomestayRecord(
            id="hs-kalimpong-01",
            destination_id="kalimpong",
            destination_name="Kalimpong",
            title="Pineview Orchid Retreat & Homestay",
            tagline="Family-run heritage cottage overlooking Kanchenjunga and organic orchids",
            address="Atisha Road, Upper Cart Road, Kalimpong - 734301",
            price_per_night_inr=2100,
            rating=4.95,
            reviews_count=84,
            room_type="Traditional Wooden Suite",
            max_guests=4,
            amenities=[
                "High-Speed Wi-Fi",
                "Home-Cooked Organic Meals",
                "Hot Water Geyser",
                "Orchid Greenhouse Access",
                "Bonfire Area"
            ],
            images=[
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-kalim-01",
            host_name="Pemba Sherpa",
            host_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
            host_experience_years=8,
            host_languages=["English", "Hindi", "Nepali", "Tibetan"],
            host_about="Third-generation orchid grower and certified mountain guide. Dedicated to zero-waste village hospitality.",
            host_response_rate="100% within 15 minutes",
            community_fund_contribution_percent=5,
            special_activity="Orchid potting workshop & traditional Lepcha cooking session",
            verification_status="VERIFIED",
            is_published=True,
            village="Upper Cart Road Village",
            panchayat_name="Kalimpong Block II Panchayat"
        )
        self._records[hs_kalim_01.id] = hs_kalim_01
        self._aliases["hs-kalim-01"] = hs_kalim_01.id

        # 2. Kalimpong - Deolo Vista Farmstay (Host: Bikram Pradhan)
        hs_kalim_02 = AuthoritativeHomestayRecord(
            id="hs-kalimpong-02",
            destination_id="kalimpong",
            destination_name="Kalimpong",
            title="Deolo Vista Farmstay",
            tagline="Quiet farm sanctuary with fresh dairy, mountain honey and Teesta valley views",
            address="Deolo Hills, Near Water Reservoir, Kalimpong - 734316",
            price_per_night_inr=2200,
            rating=4.8,
            reviews_count=62,
            room_type="Deluxe Mountain View Room",
            max_guests=2,
            amenities=["Farm-to-Table Breakfast Included", "Wi-Fi", "Solar Heating", "Trekking Guide on Demand"],
            images=[
                "https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-kalim-02",
            host_name="Bikram Pradhan",
            host_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
            host_experience_years=5,
            host_languages=["English", "Hindi", "Nepali"],
            host_about="Certified rural eco-tourism host. We believe in regenerative travel that directly supports local schools.",
            host_response_rate="Under 1 hour",
            community_fund_contribution_percent=12,
            special_activity="Beekeeping tour and evening folk flute performance",
            verification_status="VERIFIED",
            is_published=True,
            village="Deolo Hills Hamlet",
            panchayat_name="Kalimpong Block II Panchayat"
        )
        self._records[hs_kalim_02.id] = hs_kalim_02

        # 3. Lava - Neora Pine Mist Homestay (Host: Dawa Tshering Lepcha)
        hs_lava_01 = AuthoritativeHomestayRecord(
            id="hs-lava-01",
            destination_id="lava",
            destination_name="Lava",
            title="Neora Pine Mist Homestay",
            tagline="Cozy pine log cabin touching the boundary of Neora Valley National Park",
            address="Monastery Road, Lava Bazaar, Kalimpong District - 734319",
            price_per_night_inr=1850,
            rating=4.9,
            reviews_count=51,
            room_type="Pine Wood Attic Room",
            max_guests=3,
            amenities=["Organic Farm Dining", "Wood Fireplace", "Binoculars for Birding", "Nature Guide"],
            images=[
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-lava-01",
            host_name="Dawa Tshering Lepcha",
            host_avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
            host_experience_years=9,
            host_languages=["English", "Hindi", "Lepcha", "Nepali"],
            host_about="Passionate bird watcher and certified Himalayan nature guide.",
            host_response_rate="100%",
            community_fund_contribution_percent=15,
            special_activity="Early morning birding walk to spot Rufous-necked Hornbills",
            verification_status="VERIFIED",
            is_published=True,
            village="Lava Bazaar Hamlet",
            panchayat_name="Lava Forest Range Panchayat"
        )
        self._records[hs_lava_01.id] = hs_lava_01

        # 4. Lava - Neora Valley Cloud Mist Lodge (Host: Tenzin Bhutia) -> Initially UNDER_REVIEW
        hs_lava_02 = AuthoritativeHomestayRecord(
            id="hs-lava-02",
            destination_id="lava",
            destination_name="Lava",
            title="Neora Valley Cloud Mist Lodge",
            tagline="Lepcha stone cottage overlooking misty valleys and dense rhododendrons",
            address="Algarah-Lava Forest Fringe, Kalimpong District - 734319",
            price_per_night_inr=1750,
            rating=4.85,
            reviews_count=18,
            room_type="Attic Lepcha Suite",
            max_guests=3,
            amenities=["Wood Fireplace", "Homecooked Lepcha Meals", "Birding Balcony"],
            images=[
                "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-lava-02",
            host_name="Tenzin Bhutia",
            host_avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80",
            host_experience_years=4,
            host_languages=["English", "Hindi", "Nepali"],
            host_about="Traditional Lepcha homestay host passionate about indigenous forest conservation.",
            host_response_rate="100%",
            community_fund_contribution_percent=5,
            special_activity="Guided forest walk to sacred grove",
            verification_status="UNDER_REVIEW", # Hidden from tourist listings until verified
            is_published=False,
            village="Algarah-Lava Forest Fringe",
            panchayat_name="Lava Forest Range Panchayat"
        )
        self._records[hs_lava_02.id] = hs_lava_02

        # 5. Rishop - Cloud 9 Kanchenjunga Lodge (Host: Sonam Gurung)
        hs_rishop_01 = AuthoritativeHomestayRecord(
            id="hs-rishop-01",
            destination_id="rishop",
            destination_name="Rishop",
            title="Cloud 9 Kanchenjunga Lodge",
            tagline="Wake up to unobstructed 180° sunrise on snow-clad peaks",
            address="Tiffin Dara Trail, Rishop, Kalimpong District - 734319",
            price_per_night_inr=1950,
            rating=4.9,
            reviews_count=48,
            room_type="Panoramic View Cottage",
            max_guests=4,
            amenities=["Rooftop Viewing Deck", "Electric Blankets", "Authentic Gorkha Thali", "Stargazing Telescope"],
            images=[
                "https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-rishop-01",
            host_name="Sonam Gurung",
            host_avatar="https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=200&q=80",
            host_experience_years=6,
            host_languages=["English", "Hindi", "Nepali"],
            host_about="Passionate about sustainable off-grid living and eco-tourism.",
            host_response_rate="Instant",
            community_fund_contribution_percent=10,
            special_activity="Guided sunrise hike to Tiffin Dara ridge",
            verification_status="VERIFIED",
            is_published=True,
            village="Rishop Ridge",
            panchayat_name="Lava Forest Range Panchayat"
        )
        self._records[hs_rishop_01.id] = hs_rishop_01

        # 6. Lolegaon - Canopy View Heritage Homestay (Host: Nima Rai) -> Initially SUBMITTED
        hs_lole_03 = AuthoritativeHomestayRecord(
            id="hs-lole-03",
            destination_id="lolegaon",
            destination_name="Lolegaon",
            title="Canopy View Heritage Homestay",
            tagline="Quiet Lepcha home amidst centenary oaks and suspended canopy walkway",
            address="Kaffer Forest Hamlet, Lolegaon - 734319",
            price_per_night_inr=1900,
            rating=4.9,
            reviews_count=14,
            room_type="Traditional Timber Room",
            max_guests=3,
            amenities=["Pine Deck", "Traditional Hearth", "Cardamom Garden Tours"],
            images=[
                "https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80"
            ],
            host_id="host-lole-03",
            host_name="Nima Rai",
            host_avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
            host_experience_years=3,
            host_languages=["English", "Nepali"],
            host_about="Cardamom grower and indigenous folklore storyteller.",
            host_response_rate="100%",
            community_fund_contribution_percent=5,
            special_activity="Canopy walkway dawn walk & organic cardamom tasting",
            verification_status="SUBMITTED", # Hidden from tourist listings until verified
            is_published=False,
            village="Kaffer Forest Hamlet",
            panchayat_name="Lolegaon Heritage Panchayat"
        )
        self._records[hs_lole_03.id] = hs_lole_03

    def _resolve_id(self, homestay_id: str) -> str:
        clean_id = homestay_id.lower().strip()
        return self._aliases.get(clean_id, clean_id)

    def get_raw_record(self, homestay_id: str) -> Optional[AuthoritativeHomestayRecord]:
        canonical_id = self._resolve_id(homestay_id)
        return self._records.get(canonical_id)

    def get_homestay(self, homestay_id: str, visible_only: bool = False) -> Optional[Homestay]:
        record = self.get_raw_record(homestay_id)
        if not record:
            return None
        if visible_only and record.verification_status not in ("VERIFIED", "PUBLISHED"):
            return None
        return record.to_tourist_homestay()

    def list_homestays(
        self,
        destination_id: Optional[str] = None,
        max_price: Optional[int] = None,
        visible_only: bool = True
    ) -> List[Homestay]:
        """
        Lists homestays. When visible_only=True (default for tourist endpoints),
        returns ONLY VERIFIED or PUBLISHED homestays.
        Filters strictly by destination_id if provided.
        """
        results: List[Homestay] = []
        dest_filter = destination_id.lower().strip() if destination_id else None

        for rec in self._records.values():
            # Verification visibility rule: SUBMITTED, UNDER_REVIEW, REJECTED are hidden
            if visible_only and rec.verification_status not in ("VERIFIED", "PUBLISHED"):
                continue

            if dest_filter and rec.destination_id != dest_filter:
                continue

            if max_price and rec.price_per_night_inr > max_price:
                continue

            results.append(rec.to_tourist_homestay())

        return results

    def resolve_for_booking(self, homestay_id: str) -> Optional[Homestay]:
        """
        Resolves homestay for booking flow.
        Returns Homestay if found, or None if invalid.
        Does NOT silently fallback to an unrelated destination.
        """
        canonical_id = self._resolve_id(homestay_id)
        rec = self._records.get(canonical_id)
        if not rec:
            return None
        return rec.to_tourist_homestay()

    def sync_to_db(self) -> bool:
        """
        Synchronizes authoritative destinations, hosts, and homestays into SQLAlchemy models.
        Ensures foreign keys and seed records exist without duplicate key violations.
        """
        try:
            from app.core.database import SessionLocal
            from app.models.entities import DestinationModel, HostModel, HomestayModel

            db = SessionLocal()
            try:
                # 1. Ensure destinations
                dest_data = {
                    "darjeeling": ("Darjeeling", "West Bengal", 27.0410, 88.2663, 5000, False),
                    "kalimpong": ("Kalimpong", "West Bengal", 27.0594, 88.4695, 3000, False),
                    "lava": ("Lava", "West Bengal", 27.0864, 88.6611, 1000, True),
                    "lolegaon": ("Lolegaon", "West Bengal", 27.0189, 88.5583, 800, True),
                    "rishop": ("Rishop", "West Bengal", 27.1083, 88.6472, 600, True),
                    "mirik": ("Mirik", "West Bengal", 26.8910, 88.1718, 2500, False),
                }
                for d_id, (d_name, d_state, d_lat, d_lon, d_cap, d_rur) in dest_data.items():
                    existing_d = db.query(DestinationModel).filter(DestinationModel.id == d_id).first()
                    if not existing_d:
                        db.add(DestinationModel(
                            id=d_id,
                            name=d_name,
                            state=d_state,
                            latitude=d_lat,
                            longitude=d_lon,
                            carrying_capacity=d_cap,
                            is_rural=d_rur
                        ))

                # 2. Ensure hosts and homestays
                for rec in self._records.values():
                    # Host
                    existing_h = db.query(HostModel).filter(HostModel.id == rec.host_id).first()
                    if not existing_h:
                        db.add(HostModel(
                            id=rec.host_id,
                            full_name=rec.host_name,
                            phone="+91 98000 00000",
                            panchayat_name=rec.panchayat_name or "Gram Panchayat",
                            village=rec.village or "Himalayan Village",
                            state="West Bengal",
                            verification_status="VERIFIED"
                        ))

                    # Homestay
                    existing_hs = db.query(HomestayModel).filter(HomestayModel.id == rec.id).first()
                    if not existing_hs:
                        db.add(HomestayModel(
                            id=rec.id,
                            host_id=rec.host_id,
                            destination_id=rec.destination_id,
                            name=rec.title,
                            title=rec.title,
                            tagline=rec.tagline,
                            address=rec.address,
                            room_type=rec.room_type,
                            total_rooms=max(2, rec.max_guests // 2),
                            max_guests=rec.max_guests,
                            price_per_night=float(rec.price_per_night_inr),
                            latitude=27.0,
                            longitude=88.0,
                            rating=rec.rating,
                            reviews_count=rec.reviews_count,
                            panchayat_verified=rec.verification_status in ("VERIFIED", "PUBLISHED"),
                            verification_status=rec.verification_status,
                            is_published=rec.is_published,
                            village=rec.village,
                            panchayat_name=rec.panchayat_name,
                            special_activity=rec.special_activity,
                            amenities_json=rec.amenities,
                            images_json=rec.images
                        ))
                    else:
                        existing_hs.verification_status = rec.verification_status
                        existing_hs.is_published = rec.is_published

                db.commit()
                return True
            except Exception as exc:
                db.rollback()
                logger.debug(f"HomestayRepository sync_to_db notice: {exc}")
                return False
            finally:
                db.close()
        except Exception as exc:
            logger.debug(f"Database session unavailable for sync_to_db: {exc}")
            return False

    def update_verification_status(self, homestay_id: str, status: str) -> bool:
        """
        Updates verification status of authoritative homestay record.
        Called by PanchayatService when a decision is processed.
        """
        canonical_id = self._resolve_id(homestay_id)
        rec = self._records.get(canonical_id)
        if not rec:
            return False

        norm_status = status.upper().strip()
        rec.verification_status = norm_status
        rec.is_published = (norm_status in ("VERIFIED", "PUBLISHED"))

        # Synchronize with database if available
        try:
            from app.core.database import SessionLocal
            from app.models.entities import HomestayModel
            db = SessionLocal()
            try:
                db_hs = db.query(HomestayModel).filter(HomestayModel.id == canonical_id).first()
                if db_hs:
                    db_hs.verification_status = norm_status
                    db_hs.is_published = (norm_status in ("VERIFIED", "PUBLISHED"))
                    db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass

        return True

    def register_onboarding(
        self,
        listing_id: Optional[str] = None,
        homestay_id: Optional[str] = None,
        host_id: str = "host-general",
        host_name: str = "Local Himalayan Host",
        destination_id: str = "kalimpong",
        destination_name: Optional[str] = None,
        title: Optional[str] = None,
        name: Optional[str] = None,
        tagline: Optional[str] = None,
        address: Optional[str] = None,
        village: str = "Village Center",
        panchayat_name: str = "Gram Panchayat",
        price_per_night_inr: Optional[int] = None,
        price_inr: Optional[int] = None,
        room_type: str = "Standard Room",
        max_guests: int = 2,
        rooms_count: int = 2,
        amenities: Optional[List[str]] = None,
        special_activity: Optional[str] = None,
        images: Optional[List[str]] = None,
        status: Optional[str] = None,
        verification_status: Optional[str] = None,
        **kwargs: Any
    ) -> AuthoritativeHomestayRecord:
        """
        Registers newly onboarded homestay from HostService with SUBMITTED status.
        Hidden from tourist listings until verified by Panchayat.
        Supports homestay_id/listing_id and other aliases.
        """
        final_id = listing_id or homestay_id or f"hs-{destination_id}-{uuid.uuid4().hex[:4]}"
        final_title = title or name or f"{destination_id.capitalize()} Village Retreat"
        final_dest_name = destination_name or destination_id.capitalize()
        final_price = price_per_night_inr or price_inr or 2000
        final_status = (verification_status or status or "SUBMITTED").upper()
        final_address = address or f"{village}, {final_dest_name}"
        final_tagline = tagline or "Authentic Himalayan homestay experience"

        rec = AuthoritativeHomestayRecord(
            id=final_id,
            destination_id=destination_id,
            destination_name=final_dest_name,
            title=final_title,
            tagline=final_tagline,
            address=final_address,
            price_per_night_inr=final_price,
            rating=5.0,
            reviews_count=0,
            room_type=room_type,
            max_guests=max_guests,
            amenities=amenities or ["Mountain View", "Home Cooked Meals"],
            images=images or ["https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80"],
            host_id=host_id,
            host_name=host_name,
            host_avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
            host_experience_years=2,
            host_languages=["English", "Hindi", "Nepali"],
            host_about="Local Himalayan host dedicated to village hospitality.",
            host_response_rate="New Host",
            community_fund_contribution_percent=5,
            special_activity=special_activity or "Guided village farm walk",
            verification_status=final_status,
            is_published=(final_status in ("VERIFIED", "PUBLISHED")),
            village=village,
            panchayat_name=panchayat_name
        )
        self._records[rec.id] = rec

        # Persist newly onboarded host and homestay to database if available
        try:
            from app.core.database import SessionLocal
            from app.models.entities import HomestayModel, HostModel, DestinationModel
            db = SessionLocal()
            try:
                # Ensure destination exists
                if not db.query(DestinationModel).filter(DestinationModel.id == destination_id).first():
                    db.add(DestinationModel(
                        id=destination_id,
                        name=final_dest_name,
                        state="West Bengal",
                        latitude=27.0,
                        longitude=88.0,
                        carrying_capacity=2000,
                        is_rural=True
                    ))
                # Ensure host exists
                if not db.query(HostModel).filter(HostModel.id == host_id).first():
                    db.add(HostModel(
                        id=host_id,
                        full_name=host_name,
                        phone="+91 98000 00000",
                        panchayat_name=panchayat_name,
                        village=village,
                        state="West Bengal",
                        verification_status="VERIFIED"
                    ))
                # Upsert homestay
                existing_hs = db.query(HomestayModel).filter(HomestayModel.id == rec.id).first()
                if not existing_hs:
                    db.add(HomestayModel(
                        id=rec.id,
                        host_id=rec.host_id,
                        destination_id=rec.destination_id,
                        name=rec.title,
                        title=rec.title,
                        tagline=rec.tagline,
                        address=rec.address,
                        room_type=rec.room_type,
                        total_rooms=rooms_count,
                        max_guests=rec.max_guests,
                        price_per_night=float(rec.price_per_night_inr),
                        latitude=27.0,
                        longitude=88.0,
                        rating=rec.rating,
                        reviews_count=rec.reviews_count,
                        panchayat_verified=(final_status in ("VERIFIED", "PUBLISHED")),
                        verification_status=rec.verification_status,
                        is_published=rec.is_published,
                        village=rec.village,
                        panchayat_name=rec.panchayat_name,
                        special_activity=rec.special_activity,
                        amenities_json=rec.amenities,
                        images_json=rec.images
                    ))
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass

        return rec


# Global Singleton Instance
homestay_repository = HomestayRepository()
