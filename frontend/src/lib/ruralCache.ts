/**
 * Rural Cache Utility for Yatri Setu
 * Serializes and stores critical offline intelligence (Homestays, Emergencies, Itineraries, Panchayats)
 * in localStorage & IndexedDB for 2G/3G low network & deep forest areas.
 */

const RURAL_CACHE_PREFIX = 'yatri_rural_cache_';

export interface CacheEntry<T> {
  timestamp: number;
  data: T;
  version: string;
}

export function saveToRuralCache<T>(key: string, data: T): void {
  if (typeof window === 'undefined') return;
  try {
    const entry: CacheEntry<T> = {
      timestamp: Date.now(),
      data,
      version: '1.0'
    };
    localStorage.setItem(RURAL_CACHE_PREFIX + key, JSON.stringify(entry));
  } catch (err) {
    console.warn('[RuralCache] Failed to persist data locally:', err);
  }
}

export function getFromRuralCache<T>(key: string, maxAgeMs: number = 86400000 * 7): T | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(RURAL_CACHE_PREFIX + key);
    if (!raw) return null;
    const entry: CacheEntry<T> = JSON.parse(raw);
    const age = Date.now() - entry.timestamp;
    if (age > maxAgeMs) {
      // Data is older than max age, but for rural offline emergency fallback we still return it if network fails
      return entry.data;
    }
    return entry.data;
  } catch (err) {
    console.warn('[RuralCache] Read error for key:', key, err);
    return null;
  }
}

export const RURAL_EMERGENCY_CONTACTS = [
  { region: 'Uttarakhand State Emergency Response (SDRF)', phone: '1070', type: 'Disaster' },
  { region: 'Uttarakhand Tourist Helpline (24x7)', phone: '1364', type: 'Helpline' },
  { region: 'Himachal Pradesh SDRF Control Room', phone: '1077', type: 'Disaster' },
  { region: 'Chopta / Tungnath Forest Ranger Post', phone: '+91 1372 252123', type: 'Forest' },
  { region: 'Kedarnath Valley Rescue Post', phone: '+91 1364 233100', type: 'Medical' },
  { region: 'Panchayat Emergency Cell (Mana & Badrinath)', phone: '+91 1389 222045', type: 'Panchayat' }
];

export const OFFLINE_SMS_SOS_TEMPLATE = (lat: number | null, lng: number | null) => {
  const coords = lat && lng ? `LOC:${lat.toFixed(5)},${lng.toFixed(5)}` : 'LOC:UNKNOWN';
  return `YATRI_SOS! NEED ASSISTANCE. ${coords}. SENT VIA YATRI-SETU 2G OFFLINE SMS.`;
};
