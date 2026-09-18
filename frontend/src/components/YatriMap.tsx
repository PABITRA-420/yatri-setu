'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { RouteGeometry } from '@/types';
import { 
  Compass, 
  MapPin, 
  Maximize2, 
  Navigation, 
  Layers, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  Sparkles,
  Info
} from 'lucide-react';

export interface CircuitDestinationNode {
  id: string;
  name: string;
  coordinates: [number, number]; // [lng, lat]
  altitude_ft?: number;
  crowd_score?: number;
  crowd_level?: string;
  capacity_status?: string;
  access_status?: string;
  weather_summary?: string;
  tagline?: string;
}

// Canonical Eastern Himalayan Circuit Nodes with accurate coordinates
export const CANONICAL_CIRCUIT_NODES: CircuitDestinationNode[] = [
  {
    id: 'darjeeling',
    name: 'Darjeeling',
    coordinates: [88.2663, 27.0410],
    altitude_ft: 6700,
    crowd_score: 88,
    crowd_level: 'VERY HIGH',
    capacity_status: 'CRITICAL',
    access_status: 'OPEN',
    tagline: 'Colonial tea hills & heritage toy train'
  },
  {
    id: 'kalimpong',
    name: 'Kalimpong',
    coordinates: [88.4695, 27.0594],
    altitude_ft: 4100,
    crowd_score: 42,
    crowd_level: 'MODERATE',
    capacity_status: 'HEALTHY',
    access_status: 'OPEN',
    tagline: 'Orchid nurseries & serene monasteries'
  },
  {
    id: 'lava',
    name: 'Lava',
    coordinates: [88.6603, 27.0864],
    altitude_ft: 7011,
    crowd_score: 24,
    crowd_level: 'LOW',
    capacity_status: 'HEALTHY',
    access_status: 'OPEN',
    tagline: 'Misty pine woodlands & Neora gateway'
  },
  {
    id: 'lolegaon',
    name: 'Lolegaon',
    coordinates: [88.5583, 27.0142],
    altitude_ft: 5500,
    crowd_score: 18,
    crowd_level: 'LOW',
    capacity_status: 'HEALTHY',
    access_status: 'OPEN',
    tagline: 'Heritage canopy walkway & silent oak woods'
  },
  {
    id: 'rishop',
    name: 'Rishop',
    coordinates: [88.6496, 27.1065],
    altitude_ft: 8500,
    crowd_score: 15,
    crowd_level: 'LOW',
    capacity_status: 'HEALTHY',
    access_status: 'OPEN',
    tagline: '360° Kanchenjunga sunrise haven'
  },
  {
    id: 'mirik',
    name: 'Mirik',
    coordinates: [88.1755, 26.9011],
    altitude_ft: 4905,
    crowd_score: 38,
    crowd_level: 'MODERATE',
    capacity_status: 'HEALTHY',
    access_status: 'OPEN',
    tagline: 'Tranquil mountain lake & tea slopes'
  }
];

const OPENFREEMAP_STYLE_URL = 'https://tiles.openfreemap.org/styles/liberty';
const CIRCUIT_CENTER_LNG_LAT: [number, number] = [88.45, 27.04];
const DEFAULT_ZOOM = 10.2;

interface YatriMapProps {
  center?: [number, number]; // [lng, lat]
  zoom?: number;
  originId?: string;
  selectedDestinationId?: string;
  nodes?: CircuitDestinationNode[];
  routeGeometry?: RouteGeometry | [number, number][] | null;
  onSelectDestination?: (destId: string) => void;
  height?: string;
  className?: string;
  showControls?: boolean;
  interactive?: boolean;
  provenanceLabel?: string;
  routeDistanceKm?: number;
  routeDurationMin?: number;
  isRoadDistance?: boolean;
}

