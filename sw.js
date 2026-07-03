// sw.js
const CACHE_NAME = 'mytravelmap-cache-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/map2',
  '/book1',
  '/book2',
  '/add',
  '/static/css/style.css',
  '/static/map.html',
  '/static/map2.html',
  '/manifest.json',
  '/static/icons/icon_144x144.png',
  '/static/icons/icon_192x192.png',
  '/static/icons/icon_512x512.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(name) {
          return name !== CACHE_NAME;
        }).map(function(name) {
          return caches.delete(name);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(event) {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Network first for HTML routes, cache fallback
  if (event.request.mode === 'navigate' || url.pathname === '/' || url.pathname === '/map2' || url.pathname === '/book1' || url.pathname === '/book2' || url.pathname === '/add') {
    event.respondWith(
      fetch(event.request)
        .then(function(response) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, copy);
          });
          return response;
        })
        .catch(function() {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache first for static assets (fonts, images, map tiles, styles)
  event.respondWith(
    caches.match(event.request).then(function(cachedResponse) {
      if (cachedResponse) {
        // Fetch in background to update cache (stale-while-revalidate)
        fetch(event.request).then(function(networkResponse) {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, networkResponse);
            });
          }
        });
        return cachedResponse;
      }

      return fetch(event.request).then(function(networkResponse) {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic' && !url.host.includes('tile.openstreetmap.org')) {
          return networkResponse;
        }
        const copy = networkResponse.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, copy);
        });
        return networkResponse;
      });
    })
  );
});