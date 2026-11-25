# NEWS Studio — Firebase final setup

Firebase project: `ghost-b9156`  
Android application ID: `com.luckyfoundertech.news`  
Firebase Android App ID: `1:519573612826:android:8568296d317fa86bcfa4a3`

## Android debug SHA-1

Add this SHA-1 under Firebase Console → Project settings → Your apps → Android app → SHA certificate fingerprints:

```
C8:F6:57:C2:ED:17:4F:E4:CA:63:1C:1A:B3:4D:CB:D2:BE:91:17:18
```

Then download the refreshed `google-services.json` and replace the repository root file. The currently committed JSON has an empty `oauth_client` list, so native Google Sign-In is not ready until Firebase generates the OAuth client and the refreshed file is committed. This is the GitHub Actions debug signing fingerprint; a Play Store release keystore will have a different fingerprint.

## Enable Google provider

Firebase Console → Authentication → Sign-in method → Google → Enable → Save.

## Publish database rules

Copy the repository `firestore.rules` contents into Firebase Console → Firestore Database → Rules, then Publish.

Copy the repository `storage.rules` contents into Firebase Console → Storage → Rules, then Publish. Or, after Firebase CLI login, run `firebase deploy --only firestore:rules,storage` from the repository root (the project and rules config are included).

These rules restrict each user's design documents and uploaded design/media files to the matching authenticated UID.

## What cloud sync stores

- Firestore: per-user design metadata and Storage object paths.
- Firebase Storage: Yjs design state (including embedded image assets), video/audio media blobs.
- Device IndexedDB: local editing cache and thumbnails. Cloud restore rebuilds the design index and thumbnail.

## Important

Do not commit service-account private keys, OAuth client secrets, or Firebase Admin credentials. The browser/mobile Firebase API key in `google-services.json` is an application identifier, not an admin credential.
