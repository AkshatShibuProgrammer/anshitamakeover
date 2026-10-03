const CACHE_NAME = 'anshita-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/offline/',
  '/gallery/',
  '/manifest.json',
  '/static/core/css/animations.css',
  '/static/core/js/characters/CuteBunnyCharacter.js',
  '/static/core/images/icons/icon-192.png',
  '/static/core/images/icons/icon-512.png',
  '/static/core/images/og-cover.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('SW: Pre-cache asset warning:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Non-GET requests (e.g. POST to chat API) go straight to network
  if (request.method !== 'GET') {
    return;
  }

  // Static assets: Cache-First with Network fallback
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML pages: Network-First with Cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => {
        return caches.match(request).then((cached) => {
          if (cached) return cached;
          return caches.match('/offline/').then((offline) => {
            return offline || caches.match('/');
          });
        });
      })
  );
});
