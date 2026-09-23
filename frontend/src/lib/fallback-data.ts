/**
 * Fallback seed data for rock-solid offline or rapid demo reliability.
 *
 * These constants are used by the API client when the live backend is
 * unreachable, ensuring the frontend always renders meaningful content.
 *
 * Extracted from api.ts per P0 audit recommendation to keep API logic
 * and inline data separate.
 */

import { Destination, Homestay } from '@/types';

export const FALLBACK_DESTINATIONS: Destination[] = [
  {
    id: 'darjeeling',
    name: 'Darjeeling',
    tagline: 'Queen of the Hills, colonial tea plantations & heritage toy train',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'Darjeeling sits majestically at 6,700 ft with views of Kangchenjunga. While historically iconic, during high season it suffers severe vehicular congestion on narrow Hill Cart road, over-commercialized Mall Road crowding, and strain on mountain municipal resources.',
    coordinates: { lat: 27.0360, lng: 88.2627 },
    hero_image: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [
      'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80'
    ],
    attributes: {
      nature: 7.5,
      climate: 'Sub-tropical Highland',
      activities: ['Toy Train Ride', 'Tea Tasting', 'Mall Road Walk', 'Tiger Hill Sunrise', 'Monasteries'],
      culture: 'Colonial Anglo-Indian & Gorkha Heritage',
      budget_level: 'Premium',
      avg_cost_per_day_inr: 4800,
      accessibility: 'National Highway 110 (Frequent Traffic Jams)',
      altitude_ft: 6700
    },
    highlights: [
      'UNESCO World Heritage Darjeeling Himalayan Railway',
      "Iconic view of Mount Kangchenjunga (world's 3rd highest peak)",
      "Centuries-old tea gardens producing the 'Champagne of Teas'",
      'Ghoom Monastery with 15ft Maitreya Buddha statue'
    ],
    attractions: [
      {
        id: 'tiger-hill',
        name: 'Tiger Hill',
        category: 'Scenic Viewpoint',
        description: 'Famous sunrise viewpoint over Mt. Kanchenjunga. Extremely crowded at 4:00 AM.',
        crowd_density: 'High',
        visit_duration_hrs: 2.5,
        best_time: '04:00 AM - 06:30 AM',
        image_url: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=600&q=80'
      },
      {
        id: 'darjeeling-mall',
        name: 'Chowrasta Mall Road',
        category: 'Urban Promenade',
        description: 'Pedestrian promenade lined with heritage cafes and shops.',
        crowd_density: 'High',
        visit_duration_hrs: 2.0,
        best_time: '04:00 PM - 08:00 PM',
        image_url: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80'
      }
    ],
    base_crowd_score: 88,
    recommended_duration_days: 3,
    tags: ['Colonial', 'Tea Gardens', 'Heritage Train', 'High Demand']
  },
  {
    id: 'kalimpong',
    name: 'Kalimpong',
    tagline: 'Tranquil orchid ridge, vibrant monasteries & panoramic valley serenity',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'Perched on a ridge overlooking the Teesta River at 4,100 ft, Kalimpong offers a peaceful cultural retreat. Famous for rare exotic orchids, British-era schools, centuries-old Buddhist gompas, and welcoming Lepcha and Gorkha homestays with zero vehicular traffic bottlenecks.',
    coordinates: { lat: 27.0667, lng: 88.4667 },
    hero_image: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [
      'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80'
    ],
    attributes: {
      nature: 8.8,
      climate: 'Mild Temperate & Pleasant',
      activities: ['Orchid Nursery Tours', 'Monastery Meditation', 'Deolo Hill Paragliding', 'Artisan Cheese Tasting', 'Heritage Walk'],
      culture: 'Lepcha, Bhutia & Nepali Artisan Traditions',
      budget_level: 'Moderate',
      avg_cost_per_day_inr: 2800,
      accessibility: 'State Highway via Teesta Bazaar (Smooth & scenic)',
      altitude_ft: 4100
    },
    highlights: [
      "Produces 80% of India's commercial gladioli and rare orchids",
      'Deolo Hill with 360-degree vistas of Teesta valley and snowy peaks',
      'Zang Dhok Palri Phodang monastery consecrated by the Dalai Lama',
      'Famous local Kalimpong artisan cheese and homemade spiced lollipop candies'
    ],
    attractions: [
      {
        id: 'deolo-hill',
        name: 'Deolo Hill & Park',
        category: 'Scenic Viewpoint & Adventure',
        description: 'Highest point in Kalimpong offering paragliding, landscaped gardens, and Teesta river views.',
        crowd_density: 'Low',
        visit_duration_hrs: 2.5,
        best_time: '08:30 AM - 11:30 AM',
        image_url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80'
      },
      {
        id: 'durpin-monastery',
        name: 'Durpin Monastery (Zang Dhok Palri)',
        category: 'Spiritual & Heritage',
        description: 'Historic monastery preserving rare Tibetan Buddhist scriptures and vibrant mural art.',
        crowd_density: 'Low',
        visit_duration_hrs: 1.5,
        best_time: '02:00 PM - 04:30 PM',
        image_url: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=600&q=80'
      },
      {
        id: 'pine-view-nursery',
        name: 'Pine View Cactus & Orchid Nursery',
        category: 'Botanical Wonder',
        description: "One of Asia's premier collections featuring over 1,500 varieties of cacti and subtropical orchids.",
        crowd_density: 'Low',
        visit_duration_hrs: 1.5,
        best_time: '10:00 AM - 01:00 PM',
        image_url: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=600&q=80'
      }
    ],
    base_crowd_score: 42,
    recommended_duration_days: 3,
    tags: ['Orchids', 'Peaceful', 'Monasteries', 'Artisan Food', 'Eco Friendly']
  },
  {
    id: 'lava',
    name: 'Lava',
    tagline: 'Misty pine woodlands & pristine gateway to Neora Valley',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'A quaint hamlet enveloped in mist and towering pine trees at 7,011 ft. Lava is the primary gateway to Neora Valley National Park.',
    coordinates: { lat: 27.0872, lng: 88.6617 },
    hero_image: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [
      'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80'
    ],
    attributes: {
      nature: 9.5,
      climate: 'Alpine & Misty Cool',
      activities: ['Birdwatching', 'Pine Forest Treks', 'Neora Valley Safari', 'Monastery Visits'],
      culture: 'Forest Communities & Buddhist Culture',
      budget_level: 'Budget',
      avg_cost_per_day_inr: 2100,
      accessibility: 'Scenic Forest Road (32 km from Kalimpong)',
      altitude_ft: 7011
    },
    highlights: [
      'Zero commercial mall congestion — pure forest air and quiet pine trails',
      'Kagyupa Monastery of Lava with meditative prayer bells echoing in the mist'
    ],
    attractions: [],
    base_crowd_score: 24,
    recommended_duration_days: 2,
    tags: ['Pine Forest', 'Birding', 'Misty', 'Secluded']
  },
  {
    id: 'lolegaon',
    name: 'Lolegaon',
    tagline: 'Heritage canopy walkway & silent oak woods',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'Lolegaon is a tiny Lepcha mountain hamlet at 5,500 ft with suspended canopy walkway among ancient trees.',
    coordinates: { lat: 27.0200, lng: 88.5600 },
    hero_image: 'https://images.unsplash.com/photo-1511497584788-87676104235f?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [],
    attributes: {
      nature: 9.2,
      climate: 'Temperate & Serene',
      activities: ['Canopy Tree Walk', 'Jhandi Dara Sunrise', 'Forest Stargazing'],
      culture: 'Lepcha Indigenous Heritage',
      budget_level: 'Budget',
      avg_cost_per_day_inr: 1900,
      accessibility: 'Mountain Rural Road (24 km from Lava)',
      altitude_ft: 5500
    },
    highlights: ['Suspended 180m timber Canopy Walk amidst centenary heritage trees'],
    attractions: [],
    base_crowd_score: 18,
    recommended_duration_days: 2,
    tags: ['Canopy Walk', 'Heritage Forest', 'Silent']
  },
  {
    id: 'rishop',
    name: 'Rishop',
    tagline: 'Panoramic 360-degree Kanchenjunga sunrise haven',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'A vehicle-free mountain settlement at 8,500 ft where every homestay balcony opens directly to Mount Kanchenjunga.',
    coordinates: { lat: 27.1080, lng: 88.6480 },
    hero_image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [],
    attributes: {
      nature: 9.8,
      climate: 'Alpine Cold & Crystal Clear',
      activities: ['Tiffin Dara Peak Trek', 'Milky Way Stargazing', 'Fireside Storytelling'],
      culture: 'Sherpa & Gorkha Mountain Culture',
      budget_level: 'Budget',
      avg_cost_per_day_inr: 2200,
      accessibility: 'Jeep track / scenic 4 km forest hike from Lava',
      altitude_ft: 8500
    },
    highlights: ['Unrivaled 360-degree snow-capped Kanchenjunga panorama without Tiger Hill crowds'],
    attractions: [],
    base_crowd_score: 15,
    recommended_duration_days: 2,
    tags: ['Himalayan Panorama', 'Stargazing', 'No Traffic']
  },
  {
    id: 'mirik',
    name: 'Mirik',
    tagline: 'Tranquil mountain lake, cardamom groves & floating reflections',
    region: 'Eastern Himalayas',
    state: 'West Bengal',
    description: 'Centered around the serene Sumendu Lake, connected by the footbridge Indreni Pul.',
    coordinates: { lat: 26.8887, lng: 88.1764 },
    hero_image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80',
    gallery_images: [],
    attributes: {
      nature: 8.4,
      climate: 'Temperate & Refreshing',
      activities: ['Boating on Sumendu Lake', 'Orange Orchard Walks'],
      culture: 'Gorkha & Lepcha Lakeside Community',
      budget_level: 'Moderate',
      avg_cost_per_day_inr: 2900,
      accessibility: 'State Highway 12',
      altitude_ft: 4905
    },
    highlights: ['Sumendu Lake with floating lotus and arching footbridge'],
    attractions: [],
    base_crowd_score: 38,
    recommended_duration_days: 2,
    tags: ['Lakeside', 'Tea Gardens', 'Boating']
  }
];

