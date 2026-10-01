
const CACHE_NAME = 'bulkmate-v2';

// Install event
self.addEventListener('install', (event) => {
  console.log('BulkMate SW: Installed');
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  console.log('BulkMate SW: Activated');
  event.waitUntil(clients.claim());
});

// Fetch event — always fetch from network (no offline caching)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // If network fails, show a simple offline message
      return new Response(
        `<!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>BulkMate — No Internet</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                background: #0a0a0a;
                color: #e5e5e5;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                text-align: center;
                padding: 20px;
              }
              h1 { color: #4ade80; font-size: 2rem; margin-bottom: 8px; }
              p  { color: #666; font-size: 0.9rem; }
            </style>
          </head>
          <body>
            <div>
              <div style="font-size:4rem">🥗</div>
              <h1>BulkMate</h1>
              <p>No internet connection.</p>
              <p>Please connect and try again!</p>
            </div>
          </body>
        </html>`,
        { headers: { 'Content-Type': 'text/html' } }
      );
    })
  );
});