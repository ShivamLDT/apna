
// /**04/12/24 */
// const CACHE_NAME = 'Service_Worker';

// const urlsToCache = [
//   '/',  // Root page (index.html)
//   '/index.html',  // Main HTML file
//   '/manifest',  // Manifest file
//   '/asset-manifest',  // Asset manifest file
//   '/json.data',  // Example data file
//   '/offline.html',  // Offline fallback page
//   // JavaScript files (adjust with actual filenames from build)
//   '/static/js/787.c7b71262.chunk.js',  // JavaScript chunk file
//   '/static/js/main.efac63d2.js',  // Main JavaScript bundle
//   '/static/js/main.efac63d2.js.LICENSE',  // License file (optional, usually not cached)
  
//   // CSS files
//   '/static/css/main.67bfea40.css',  // Main CSS file
  
//   // Media assets (adjust for your actual media files)
//   '/static/media/logo.svg',  // Example logo, replace with actual media if available
//   '/static/media/background.jpg',  // Example image, replace with actual media if available
  
//   // You can add more media files here if needed (e.g., fonts, images, etc.)
// ];

// self.addEventListener('install', async (event) => {
//   // console.log('Service Worker installing...');
//   self.skipWaiting(); // Force the waiting service worker to become active
  
//   try {
//     const cache = await caches.open(CACHE_NAME);
//     // console.log('Opened cache:', CACHE_NAME);
//     await cache.addAll(urlsToCache);  // Cache all specified files
//     // console.log('Files cached:', urlsToCache);
//   } catch (error) {
//     console.error('Error adding files to cache:', error);
//   }

//   // Wait for cache operation to complete
//   event.waitUntil(
//     caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
//   );
// });

// // Fetch event: Serve files from cache or fetch from network if not cached
// // self.addEventListener('fetch', (event) => {
// //   event.respondWith(
// //     (async () => {
// //       // Cache all request methods (GET, POST, PUT, DELETE, etc.)
// //       const cachedResponse = await caches.match(event.request);

// //       // If the file is found in cache, return it
// //       if (cachedResponse) {
// //         return cachedResponse;
// //       }

// //       try {
// //         // Otherwise, fetch the request from the network
// //         const networkResponse = await fetch(event.request);
// //         const networkResponseClone = networkResponse.clone();

// //         // Cache the network response for future use
// //         caches.open(CACHE_NAME).then((cache) => {
// //           cache.put(event.request, networkResponseClone);
// //         });

// //         // Return the network response to the browser
// //         return networkResponse;
// //       } catch (error) {
// //         // In case of network failure, return the offline page if available
// //         return caches.match('/offline.html');  // Ensure offline page is cached
// //       }
// //     })()
// //   );
// // });


// self.addEventListener('fetch', (event) => {
//   event.respondWith(
//     (async () => {
//       // Try to fetch from the cache first
//       const cachedResponse = await caches.match(event.request);

//       // If the request is found in the cache, return it
//       if (cachedResponse) {
//         // console.log('Serving from cache:', event.request.url);
//         return cachedResponse;
//       }

//       // If the request is not found in the cache, try to fetch from the network
//       try {
//         const networkResponse = await fetch(event.request);

//         // Cache the network response for future use
//         const networkResponseClone = networkResponse.clone();

//         // Cache only non-HTML content (to avoid caching dynamic pages like React routes)
//         if (!event.request.url.includes('.html')) {
//           const cache = await caches.open(CACHE_NAME);
//           cache.put(event.request, networkResponseClone);
//         }

//         // console.log('Serving from network:', event.request.url);
//         return networkResponse;

//       } catch (error) {
//         // If offline and network fails, serve the offline page (ensure it's cached)
//         // console.log('Network request failed, serving offline page');
//         return caches.match('/offline.html');
//       }
//     })()
//   );
// });



// // Activate event: Clean up old caches if service worker is updated
// self.addEventListener('activate', (event) => {
//   const cacheWhitelist = [CACHE_NAME]; // Make sure only the current cache is retained
//   event.waitUntil(
//     caches.keys().then((cacheNames) => {
//       return Promise.all(
//         cacheNames.map((cacheName) => {
//           if (!cacheWhitelist.includes(cacheName)) {
//             return caches.delete(cacheName);  // Clean up old caches
//           }
//         })
//       );
//     })
//   );
// });
