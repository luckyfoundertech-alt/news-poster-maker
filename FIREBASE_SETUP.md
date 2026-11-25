# NEWS Studio — Firebase final setup

Firebase project: `ghost-b9156`  
Android application ID: `com.luckyfoundertech.news`  
Firebase Android App ID: `1:519573612826:android:8568296d317fa86bcfa4a3`

## Android debug SHA-1

Add this SHA-1 under Firebase Console → Project settings → Your apps → Android app → SHA certificate fingerprints:

```
1B:0A:A7:8E:1F:84:1A:27:DE:70:80:D6:92:4E:89:07:6C:C3:FA:71
```

Then download the refreshed `google-services.json` and replace the repository root file. This is the GitHub Actions debug signing fingerprint; a Play Store release keystore will have a different fingerprint.

## Enable Google provider

Firebase Console → Authentication → Sign-in method → Google → Enable → Save.

## Publish database rules

Copy the repository `firestore.rules` contents into Firebase Console → Firestore Database → Rules, then Publish.

Copy the repository `storage.rules` contents into Firebase Console → Storage → Rules, then Publish.

These rules restrict each user's design documents and uploaded design/media files to the matching authenticated UID.

## What cloud sync stores

- Firestore: per-user design metadata and Storage object paths.
- Firebase Storage: Yjs design state (including embedded image assets), video/audio media blobs.
- Device IndexedDB: local editing cache and thumbnails. Cloud restore rebuilds the design index and thumbnail.

## Important

Do not commit service-account private keys, OAuth client secrets, or Firebase Admin credentials. The browser/mobile Firebase API key in `google-services.json` is an application identifier, not an admin credential.
