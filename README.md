# NEWS — Poster Studio

A responsive, installable news-poster maker for mobile and desktop.

## Features
- Six poster layouts: Breaking, Classic, Minimal, Sports, Business and Alert.
- Live headline, description, category, publication name and footer editing.
- Upload a photo and choose background or lower-image placement.
- Accent/background colors, headline sizing and alignment.
- Export high-resolution 1080 × 1350 PNG files.
- Share poster on supported mobile browsers.
- PWA manifest and service worker for home-screen installation and offline app shell.

## Run locally
No build step or dependencies are required. Serve this directory with any static web server, for example:

```bash
python3 -m http.server 8080
```

Open http://localhost:8080.

## Deploy
Enable GitHub Pages for the `main` branch, root folder. The app is static and can also be hosted on any HTTPS static host.

## Android
On Android Chrome, open the deployed HTTPS URL and choose **Install app** / **Add to Home screen**. This is the installable PWA version; a signed native APK/AAB and native Android project are not included yet.

## License
Project starter code: MIT. Third-party fonts/assets are not bundled.