export const FALLBACK_HOMESTAYS: Homestay[] = [
  {
    id: 'hs-kalimpong-01',
    destination_id: 'kalimpong',
    destination_name: 'Kalimpong',
    title: 'Pineview Orchid Retreat & Homestay',
    tagline: 'Family-run heritage cottage overlooking Kanchenjunga and organic orchids',
    address: 'Atisha Road, Upper Cart Road, Kalimpong - 734301',
    price_per_night_inr: 2400,
    rating: 4.9,
    reviews_count: 84,
    room_type: 'Entire Wooden Suite with Valley Balcony',
    max_guests: 3,
    amenities: ['High-Speed Wi-Fi', 'Home-Cooked Organic Meals', 'Hot Water Geyser', 'Orchid Greenhouse Access', 'Bonfire Area'],
    images: [
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80',
      'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'
    ],
    host: {
      name: 'Pemba & Choden Sherpa',
      avatar_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80',
      experience_years: 7,
      languages: ['English', 'Hindi', 'Nepali', 'Bengali'],
      about: 'Our family has cultivated rare Himalayan orchids for three generations. We welcome travelers with authentic home-cooked meals, homemade ginger-rhododendron tea, and warm fireside stories.',
      verified_panchayat: true,
      response_rate: '100% within 15 minutes'
    },
    community_fund_contribution_percent: 10,
    special_activity: 'Orchid potting workshop & traditional Lepcha cooking session',
    verified: true
  },
  {
    id: 'hs-kalimpong-02',
    destination_id: 'kalimpong',
    destination_name: 'Kalimpong',
    title: 'Deolo Vista Farmstay',
    tagline: 'Quiet farm sanctuary with fresh dairy, mountain honey and Teesta valley views',
    address: 'Deolo Hills, Near Water Reservoir, Kalimpong - 734316',
    price_per_night_inr: 2200,
    rating: 4.8,
    reviews_count: 62,
    room_type: 'Deluxe Mountain View Room',
    max_guests: 2,
    amenities: ['Farm-to-Table Breakfast Included', 'Wi-Fi', 'Solar Heating', 'Trekking Guide on Demand'],
    images: [
      'https://images.unsplash.com/photo-1587061949409-02df41d5e562?auto=format&fit=crop&w=800&q=80'
    ],
    host: {
      name: 'Bikram Pradhan',
      avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80',
      experience_years: 5,
      languages: ['English', 'Hindi', 'Nepali'],
      about: 'Certified rural eco-tourism host. We believe in regenerative travel that directly supports local schools.',
      verified_panchayat: true,
      response_rate: 'Under 1 hour'
    },
    community_fund_contribution_percent: 12,
    special_activity: 'Beekeeping tour and evening folk flute performance',
    verified: true
  },
  {
    id: 'hs-lava-01',
    destination_id: 'lava',
    destination_name: 'Lava',
    title: 'Neora Pine Mist Homestay',
    tagline: 'Cozy pine log cabin touching the boundary of Neora Valley National Park',
    address: 'Monastery Road, Lava Bazaar, Kalimpong District - 734319',
    price_per_night_inr: 1850,
    rating: 4.9,
    reviews_count: 51,
    room_type: 'Pine Wood Attic Room',
    max_guests: 3,
    amenities: ['Organic Farm Dining', 'Wood Fireplace', 'Binoculars for Birding', 'Nature Guide'],
    images: [
      'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80'
    ],
    host: {
      name: 'Dawa Tshering Lepcha',
      avatar_url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80',
      experience_years: 9,
      languages: ['English', 'Hindi', 'Lepcha', 'Nepali'],
      about: 'Passionate bird watcher and certified Himalayan nature guide.',
      verified_panchayat: true,
      response_rate: '100%'
    },
    community_fund_contribution_percent: 15,
    special_activity: 'Early morning birding walk to spot Rufous-necked Hornbills',
    verified: true
  },
  {
    id: 'hs-rishop-01',
    destination_id: 'rishop',
    destination_name: 'Rishop',
    title: 'Cloud 9 Kanchenjunga Lodge',
    tagline: 'Wake up to unobstructed 180° sunrise on snow-clad peaks',
    address: 'Tiffin Dara Trail, Rishop, Kalimpong District - 734319',
    price_per_night_inr: 1950,
    rating: 4.9,
    reviews_count: 48,
    room_type: 'Panoramic View Cottage',
    max_guests: 4,
    amenities: ['Rooftop Viewing Deck', 'Electric Blankets', 'Authentic Gorkha Thali', 'Stargazing Telescope'],
    images: [
      'https://images.unsplash.com/photo-1510798831971-661eb04b3739?auto=format&fit=crop&w=800&q=80'
    ],
    host: {
      name: 'Sonam Gurung',
      avatar_url: 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=200&q=80',
      experience_years: 6,
      languages: ['English', 'Hindi', 'Nepali'],
      about: 'Passionate about sustainable off-grid living and eco-tourism.',
      verified_panchayat: true,
      response_rate: 'Instant'
    },
    community_fund_contribution_percent: 10,
    special_activity: 'Guided sunrise hike to Tiffin Dara ridge',
    verified: true
  }
];
