const CACHE_NAME = "sarkariprep-v4";
const ASSETS_TO_CACHE = [
  "/",
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/img/study_banner.png",
  "/static/img/icon-192.png",
  "/static/img/icon-512.png",
  "/static/manifest.json"
];

// Install Service Worker
self.addEventListener("install", (event) => {
  self.skipWaiting(); // Force the waiting service worker to become active immediately
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// Activate Service Worker
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => {
      return self.clients.claim(); // Take control of all open pages immediately
    })
  );
});

// Fetch Request Interception (Network-First for HTML/API to ensure live updates)
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  const url = new URL(event.request.url);

  // Network-First for navigation or API requests
  if (event.request.mode === "navigate" || url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
    return;
  }

  // Cache-First with Network Fallback for static assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return (
        cachedResponse ||
        fetch(event.request).then((response) => {
          return response;
        })
      );
    })
  );
});