export const YatriMap: React.FC<YatriMapProps> = ({
  center = CIRCUIT_CENTER_LNG_LAT,
  zoom = DEFAULT_ZOOM,
  originId,
  selectedDestinationId,
  nodes = CANONICAL_CIRCUIT_NODES,
  routeGeometry,
  onSelectDestination,
  height = '460px',
  className = '',
  showControls = true,
  interactive = true,
  provenanceLabel,
  routeDistanceKm,
  routeDurationMin,
  isRoadDistance = true
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState<string | null>(null);

  // Initialize MapLibre
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapRef.current) return;

    try {
      const map = new maplibregl.Map({
        container: mapContainerRef.current,
        style: OPENFREEMAP_STYLE_URL,
        center: center,
        zoom: zoom,
        interactive: interactive,
        attributionControl: false
      });

      if (showControls) {
        map.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
      }

      map.on('load', () => {
        mapRef.current = map;
        setMapLoaded(true);
      });

      map.on('error', (e: any) => {
        console.warn('MapLibre encounter warning or style reload:', e);
      });

      return () => {
        markersRef.current.forEach((m) => m.remove());
        markersRef.current = [];
        map.remove();
        mapRef.current = null;
      };
    } catch (err) {
      console.error('Failed to initialize MapLibre GL:', err);
      setMapError('Interactive WebGL map failed to initialize in this browser environment.');
    }
  }, []);

  // Update Markers & Popups
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    // Clear previous markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    nodes.forEach((node) => {
      const isOrigin = originId && node.id.toLowerCase() === originId.toLowerCase();
      const isSelected = selectedDestinationId && node.id.toLowerCase() === selectedDestinationId.toLowerCase();

      // Custom DOM Element for marker
      const el = document.createElement('div');
      el.className = 'yatri-map-marker-container cursor-pointer group transition-transform duration-200';

      // Pin styling based on role
      let pinColor = '#3b82f6'; // default blue
      let badgeLabel = '';
      let ringClass = '';

      if (isOrigin) {
        pinColor = '#f59e0b'; // Amber luxury origin
        badgeLabel = 'ORIGIN';
        ringClass = 'ring-4 ring-amber-400/50 animate-pulse';
      } else if (isSelected) {
        pinColor = '#10b981'; // Emerald selected alternative
        badgeLabel = 'SELECTED';
        ringClass = 'ring-4 ring-emerald-400/60 shadow-lg shadow-emerald-500/30';
      } else if ((node.crowd_score || 0) > 75) {
        pinColor = '#ef4444'; // Rose high crowd
      } else if ((node.crowd_score || 0) < 35) {
        pinColor = '#10b981'; // Emerald calm
      } else {
        pinColor = '#0284c7'; // Cyan moderate
      }

      el.innerHTML = `
        <div class="relative flex flex-col items-center">
          ${badgeLabel ? `
            <span class="mb-1 text-[9px] font-black tracking-widest px-1.5 py-0.5 rounded-md text-white shadow-md ${
              isOrigin ? 'bg-amber-600' : 'bg-emerald-600'
            }">
              ${badgeLabel}
            </span>
          ` : ''}
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-xs shadow-xl transition-all group-hover:scale-115 ${ringClass}"
               style="background: ${pinColor}; border: 2.5px solid white;">
            <span>${node.name.slice(0, 1)}</span>
          </div>
          <div class="mt-1 bg-stone-900/90 dark:bg-stone-950/95 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-md whitespace-nowrap border border-white/20 backdrop-blur-sm pointer-events-none">
            ${node.name} <span class="text-amber-300 font-mono ml-0.5">${node.crowd_score ?? ''}</span>
          </div>
        </div>
      `;

      // Popup Content
      const popupHTML = `
        <div class="p-3 text-stone-900 dark:text-stone-100 font-sans max-w-[240px] space-y-2">
          <div class="flex items-center justify-between border-b border-stone-200 dark:border-stone-700 pb-1.5">
            <h4 class="font-extrabold text-sm text-stone-950 dark:text-white">${node.name}</h4>
            <span class="text-[9px] font-bold uppercase px-1.5 py-0.5 rounded bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300">
              ${node.altitude_ft ? `${node.altitude_ft.toLocaleString()} ft` : 'Himalayas'}
            </span>
          </div>
          <p class="text-[11px] text-stone-600 dark:text-stone-300 line-clamp-2">
            ${node.tagline || 'Eastern Himalayan circuit destination'}
          </p>
          <div class="grid grid-cols-2 gap-1.5 text-[10px] pt-1">
            <div class="bg-stone-50 dark:bg-stone-800/60 p-1.5 rounded-md">
              <span class="text-stone-400 block text-[9px] uppercase font-bold">Crowd</span>
              <span class="font-bold text-stone-800 dark:text-stone-200">${node.crowd_score ?? 40}/100</span>
            </div>
            <div class="bg-stone-50 dark:bg-stone-800/60 p-1.5 rounded-md">
              <span class="text-stone-400 block text-[9px] uppercase font-bold">Capacity</span>
              <span class="font-bold text-emerald-600 dark:text-emerald-400">${node.capacity_status || 'HEALTHY'}</span>
            </div>
          </div>
          <div class="pt-1 flex items-center justify-between text-[9px] text-stone-500">
            <span>Access: <strong>${node.access_status || 'OPEN'}</strong></span>
            <span class="text-amber-600 dark:text-amber-400 font-semibold cursor-pointer select-action-link">Select &rarr;</span>
          </div>
        </div>
      `;

      const popup = new maplibregl.Popup({ offset: 25, closeButton: false }).setHTML(popupHTML);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(node.coordinates)
        .setPopup(popup)
        .addTo(map);

      // On marker click: notify parent
      el.addEventListener('click', () => {
        if (onSelectDestination) {
          onSelectDestination(node.id);
        }
      });

      markersRef.current.push(marker);
    });
  }, [nodes, originId, selectedDestinationId, mapLoaded, onSelectDestination]);

  // Update Route Geometry Layer
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapLoaded) return;

    const sourceId = 'yatri-route-source';
    const layerId = 'yatri-route-layer';
    const casingLayerId = 'yatri-route-casing-layer';

    // Remove existing layer/source if present
    if (map.getLayer(layerId)) map.removeLayer(layerId);
    if (map.getLayer(casingLayerId)) map.removeLayer(casingLayerId);
    if (map.getSource(sourceId)) map.removeSource(sourceId);

    if (!routeGeometry) return;

    let coordinates: [number, number][] = [];
    if (Array.isArray(routeGeometry)) {
      coordinates = routeGeometry;
    } else if (routeGeometry.coordinates && Array.isArray(routeGeometry.coordinates)) {
      coordinates = routeGeometry.coordinates as [number, number][];
    }

    if (coordinates.length < 2) return;

    // Add GeoJSON source
    map.addSource(sourceId, {
      type: 'geojson',
      data: {
        type: 'Feature',
        properties: {},
        geometry: {
          type: 'LineString',
          coordinates: coordinates
        }
      }
    });

    // Add outer glow casing
    map.addLayer({
      id: casingLayerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#f59e0b',
        'line-width': 8,
        'line-opacity': 0.35,
        'line-blur': 3
      }
    });

    // Add crisp inner road line (amber for road, dashed cyan for haversine)
    map.addLayer({
      id: layerId,
      type: 'line',
      source: sourceId,
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': isRoadDistance ? '#f59e0b' : '#38bdf8',
        'line-width': isRoadDistance ? 4 : 3,
        'line-opacity': 0.95,
        'line-dasharray': isRoadDistance ? [1, 0] : [2, 2]
      }
    });

    // Fit map bounds to frame both points smoothly
    try {
      const bounds = coordinates.reduce(
        (b, coord) => b.extend(coord as [number, number]),
        new maplibregl.LngLatBounds(coordinates[0], coordinates[0])
      );
      map.fitBounds(bounds, {
        padding: { top: 60, bottom: 60, left: 60, right: 60 },
        maxZoom: 12,
        duration: 1200
      });
    } catch (err) {
      console.warn('Could not fit bounds to route:', err);
    }
  }, [routeGeometry, mapLoaded, isRoadDistance]);

  const handleResetCamera = useCallback(() => {
    if (!mapRef.current) return;
    mapRef.current.flyTo({
      center: center,
      zoom: zoom,
      duration: 1000
    });
  }, [center, zoom]);

  return (
    <div className={`relative rounded-3xl overflow-hidden shadow-xl border border-stone-200/90 dark:border-white/10 bg-stone-900 ${className}`}>
      {/* Map Canvas Container */}
      <div 
        ref={mapContainerRef} 
        style={{ height: height }} 
        className="w-full bg-stone-950"
      />

      {/* Fallback Display if WebGL/MapLibre Fails */}
      {mapError && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-stone-900/95 p-6 text-center text-white z-20">
          <AlertTriangle className="w-10 h-10 text-amber-400 mb-3" />
          <h4 className="font-extrabold text-base mb-1">Map Visualization Unavailable</h4>
          <p className="text-xs text-stone-300 max-w-md mb-4">{mapError}</p>
          <div className="bg-stone-800/80 p-3.5 rounded-2xl text-left text-xs space-y-1.5 border border-white/10 max-w-sm w-full">
            <span className="font-bold text-amber-400 block text-[10px] uppercase">Circuit Coordinate Reference</span>
            <div className="grid grid-cols-2 gap-2 text-[11px] text-stone-300">
              <div>Darjeeling: 27.04° N, 88.27° E</div>
              <div>Kalimpong: 27.06° N, 88.47° E</div>
              <div>Lava: 27.09° N, 88.66° E</div>
              <div>Rishop: 27.11° N, 88.65° E</div>
            </div>
          </div>
        </div>
      )}

      {/* Floating Header Banner */}
      <div className="absolute top-3.5 left-3.5 z-10 flex flex-wrap items-center gap-2 pointer-events-none">
        <div className="pointer-events-auto glass-pill px-3 py-1.5 rounded-2xl bg-stone-950/80 dark:bg-stone-900/90 text-white text-xs font-extrabold flex items-center gap-2 border border-white/15 shadow-lg backdrop-blur-md">
          <Compass className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
          <span>Eastern Himalayan Circuit Map</span>
        </div>

        {routeDistanceKm !== undefined && (
          <div className="pointer-events-auto px-3 py-1.5 rounded-2xl bg-stone-950/90 text-white text-xs font-bold flex items-center gap-2 border border-amber-500/40 shadow-lg backdrop-blur-md">
            <Navigation className="w-3.5 h-3.5 text-amber-400" />
            <span>
              {routeDistanceKm} km {isRoadDistance ? 'Road' : 'Approx. Geographic'}
            </span>
            {routeDurationMin !== undefined && isRoadDistance && (
              <span className="text-stone-400">• ~{routeDurationMin} min</span>
            )}
          </div>
        )}
      </div>

      {/* Floating Bottom Metadata & Provenance Bar */}
      <div className="absolute bottom-3.5 left-3.5 right-3.5 z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pointer-events-none">
        {/* Left Provenance Badge */}
        <div className="pointer-events-auto flex items-center gap-2">
          <div className="glass-pill px-2.5 py-1 rounded-xl bg-stone-950/85 text-[10px] font-bold text-stone-300 border border-white/10 shadow-md backdrop-blur-md flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-amber-400" />
            <span>OpenFreeMap Liberty • MapLibre GL JS</span>
          </div>

          {provenanceLabel && (
            <div className="glass-pill px-2.5 py-1 rounded-xl bg-amber-500/20 text-[10px] font-extrabold text-amber-300 border border-amber-500/30 shadow-md backdrop-blur-md flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>{provenanceLabel}</span>
            </div>
          )}
        </div>

        {/* Right Camera Reset Action */}
        <div className="pointer-events-auto flex items-center gap-1.5 self-end sm:self-auto">
          <button
            type="button"
            onClick={handleResetCamera}
            className="px-2.5 py-1 rounded-xl bg-stone-950/85 hover:bg-stone-900 text-stone-300 hover:text-white text-[10px] font-bold border border-white/10 shadow-md backdrop-blur-md transition-all flex items-center gap-1 cursor-pointer"
            title="Reset to Himalayan Circuit View"
          >
            <Maximize2 className="w-3 h-3" />
            <span>Reset View</span>
          </button>
        </div>
      </div>
    </div>
  );
};
