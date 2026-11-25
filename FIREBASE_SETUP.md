# NEWS Studio — Firebase production setup

Firebase project: `ghost-b9156`  
Android application ID: `com.luckyfoundertech.news`  
Firebase Android App ID: `1:519573612826:android:8568296d317fa86bcfa4a3`

## Current GitHub Actions debug SHA-1

Add this exact fingerprint under Firebase Console → Project settings → Your apps → Android app → SHA certificate fingerprints:

```
2D:15:5C:76:48:D0:D3:12:14:C8:71:2F:86:66:3D:E5:3A:E8:AE:92
```

This is the SHA-1 printed by the latest successful Android CI build (25 November 2026). The earlier fingerprint in this document was stale.

After adding the fingerprint:
1. In Firebase Console → Authentication → Sign-in method, enable Google.
2. Download a fresh `google-services.json` for package `com.luckyfoundertech.news`.
3. Replace the repository-root `google-services.json` and commit it.
4. Confirm the refreshed file contains an OAuth client entry for this Android app. The currently committed file has an empty `oauth_client` array, so Google Sign-In cannot be considered configured until the refreshed file is committed.

A Play Store release keystore has a different SHA-1 and SHA-256. Add those release fingerprints to Firebase as well after creating and securely storing the release signing key. Never commit the keystore or its passwords.

## Publish database rules

The repository contains restrictive per-user rules. Publish them to the Firebase project:

- Copy `firestore.rules` into Firebase Console → Firestore Database → Rules, then Publish.
- Copy `storage.rules` into Firebase Console → Storage → Rules, then Publish.

Alternatively, after Firebase CLI login, run:

```bash
firebase deploy --only firestore:rules,storage
```

Do not deploy permissive test-mode rules.

## Cloud-save data model

- Firestore: `users/{uid}/designs/{designId}` metadata and Storage object paths.
- Firebase Storage: Yjs design state, including embedded image/SVG assets, plus video/audio media blobs.
- Device IndexedDB: local editing cache and generated thumbnails.

Each signed-in user can read/write only their own `users/{uid}/designs/**` data under the supplied rules. Cloud sync requires the Firestore and Storage products to be enabled and the rules above to be published.

## Release signing

The CI debug APK is for installation/testing, not a Play Store release. A production release must be signed with a persistent Android upload/release keystore. Store the keystore and passwords in a secure password manager / CI secrets; never put them in Git. Register the release certificate fingerprints in Firebase before enabling production Google Sign-In.

## Security

Do not commit service-account private keys, OAuth client secrets, or Firebase Admin credentials. The Firebase client API key in `google-services.json` is intended to be shipped in the app; protect the project with Authentication and restrictive Firestore/Storage rules.
