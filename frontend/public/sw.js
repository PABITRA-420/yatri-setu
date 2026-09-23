// Yatri Setu Production Service Worker (v2) — Rural 2G/3G & Offline Resilience
const CACHE_NAME = 'yatri-setu-v2-cache';
const OFFLINE_SHELL_URLS = [
  '/',
  '/destinations',
  '/homestays',
  '/itinerary',
  '/safety/sos',
  '/panchayat'
];

// Domains permitted for image & static asset caching
const CACHEABLE_ORIGINS = [
  'images.unsplash.com',
  'fonts.googleapis.com',
  'fonts.gstatic.com'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_SHELL_URLS).catch((err) => {
        console.warn('[SW] Non-critical cache error on install:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[SW] Purging legacy cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // 1. Bypass non-http protocols (e.g. chrome-extension:)
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // 2. Bypass Next.js HMR, hot reload & dev-server endpoints
  if (url.pathname.includes('/_next/webpack-hmr') || url.pathname.includes('__nextjs')) {
    return;
  }

  // 3. Bypass Next.js dynamic React Server Component (_rsc) navigation chunks to prevent stale routing
  if (url.searchParams.has('_rsc')) {
    return;
  }

  // 4. Image & Media Asset Caching Strategy (Cache-First with Network Fallback)
  const isImageOrMedia =
    event.request.destination === 'image' ||
    CACHEABLE_ORIGINS.some((origin) => url.hostname.includes(origin)) ||
    url.pathname.match(/\.(png|jpg|jpeg|svg|webp|ico|woff2?)$/i);

  if (isImageOrMedia) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request)
          .then((networkResponse) => {
            if (networkResponse && (networkResponse.status === 200 || networkResponse.type === 'opaque')) {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, responseToCache);
              });
            }
            return networkResponse;
          })
          .catch(() => {
            // Return empty SVG placeholder when completely offline and image not cached
            return new Response(
              '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"><rect width="100%" height="100%" fill="#1c1917"/><text x="50%" y="50%" fill="#a8a29e" font-family="sans-serif" font-size="14" text-anchor="middle" dy=".3em">Offline Image Cached Locally</text></svg>',
              { headers: { 'Content-Type': 'image/svg+xml' } }
            );
          });
      })
    );
    return;
  }

  // 5. HTML Navigation Requests (Network-First with App Shell Fallback)
  if (event.request.mode === 'navigate' || event.request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;
            return caches.match('/');
          });
        })
    );
    return;
  }

  // 6. API Requests (Network-First with Graceful Offline JSON Fallback)
  if (url.pathname.startsWith('/api') || url.hostname.includes('onrender.com')) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          return caches.match(event.request).then((cachedResponse) => {
            if (cachedResponse) return cachedResponse;
            // Return structured 503 fallback JSON response instead of undefined
            return new Response(
              JSON.stringify({
                offline: true,
                status: 'OFFLINE_FALLBACK',
                message: 'Operating in 2G/offline fallback mode. Serving local cache.'
              }),
              {
                status: 503,
                statusText: 'Service Unavailable (Offline)',
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }

  // 7. General Static Assets (Stale-While-Revalidate)
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});
