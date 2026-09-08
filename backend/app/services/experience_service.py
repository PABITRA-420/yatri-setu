from typing import List, Optional
from app.models.experience import Experience, ExperienceCreateRequest

SEED_EXPERIENCES = [
    {
        "id": "exp-darj-01",
        "title": "Makaibari Biodynamic Tea Plucking & Tasting Masterclass",
        "description": "Walk among centenarian tea bushes alongside third-generation women tea pluckers. Learn two leaves and a bud precision harvest, followed by private factory cupping of rare silver-tip muscatel teas.",
        "host_id": "host-darj-01",
        "host_name": "Maya Tamang",
        "destination_id": "darjeeling",
        "destination_name": "Darjeeling",
        "village": "Kurseong-Makaibari Valley",
        "panchayat_name": "Makaibari Gram Panchayat",
        "duration_hours": 3.5,
        "price_inr": 1250,
        "capacity": 8,
        "languages": ["English", "Hindi", "Nepali"],
        "sustainability_score": 96,
        "verification_status": "VERIFIED",
        "category": "Agri-Tourism",
        "image_url": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Hand-pick organic first-flush tea leaves with local pluckers",
            "Learn biodynamic astral calendar planting philosophies",
            "Tasting session of 5 world-famous Darjeeling flushes"
        ],
        "gear_provided": ["Traditional bamboo plucking basket (Doko)", "Loom woven cotton apron", "Sampling tasting cup"]
    },
    {
        "id": "exp-kalim-01",
        "title": "Rare Cymbidium Orchid Hybridisation & Tibetan Woodblock Art",
        "description": "Exclusive hands-on workshop at a 50-year-old family orchid sanctuary in Kalimpong. Learn delicate pollen transfer for Himalayan orchids, followed by traditional Tibetan woodblock printing on handmade daphne bark paper.",
        "host_id": "host-kalim-01",
        "host_name": "Pemba Sherpa",
        "destination_id": "kalimpong",
        "destination_name": "Kalimpong",
        "village": "Upper Cart Road Village",
        "panchayat_name": "Kalimpong Block II Panchayat",
        "duration_hours": 2.5,
        "price_inr": 850,
        "capacity": 6,
        "languages": ["English", "Hindi", "Nepali", "Tibetan"],
        "sustainability_score": 94,
        "verification_status": "VERIFIED",
        "category": "Artisan & Craft",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Learn orchid cross-pollination in a climate-controlled greenhouse",
            "Print your own Tibetan prayer flag using heritage woodblocks",
            "Sip authentic hot salted butter tea (Po Cha)"
        ],
        "gear_provided": ["Precision horticultural tweezers", "Cotton handmade paper", "Herbal mineral pigments"]
    },
    {
        "id": "exp-lava-01",
        "title": "Neora Valley Virgin Canopy Birding & Hornbill Tracking",
        "description": "Early dawn canopy birding expedition into Neora Valley National Park's subtropical montane forest with a veteran Lepcha naturalist. Track rare Rufous-necked Hornbills, Scarlet Minivets, and medicinal mosses.",
        "host_id": "host-lava-01",
        "host_name": "Dawa Tshering Lepcha",
        "destination_id": "lava",
        "destination_name": "Lava",
        "village": "Lava Bazaar Village",
        "panchayat_name": "Lava Forest Range Panchayat",
        "duration_hours": 4.0,
        "price_inr": 1100,
        "capacity": 5,
        "languages": ["English", "Hindi", "Lepcha", "Nepali"],
        "sustainability_score": 98,
        "verification_status": "VERIFIED",
        "category": "Forest & Wildlife",
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Spot 30+ rare Himalayan bird species with high-power spotting scopes",
            "Learn indigenous Lepcha herbal folklore and medicinal plant identification",
            "Zero plastic leave-no-trace trail protocol"
        ],
        "gear_provided": ["High-index roof prism binoculars", "Himalayan field bird identification guide", "Bamboo walking pole"]
    },
    {
        "id": "exp-lole-01",
        "title": "Heritage Wooden Suspension Canopy Walk & Forest Bathing",
        "description": "Gentle sensory immersion and Japanese Shinrin-yoku (forest bathing) along Lolegaon's historic 180-meter suspended oak canopy bridge. Accompanied by traditional bamboo flute meditation and green cardamom pod harvest.",
        "host_id": "host-lole-01",
        "host_name": "Phurba Lama",
        "destination_id": "lolegaon",
        "destination_name": "Lolegaon",
        "village": "Kaffer Village",
        "panchayat_name": "Lolegaon Heritage Panchayat",
        "duration_hours": 3.0,
        "price_inr": 750,
        "capacity": 8,
        "languages": ["English", "Hindi", "Nepali"],
        "sustainability_score": 95,
        "verification_status": "VERIFIED",
        "category": "Spiritual Heritage",
        "image_url": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Private morning access to tree canopy walkway before any tourist groups",
            "Guided breathing and meditation among century-old cryptomeria pines",
            "Fresh organic cardamom roasting demo"
        ],
        "gear_provided": ["Woolen meditation sitting mat", "Fresh mountain spring infusion thermos"]
    },
    {
        "id": "exp-rish-01",
        "title": "Tiffin Dara Ridge Sunrise Hike & Organic Nettle Tea Ceremony",
        "description": "Hike through silent rhododendron ridges up to Tiffin Dara (8,200 ft) for a 180° sunrise view stretching from Mt. Kanchenjunga to Nathula Pass. Conclude with a traditional hot nettle-leaf and millet pancake breakfast at a village homestead.",
        "host_id": "host-rish-01",
        "host_name": "Sonam Gurung",
        "destination_id": "rishop",
        "destination_name": "Rishop",
        "village": "Upper Rishop Hamlet",
        "panchayat_name": "Rishop Ridge Panchayat",
        "duration_hours": 3.5,
        "price_inr": 900,
        "capacity": 6,
        "languages": ["English", "Hindi", "Nepali"],
        "sustainability_score": 97,
        "verification_status": "VERIFIED",
        "category": "Culinary & Foraging",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Watch early light paint Kanchenjunga golden without Mall road crowds",
            "Forage wild Himalayan stinging nettle (Sisnu) leaves safely",
            "Traditional hearth cooking with freshly milled buckwheat pancakes (Phapar Roti)"
        ],
        "gear_provided": ["Headlamp for pre-dawn hike", "Trekking poles", "Thermal travel mug"]
    },
    {
        "id": "exp-mirik-01",
        "title": "Orange Orchard Beekeeping & Bokar Monastery Butter Lamp Ritual",
        "description": "Visit an organic terraced citrus grove overlooking Sumendu Lake. Experience native stingless bee honey tasting, followed by an evening invitation to light 108 butter lamps with resident monks at Bokar Gompa.",
        "host_id": "host-mirik-01",
        "host_name": "Chhiring Subba",
        "destination_id": "mirik",
        "destination_name": "Mirik",
        "village": "Bunkulung Agro Hamlet",
        "panchayat_name": "Mirik Valley Panchayat",
        "duration_hours": 3.0,
        "price_inr": 800,
        "capacity": 7,
        "languages": ["English", "Hindi", "Nepali"],
        "sustainability_score": 93,
        "verification_status": "VERIFIED",
        "category": "Agri-Tourism",
        "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "highlights": [
            "Safe inspect-and-taste hive session with native stingless Himalayan honeybees",
            "Pick sweet Mirik mandarins directly from terrace orchards (seasonal)",
            "Peaceful butter lamp blessing inside Bokar Ngedon Chokhor Ling"
        ],
        "gear_provided": ["Protective beekeeping veil hat", "Locally made clay butter lamp vessel"]
    }
]

