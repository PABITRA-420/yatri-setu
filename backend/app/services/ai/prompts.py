"""
Prompt Templates and Context Builders for Yatri Setu AI Providers
"""

import json
from typing import Dict, Any, Optional
from app.models.itinerary import ItineraryContext

SYSTEM_PROMPT = """You are Yatri Setu's Adaptive Himalayan Travel Intelligence Engine (Smart India Hackathon 2026).
Your primary mission is sustainable, hyperlocal tourist flow management across the North Bengal & Sikkim Himalayas (Darjeeling, Kalimpong, Lava, Lolegaon, Rishop, Mirik).

CORE RULES:
1. RESPECT CROWD LEVELS: If a destination or attraction has HIGH or VERY HIGH crowd density, schedule it at off-peak hours (early morning) or substitute with serene nearby alternatives.
2. ADAPT TO WEATHER: If rain is expected or mountain visibility is low, you MUST adjust outdoor activities (especially in afternoons) to covered cultural, monastery, or artisan tea/cheese workshops.
   - For any adapted activity, set is_weather_adapted=true and provide an adaptation_reason like: "Yatri Setu adapted this activity because of expected mountain rain."
3. MAXIMIZE LOCAL COMMUNITY BENEFIT: Prioritize authentic homestay meals, local Sherpa/Lepcha/Gorkha community guides, and handicraft cooperatives.
4. TRANSIT REALISM: Mountain travel takes longer due to terrain. Account for shared jeeps and walking trails.
5. STRICT JSON OUTPUT: Return ONLY a valid JSON object matching the requested schema. No markdown backticks, no markdown formatting, no conversational filler.

GROUNDING RULES (MANDATORY — NEVER VIOLATE):
6. NEVER INVENT METRICS: Do NOT fabricate crowd_score, distance_km, ETA, occupancy_rate, temperature, or any other numeric metric.
   Use ONLY the values provided in the DESTINATION CONTEXT section of this prompt.
7. NEVER CLAIM REAL DATA YOU DO NOT HAVE: If a context field is missing or None, say "data not available" rather than guessing.
   Example: if precipitation_chance is not given, do NOT invent a percentage.
8. COST RANGES: Activity cost_estimate_inr must be a realistic amount between 50 and 5000 INR per activity per person.
   Do NOT produce unrealistic values like 0, 50000, or "free" for paid activities.
9. ACTIVITY COUNT: Each day must have between 2 and 5 activities. Never suggest 0 activities for a day.
10. CROWD FORECAST GROUNDING: For crowd_forecast fields, use only: "Low", "Moderate", "High", or "Very High".
    Base these on the crowd_score provided in context, not on invented observations.
"""

def format_itinerary_context_prompt(context: ItineraryContext) -> str:
    user_pref = context.user_preferences
    prompt = f"""
DESTINATION CONTEXT:
- Destination: {context.destination_name} (ID: {context.destination_id})
- Current Crowd Score: {context.crowd_score}/100 ({context.crowd_classification})
- Weather Condition: {context.weather.condition}
- Temperature: {context.weather.temperature_range_c}
- Rain Expected: {'YES' if context.weather.rain_expected else 'NO'} (Precipitation Chance: {context.weather.precipitation_chance_percent}%)
- Mountain Visibility: {context.weather.mountain_visibility_score}/100
- Weather Advisory: {context.weather.advisory}
- Best Hours for Outdoors: {context.weather.best_hours_for_outdoors}

TRAVELER PREFERENCES:
- Duration: {user_pref.get('duration_days', 3)} days
- Traveler Type: {user_pref.get('traveler_type', 'Solo')}
- Pace: {user_pref.get('pace', 'Moderate')}
- Interests: {', '.join(user_pref.get('interests', ['Nature', 'Culture', 'Local Food']))}
- Budget Tier: {user_pref.get('budget_level', 'Moderate')}

AVAILABLE LOCAL ATTRACTIONS:
{json.dumps(context.attractions, indent=2)}

ROUTE SEGMENT ESTIMATES:
{json.dumps([r.model_dump() for r in context.route_estimates], indent=2)}

TASK:
Generate a complete {user_pref.get('duration_days', 3)}-day adaptive itinerary.
Output JSON schema:
{{
  "overview_note": "A 2-3 sentence strategic summary explaining how this itinerary manages crowd exposure and embraces local culture.",
  "why_this_itinerary": [
    "Key rationale 1 (e.g. avoided 4 PM Mall road bottleneck)",
    "Key rationale 2 (e.g. routed to Lepcha handicraft cooperative)",
    "Key rationale 3 (e.g. adjusted afternoon trek to morning window)"
  ],
  "weather_adaptation_notice": "Notice string if weather adjustments were applied, or null",
  "days": [
    {{
      "day_number": 1,
      "theme": "Day Theme Title",
      "overview": "Short narrative for the day",
      "transit_advice": "Shared mountain jeep / walking trail advice",
      "activities": [
        {{
          "time_slot": "08:30 AM - 10:30 AM",
          "period": "Morning",
          "title": "Activity Title",
          "description": "Engaging description",
          "location_name": "Location Name",
          "crowd_forecast": "Low",
          "cost_estimate_inr": 250,
          "duration_hrs": 2.0,
          "travel_tip": "Insider tip for visitors",
          "category": "Culture",
          "is_weather_adapted": false,
          "adaptation_reason": null
        }}
      ]
    }}
  ]
}}
"""
    return prompt

def format_optimization_prompt(
    context: ItineraryContext,
    current_itinerary: Dict[str, Any],
    instruction: str,
    custom_instruction: Optional[str] = None
) -> str:
    prompt = f"""
OPTIMIZATION DIRECTIVE:
Instruction: {instruction}
Additional User Notes: {custom_instruction or 'None'}

CURRENT ITINERARY TO MODIFY:
{json.dumps(current_itinerary, indent=2, default=str)}

DESTINATION CURRENT ENVIRONMENT:
- Destination: {context.destination_name}
- Crowd Score: {context.crowd_score}/100 ({context.crowd_classification})
- Weather: {context.weather.condition}, Rain Expected: {context.weather.rain_expected}, Visibility: {context.weather.mountain_visibility_score}/100
- Advisory: {context.weather.advisory}

INSTRUCTION GUIDELINES:
- If 'MAKE_CHEAPER': Swap commercial activities for free nature trails, community viewpoints, and budget village eateries. Reduce costs by 25-40%.
- If 'MORE_RELAXED': Reduce activity count per day to 2 or 3, extend duration, prioritize calm tea tasting, verandah views, and leisurely walks.
- If 'MORE_NATURE': Replace town walks or shops with pine forest trails, orchid nurseries, canopy walks, and scenic viewpoints.
- If 'MORE_CULTURE': Incorporate heritage monasteries, Tibetan paper-making, Lepcha museum visits, and traditional culinary workshops.
- If 'RAIN_SAFE': Shift afternoon activities indoors (monasteries, cheese factories, covered market pavilions) and set is_weather_adapted=true.
- If 'FAMILY_FRIENDLY': Ensure safe gentle trails, interactive cultural experiences, minimal steep climbs, and accessible dining.
- If 'AVOID_CROWDS': Re-sequence popular spots to 6:00 AM - 8:30 AM or replace them with hidden gems.

Return the modified itinerary in the exact same JSON schema as before.
"""
    return prompt
