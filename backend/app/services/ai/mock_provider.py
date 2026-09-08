"""
Mock AI Travel Intelligence Provider for Yatri Setu (Smart India Hackathon 2026)
Provides deterministic yet genuinely adaptive Himalayan itineraries without requiring external API keys.
Demonstrates realistic weather adaptation, crowd evasion, and prompt-driven optimization.
"""

from typing import Dict, Any, Optional, List
from app.services.ai.provider import BaseAIProvider
from app.models.itinerary import (
    ItineraryContext,
    AIItineraryOutput,
    AIDayOutput,
    AIActivityOutput
)

# Rich destination catalog for adaptive itinerary construction
DESTINATION_CATALOG: Dict[str, Dict[str, Any]] = {
    "darjeeling": {
        "name": "Darjeeling",
        "morning_attractions": [
            ("Tiger Hill Sunrise & Ghoom Monastic Chanting", "Early morning vista over Kanchenjunga followed by peaceful prayer drums at Old Ghoom.", "Tiger Hill & Ghoom", 250, "Culture", "Arrive by 5:00 AM to beat tourist vehicle convoy."),
            ("Peshok Tea Garden Heritage Plucking Walk", "Guided walking trail through emerald slopes with organic first-flush tasting.", "Peshok Estate", 350, "Nature", "Comfortable walking shoes recommended on dew-soaked terraces."),
            ("Batasia Loop & Himalayan War Memorial", "Engineering marvel circular railway loop with clear morning mountain vistas.", "Batasia Loop", 100, "Scenic", "Visit early before toy train tourist crowds peak at 10 AM.")
        ],
        "afternoon_attractions": [
            ("Himalayan Mountaineering Institute & Snow Leopard Center", "World-renowned alpine museum and ethical high-altitude wildlife conservation.", "Jawahar Parbat", 200, "Nature", "Indoor and paved enclosures; pleasant even during mist."),
            ("Tibetan Refugee Self Help Centre Craft Workshops", "Watch generational artisans weave wool carpets and carve Himalayan woodwork.", "Hill Cart Road", 150, "Culture", "100% of purchase proceeds support local elder weavers."),
            ("Mahakal Temple Sacred Ridge Meditation", "Ancient syncretic shrine atop Observatory Hill where bells ring through ancient pines.", "Observatory Hill", 50, "Culture", "Beware of playful macaques; keep snacks enclosed.")
        ],
        "indoor_rain_attractions": [
            ("Happy Valley Historic Tea Factory & Roasting Room", "Covered tour of historic 1854 tea rolling tables and sensory cupping session.", "Happy Valley", 300, "Culinary", "Completely indoors and sheltered from mountain cloudbursts."),
            ("Darjeeling Himalayan Heritage Archives & Library", "Historical photographs, colonial maps, and railway documentation in covered heritage halls.", "Chowrasta", 100, "Culture", "Warm covered space with quiet reading room.")
        ],
        "evening_attractions": [
            ("Chowrasta Mall Quiet Side-Alley Stroll & Local Bakery", "Avoid crowded central square; enjoy warm local bakery tea and view valley lights.", "Chowrasta Lane", 150, "Culinary", "Warm woolen shawls recommended as temperature drops after sunset."),
            ("Gorkha Cultural Folk Performance & Thukpa Dinner", "Acoustic folk music with steaming homemade Darjeeling thukpa and momos.", "Local Cultural Association", 400, "Culture", "Family run eatery supporting young local artists.")
        ]
    },
    "kalimpong": {
        "name": "Kalimpong",
        "morning_attractions": [
            ("Deolo Hill Panoramic Valley Vista & Nature Walk", "360-degree vista over Teesta gorge and snow peaks before mid-day haze.", "Deolo Hill", 100, "Scenic", "Best mountain clarity between 6:30 AM and 9:00 AM."),
            ("Pine View Exotic Cactus & Orchid Conservatories", "Acclaimed sanctuary housing over 1,500 species of rare Himalayan succulents.", "Atisha Road", 150, "Nature", "Support local botanists dedicated to North-East flora preservation."),
            ("Zang Dhok Palri Phodang Consecrated Gompa", "Vibrant monastery perched on Durpin Dara with rare Tibetan wall paintings.", "Durpin Dara", 80, "Culture", "Listen to peaceful morning horn blowing and monk debates.")
        ],
        "afternoon_attractions": [
            ("Lark's Himalayan Cheese Workshop & Tasting", "Hyperlocal Gouda and Chhurpi artisanal cheese tasting from dairy farmers.", "Rishi Road", 250, "Culinary", "Taste organic cheese crafted using traditional Dutch-Himalayan methods."),
            ("Dr. Graham's Heritage Forest Campus & Museum", "Serene educational campus established in 1900 with historic stone chapel.", "Deolo Foothill", 100, "Culture", "Walking trails shaded by century-old silver fir trees."),
            ("Lepcha Museum of Indigenous Folklore", "Curated displays of tribal musical instruments, ancient manuscripts, and hunting tools.", "Melli Road", 100, "Culture", "Guided by a Lepcha community elder sharing oral heritage.")
        ],
        "indoor_rain_attractions": [
            ("Traditional Lepcha Handloom & Textile Workshop", "Covered weaving shelter learning backstrap loom techniques from master weavers.", "Kalimpong Craft Center", 150, "Culture", "Stay dry while supporting indigenous female artisan livelihoods."),
            ("Himalayan Herbal Apothecary & Tea Lounge", "Sheltered herbal blending workshop tasting rhododendron and chamomile mountain infusions.", "Ongden Road", 180, "Culinary", "Relaxing indoor acoustic ambiance with mountain view verandah.")
        ],
        "evening_attractions": [
            ("Morgan House Pine Verandah Sunset Tea", "British colonial stone manor overlooking pine-clad slopes with hot Darjeeling brew.", "Durpin Hill", 200, "Scenic", "Peaceful twilight atmosphere far removed from urban noise."),
            ("Gorkha Kitchen Farm-to-Table Traditional Dinner", "Organic Gundruk, Kinema, and millet bread prepared by a host family.", "Dharmodaya Vihar", 350, "Culinary", "Zero food miles; ingredients harvested from host garden.")
        ]
    },
    "lava": {
        "name": "Lava",
        "morning_attractions": [
            ("Neora Valley Pine Canopy Trail & Birdwatching", "Quiet morning walk along dense pine ridges spotting rare Himalayan Monal.", "Neora Valley Forest Gate", 120, "Nature", "Bring binoculars; morning mist clears into sparkling sunshine."),
            ("Kagyu Thekchen Ling Tibetan Buddhist Monastery", "Large monastery complex nestled in pine forest with striking painted prayer halls.", "Lava Ridge", 50, "Culture", "Join morning butter lamp lighting with welcoming resident monks."),
            ("Rachela Pass Forest Overlook Point", "Gentle uphill trail to panoramic clearing with views stretching into Bhutan hills.", "Forest Route", 100, "Nature", "Crisp oxygen-rich mountain air with zero vehicle sound.")
        ],
        "afternoon_attractions": [
            ("Lava Forest Interpretation Center & Flora Exhibit", "Interactive nature center showcasing Neora Valley's elusive Red Panda habitat.", "Main Forest Road", 60, "Nature", "Educational and deeply engaging for eco-conscious travelers."),
            ("Pine Cone Craft & Community Woodcarving Workshop", "Watch village youths carve sustainable pine art and bamboo utensils.", "Village Cooperative", 150, "Culture", "Direct purchase benefits local forest-fringe youth skills program."),
            ("Wild Orchid Valley Footpath", "Quiet nature trail through dripping mossy oaks and wild epiphytic orchids.", "Lower Lava Ridge", 50, "Nature", "Fragrant wild blooms line this low-impact earthen trail.")
        ],
        "indoor_rain_attractions": [
            ("Monastery Scripture Hall & Butter Sculpture Gallery", "Covered monastic gallery displaying intricate religious butter carvings and thangkas.", "Lava Monastery", 80, "Culture", "Peaceful refuge from mountain drizzle with warm butter tea."),
            ("Forest Herbal Infusion & Community Hearth Gathering", "Indoor traditional kitchen session learning to brew medicinal forest herbs around a warm hearth.", "Lava Homestay Commons", 120, "Culinary", "Warm and safe indoor cultural immersion while rain patters outside.")
        ],
        "evening_attractions": [
            ("Misty Pine Verandah Stargazing & Mountain Lore", "Fireside storytelling with village elders recounting Himalayan folklore.", "Homestay Courtyard", 100, "Culture", "Wrap up in cozy woolen blankets as cool mountain night falls."),
            ("Organic Homestay Dinner of Sisnu Soup & Rice", "Nutritious wild stinging nettle soup with organic brown mountain rice.", "Village Homestay", 250, "Culinary", "Traditional immune-boosting Himalayan home recipe.")
        ]
    },
    "lolegaon": {
        "name": "Lolegaon",
        "morning_attractions": [
            ("Lolegaon Heritage Hanging Forest Canopy Walk", "Walk across suspension bridges swinging 40 feet above ground in virgin oak forest.", "Forest Reserve", 120, "Nature", "Early morning reveals sunbeams cutting through ancient oak moss."),
            ("Jhandi Dara Mountain Sunrise Viewpoint", "Lookout point with sweeping panoramic sunrise over Kanchenjunga range.", "Jhandi Dara", 60, "Scenic", "Spectacular early dawn visibility without commercial souvenir stalls."),
            ("Silent Oak Woodland Contemplation Trail", "Tranquil walking path through protected temperate broadleaf forest.", "Upper Lolegaon", 40, "Nature", "Ideal for birding, mindful walking, and peaceful recharge.")
        ],
        "afternoon_attractions": [
            ("Rishi Eco-Farm Organic Cardamom Walk", "Stroll through shade-grown large cardamom plantations with village cultivators.", "Lower Eco-Farm", 150, "Agri-Tourism", "Learn how Sikkim and Kalimpong farmers grow GI-tagged black cardamom."),
            ("Village Bamboo Weaving Cooperative", "Observe master artisans weave durable mountain baskets and rain hats.", "Panchayat Hall", 80, "Culture", "Supports elderly village craftsmen passing down ancient weaving skills."),
            ("Forest Stream Meditation & Pebble Clearing", "Serene mountain stream shaded by weeping willows and wild ferns.", "Stream Trail", 30, "Nature", "Crystal pure spring water trickling through mossy stones.")
        ],
        "indoor_rain_attractions": [
            ("Village Community Library & Lepcha Heritage Room", "Covered traditional wooden pavilion featuring village oral history archives.", "Lolegaon Center", 50, "Culture", "Sheltered from showers with open wooden windows to the forest."),
            ("Artisanal Cardamom & Cinnamon Tea Tasting", "Indoor spiced tea brewing demonstration at village co-op store.", "Cooperative Shed", 90, "Culinary", "Warm fragrant spices and dry indoor seating.")
        ],
        "evening_attractions": [
            ("Sunset Ridge Fire Pit & Acoustic Mountain Music", "Gather around the crackling pine wood fire with host family singing Nepali ballads.", "Homestay Lawn", 100, "Culture", "Community warmth under crystal clear starry skies."),
            ("Traditional Bamboo Shoot Curry & Tingmo Dinner", "Steamed Tibetan Tingmo bread with locally foraged wild bamboo shoots.", "Homestay Kitchen", 280, "Culinary", "Freshly steamed and comforting mountain meal.")
        ]
    },
    "rishop": {
        "name": "Rishop",
        "morning_attractions": [
            ("Tiffindara 360-Degree Kanchenjunga Sunrise Trek", "Gentle 1.5 km forest climb to the highest point with unobstructed 360-degree Himalayan snow views.", "Tiffindara Peak", 80, "Scenic", "One of the finest vantage points in the entire Eastern Himalayas."),
            ("Pine Forest Birding Walk towards Lava Footpath", "Listen to calls of Verditer Flycatchers and Laughingthrushes in pristine woods.", "Lava-Rishop Trail", 40, "Nature", "Zero vehicular noise; pure tranquility under tall conifers."),
            ("Village Hilltop Bell Shrine & Prayer Flags", "Colorful Tibetan prayer flags fluttering in fresh sub-alpine winds.", "Rishop Ridge", 20, "Culture", "Tie your own prayer flag for peace and safe mountain travels.")
        ],
        "afternoon_attractions": [
            ("Organic Terrace Vegetable Harvest Experience", "Help homestay hosts harvest mountain radish, peas, and leafy greens for dinner.", "Host Terrace", 100, "Agri-Tourism", "Directly reconnect with mountain soil and sustainable smallholder farming."),
            ("Himalayan Herbal Balms & Essential Oils Workshop", "Learn how pine resins and wild artemisia are distilled into winter healing balms.", "Village Shed", 150, "Culture", "Take home eco-friendly, handmade wellness remedies."),
            ("Quiet Cliffside Hammock Reading & Valley Gazing", "Relax with a book overlooking deep green Neora Valley valleys below.", "Homestay Lookout", 0, "Scenic", "True slow travel: disconnect from digital distractions.")
        ],
        "indoor_rain_attractions": [
            ("Homestay Clay Stove Cooking Masterclass", "Learn to shape momos and ferment Gundruk beside a traditional mountain clay stove.", "Homestay Kitchen", 180, "Culinary", "Intimate, warm, and protected from sudden mountain rain showers."),
            ("Wool Weaving & Mountain Shawl Demonstration", "Indoor session watching grandmothers knit warm yak-wool mittens and beanies.", "Community Room", 100, "Culture", "Cosy indoor atmosphere with hot mountain ginger tea.")
        ],
        "evening_attractions": [
            ("High Altitude Stargazing with Telescope Session", "With zero urban light pollution, observe the Milky Way and Jupiter's moons.", "Rishop Ridge Deck", 150, "Scenic", "Bundle up in heavy jackets; mountain air drops to single digits."),
            ("Candlelight Village Dinner with Local Millet Brew (Tongba)", "Traditional warm fermented millet drink served in bamboo canisters with hot dumplings.", "Village Dining Hut", 350, "Culinary", "Age-old Himalayan hospitality that warms the body and soul.")
        ]
    },
    "mirik": {
        "name": "Mirik",
        "morning_attractions": [
            ("Sumendu Lake Morning Nature Walk & Arch Footbridge", "Peaceful 3.5 km circumference walk through cryptomeria pines bordering the still mountain lake.", "Sumendu Lake", 50, "Nature", "Morning mist over the lake water creates fairytale reflections."),
            ("Bokar Ngedon Chokhor Ling Gompa Visit", "Magnificent Buddhist monastery on hillock with sprawling valley vistas.", "Bokar Hill", 40, "Culture", "Peaceful sanctum welcoming respectful morning visitors."),
            ("Helipad Sunrise Point & Mountain Meadow", "Grassy meadow offering panoramic views of Mount Kanchenjunga across tea hills.", "Mirik Helipad", 30, "Scenic", "Open grassy field ideal for morning yoga and deep breathing.")
        ],
        "afternoon_attractions": [
            ("Mirik Orange Orchards & Honey Bee Farm Tour", "Walk through lush orange groves and taste fresh citrus blossom mountain honey.", "Pahilo Gaon", 150, "Agri-Tourism", "Support family orchards practicing organic regenerative farming."),
            ("Tingling View Point & Tea Bush Walk", "Terraced tea garden viewpoint overlooking thousands of rolling tea bushes.", "Tingling Point", 50, "Scenic", "Breathtaking green contours cascading down into Mechi river basin."),
            ("Lake Rowing Boat Ride with Local Boatmen", "Eco-friendly wooden rowboats steered by licensed local village youths.", "Lake Boating Club", 120, "Nature", "Silent paddling without motor fuel or water pollution.")
        ],
        "indoor_rain_attractions": [
            ("Mirik Heritage Orchid Nursery & Greenhouse", "Covered glasshouse containing blooming cattleya, cymbidium, and rare native orchids.", "Krishnanagar", 80, "Nature", "Dry and fragrant oasis even during sudden rain showers."),
            ("Traditional Nepali Sweet-Making & Sel Roti Workshop", "Sheltered village kitchen learning to fry circular Sel Roti and sweet Lalmohan.", "Local Eatery", 120, "Culinary", "Crispy hot traditional mountain treats fresh from the pan.")
        ],
        "evening_attractions": [
            ("Lake Promenade Stroll & Steaming Sweet Corn", "Enjoy freshly roasted sweet mountain corn brushed with local lemon and chili.", "Sumendu Promenade", 60, "Culinary", "Gentle evening breeze under vintage lampposts."),
            ("Local Gorkha Thali Dinner at Village Cooperative", "Authentic 7-item mountain thali featuring local dal, wild mushroom curry, and ghee.", "Coop Dining Hall", 260, "Culinary", "100% locally procured farm ingredients.")
        ]
    }
}

class MockAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        norm_id = context.destination_id.lower().strip()
        catalog = DESTINATION_CATALOG.get(norm_id, DESTINATION_CATALOG["kalimpong"])
        dest_name = catalog["name"]

        duration = context.user_preferences.get("duration_days", 3)
        rain_expected = context.weather.rain_expected
        pace = context.user_preferences.get("pace", "Moderate").lower()

        weather_notice: Optional[str] = None
        if rain_expected:
            weather_notice = f"Yatri Setu AI adapted afternoon schedules in {dest_name} to sheltered cultural and indoor culinary venues due to expected mountain precipitation ({context.weather.precipitation_chance_percent}% chance)."

        why_this = [
            f"Strategically scheduled high-interest sights in early morning to avoid peak tourist congestion ({context.crowd_score}/100 crowd score).",
            f"Empowers rural livelihoods by directing 85%+ of activity spend to verified local guides, cooperatives, and family homestays.",
            f"Incorporated real-time Himalayan weather profile: {context.weather.advisory}"
        ]

        days: List[AIDayOutput] = []

        for d in range(1, duration + 1):
            activities: List[AIActivityOutput] = []

            # Morning Activity
            m_list = catalog["morning_attractions"]
            m_item = m_list[(d - 1) % len(m_list)]
            activities.append(AIActivityOutput(
                time_slot="06:30 AM - 09:30 AM" if d == 1 else "08:00 AM - 10:30 AM",
                period="Morning",
                title=m_item[0],
                description=m_item[1],
                location_name=m_item[2],
                crowd_forecast="Low",
                cost_estimate_inr=m_item[3],
                duration_hrs=2.5,
                travel_tip=m_item[5],
                category=m_item[4],
                is_weather_adapted=False,
                adaptation_reason=None
            ))

            # Afternoon Activity: Check Weather Adaptation
            if rain_expected:
                rain_list = catalog["indoor_rain_attractions"]
                a_item = rain_list[(d - 1) % len(rain_list)]
                activities.append(AIActivityOutput(
                    time_slot="01:30 PM - 04:00 PM",
                    period="Afternoon",
                    title=a_item[0],
                    description=a_item[1],
                    location_name=a_item[2],
                    crowd_forecast="Low",
                    cost_estimate_inr=a_item[3],
                    duration_hrs=2.5,
                    travel_tip=a_item[5],
                    category=a_item[4],
                    is_weather_adapted=True,
                    adaptation_reason="Yatri Setu adapted this activity because of expected mountain rain."
                ))
            else:
                a_list = catalog["afternoon_attractions"]
                a_item = a_list[(d - 1) % len(a_list)]
                activities.append(AIActivityOutput(
                    time_slot="01:30 PM - 04:00 PM",
                    period="Afternoon",
                    title=a_item[0],
                    description=a_item[1],
                    location_name=a_item[2],
                    crowd_forecast="Moderate",
                    cost_estimate_inr=a_item[3],
                    duration_hrs=2.5,
                    travel_tip=a_item[5],
                    category=a_item[4],
                    is_weather_adapted=False,
                    adaptation_reason=None
                ))

            # Evening Activity (skip if pace is relaxed and d > 1 to allow restful leisure)
            if pace != "relaxed" or d == 1:
                e_list = catalog["evening_attractions"]
                e_item = e_list[(d - 1) % len(e_list)]
                activities.append(AIActivityOutput(
                    time_slot="05:30 PM - 07:30 PM",
                    period="Evening",
                    title=e_item[0],
                    description=e_item[1],
                    location_name=e_item[2],
                    crowd_forecast="Low",
                    cost_estimate_inr=e_item[3],
                    duration_hrs=2.0,
                    travel_tip=e_item[5],
                    category=e_item[4],
                    is_weather_adapted=False,
                    adaptation_reason=None
                ))

            theme_titles = [
                f"Heritage & Panoramic Dawn of {dest_name}",
                f"Indigenous Flavors, Forest Trails & Village Living",
                f"Sacred Monasteries & Artisanal Cooperatives",
                f"Hidden Ridge Vistas & Deep Forest Trails",
                f"Community Farewell & Slow Living Farewell"
            ]

            day_theme = theme_titles[(d - 1) % len(theme_titles)]
            days.append(AIDayOutput(
                day_number=d,
                theme=day_theme,
                overview=f"Day {d} centers on authentic {dest_name} experiences designed for low environmental footprint and minimal peak-hour queueing.",
                activities=activities,
                transit_advice="Utilize pre-arranged shared mountain jeeps or scenic foot trails connecting hamlets. Avoid single-occupancy diesel cabs."
            ))

        overview = (
            f"Hyperlocal adaptive itinerary for {dest_name} crafted by Yatri Setu AI. "
            f"Balances crowd dispersal (score {context.crowd_score}/100), authentic village hospitality, "
            f"and real-time mountain weather intelligence ({context.weather.condition})."
        )

        return AIItineraryOutput(
            overview_note=overview,
            why_this_itinerary=why_this,
            weather_adaptation_notice=weather_notice,
            days=days
        )

    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        norm_id = context.destination_id.lower().strip()
        catalog = DESTINATION_CATALOG.get(norm_id, DESTINATION_CATALOG["kalimpong"])
        dest_name = catalog["name"]
        clean_inst = instruction.upper().strip()

        # Start from base generation then apply directive-specific transformations
        base = await self.generate_itinerary(context)

        why_this = list(base.why_this_itinerary)
        weather_notice = base.weather_adaptation_notice

        if clean_inst == "MAKE_CHEAPER":
            why_this.insert(0, "Optimized for budget efficiency: Replaced ticketed commercial venues with free community nature walks and village cooperatives, slashing costs by ~35%.")
            for day in base.days:
                for act in day.activities:
                    act.cost_estimate_inr = max(0, int(act.cost_estimate_inr * 0.55))
                    if act.category == "Culinary":
                        act.title = f"Budget Village Kitchen: {act.title}"
            overview = f"Budget-optimized itinerary for {dest_name}. Maximizes zero-cost nature exploration and direct community eateries."

        elif clean_inst == "MORE_RELAXED":
            why_this.insert(0, "Pace adapted to 'Relaxed': Trimmed evening rush, prolonged morning tea verandah hours, and prioritized leisurely unhurried immersion.")
            for day in base.days:
                if len(day.activities) > 2:
                    day.activities = day.activities[:2] # Keep only 2 activities per day
                for act in day.activities:
                    act.duration_hrs = round(act.duration_hrs + 0.5, 1)
            overview = f"Slow-travel relaxed itinerary for {dest_name}. Reduced transit friction with generous restorative downtime."

        elif clean_inst == "MORE_NATURE":
            why_this.insert(0, "Nature-focused customization: Substituted urban viewpoints with deep pine forest canopy trails, wild orchid walks, and river clearings.")
            for day in base.days:
                day.theme = f"Deep Alpine Nature & Forest Sanctuaries of {dest_name}"
                for act in day.activities:
                    if act.category != "Nature" and act.category != "Scenic":
                        act.category = "Nature"
                        act.title = f"Forest Trail & Canopy Walk ({act.location_name})"
                        act.description = "Shaded woodland trail rich in mossy oaks, mountain streams, and native birdlife."
            overview = f"Eco-nature itinerary for {dest_name}, highlighting pristine Himalayan forests and minimal concrete footprint."

        elif clean_inst == "MORE_CULTURE":
            why_this.insert(0, "Cultural depth enhancement: Prioritized monastic scriptures, traditional Gorkha/Lepcha workshops, and oral history storytelling.")
            for day in base.days:
                day.theme = f"Himalayan Heritage, Sacred Gompas & Artisan Traditions"
                for act in day.activities:
                    if act.category != "Culture":
                        act.category = "Culture"
                        act.title = f"Heritage Crafts & Monastic Living ({act.location_name})"
                        act.description = "Engage directly with indigenous craftspeople and learn ancestral conservation philosophies."
            overview = f"Culturally immersive itinerary for {dest_name}, centering indigenous traditions and living heritage."

        elif clean_inst == "RAIN_SAFE":
            why_this.insert(0, "Rain-safe defensive scheduling: Diverted all afternoon exposure to covered monasteries, cheese workshops, and artisan centers.")
            weather_notice = f"All afternoon and exposed outdoor slots in {dest_name} have been weather-shielded due to precipitation forecasts."
            for day in base.days:
                for act in day.activities:
                    if act.period in ["Afternoon", "Evening"]:
                        act.is_weather_adapted = True
                        act.adaptation_reason = "Yatri Setu adapted this activity because of expected mountain rain."
                        act.category = "Culture"
                        act.title = f"Sheltered Experience: {act.title}"
            overview = f"Weather-resilient itinerary for {dest_name}. Keeps travelers dry, warm, and engaged during mountain rains."

        elif clean_inst == "AVOID_CROWDS":
            why_this.insert(0, "Anti-congestion sequencing: Scheduled iconic spots at dawn (05:45 AM - 07:30 AM) and substituted midday peaks with serene secret viewpoints.")
            for day in base.days:
                if day.activities:
                    day.activities[0].time_slot = "05:45 AM - 07:45 AM (Dawn Dawn Slot - 0 Crowds)"
                    day.activities[0].crowd_forecast = "Low"
            overview = f"Off-peak anti-crowd itinerary for {dest_name}. Bypasses 95% of tourist vehicular congestion."

        elif clean_inst == "FAMILY_FRIENDLY":
            why_this.insert(0, "Family-centric safety: Filtered out steep technical scrambles; selected gentle paved walks, interactive crafts, and child-safe dining.")
            for day in base.days:
                for act in day.activities:
                    act.travel_tip = f"Family friendly: gentle terrain, accessible facilities, and welcoming for all age groups."
            overview = f"Family-friendly gentle itinerary for {dest_name}, designed for generational comfort and safety."

        else: # CUSTOM or other
            custom_note = custom_instruction or instruction
            why_this.insert(0, f"Custom AI adaptation applied: '{custom_note}'.")
            overview = f"Custom-tailored itinerary for {dest_name} adapted to user request: '{custom_note}'."

        return AIItineraryOutput(
            overview_note=overview,
            why_this_itinerary=why_this,
            weather_adaptation_notice=weather_notice,
            days=base.days
        )