class ExperienceService:
    def __init__(self):
        self._experiences: List[Experience] = [Experience(**e) for e in SEED_EXPERIENCES]

    def list_experiences(
        self,
        destination_id: Optional[str] = None,
        verified_only: bool = True
    ) -> List[Experience]:
        results = self._experiences
        if destination_id:
            results = [e for e in results if e.destination_id == destination_id.lower().strip()]
        if verified_only:
            results = [e for e in results if e.verification_status in ["VERIFIED", "PUBLISHED"]]
        return results

    def get_experience_by_id(self, experience_id: str) -> Optional[Experience]:
        for e in self._experiences:
            if e.id == experience_id:
                return e
        return None

    def create_experience(self, req: ExperienceCreateRequest) -> Experience:
        new_id = f"exp-custom-{len(self._experiences) + 1:02d}"
        dest_name_map = {
            "darjeeling": "Darjeeling",
            "kalimpong": "Kalimpong",
            "lava": "Lava",
            "lolegaon": "Lolegaon",
            "rishop": "Rishop",
            "mirik": "Mirik"
        }
        dest_name = dest_name_map.get(req.destination_id.lower().strip(), req.destination_id.title())
        new_exp = Experience(
            id=new_id,
            title=req.title,
            description=req.description,
            host_id=req.host_id,
            host_name="Host Participant",
            destination_id=req.destination_id.lower().strip(),
            destination_name=dest_name,
            village=f"{dest_name} Rural Circle",
            panchayat_name=f"{dest_name} Gram Panchayat",
            duration_hours=req.duration_hours,
            price_inr=req.price_inr,
            capacity=req.capacity,
            languages=req.languages,
            sustainability_score=92,
            verification_status="UNDER_REVIEW", # Needs panchayat sign-off
            category=req.category,
            image_url=req.image_url or "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
            highlights=req.highlights or ["Handcrafted local immersion", "Direct family economic support"]
        )
        self._experiences.append(new_exp)
        return new_exp

# Global singleton
experience_service = ExperienceService()
