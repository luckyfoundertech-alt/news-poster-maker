# NEWS Studio — Android Design Studio

NEWS Studio is an Android-packaged poster/design editor with Firebase account and cloud-sync integrations, a 337-template library, and a deterministic RSS-to-editable-poster workflow. The app intentionally contains no AI writing, image generation, background-removal model, or AI poster generation.

## Android editor integration

The Android build currently checks out a pinned OpenTempl editor revision, applies NEWS Studio branding/mobile/auth/cloud/news patches, builds its React editor and template library, packages it into the NEWS Capacitor Android shell, and produces a debug APK. **The editor has not yet been independently rewritten and the build still depends on the upstream OpenTempl source.** Its MIT license notice is retained in `OPEN-TEMPL-LICENSE`.

The editor provides a multi-page canvas, layers, typography, image editing, and the upstream template packs. The CI build verified **337 templates across 34 design styles** in the 25 November 2026 build. This is a packaging/count check, not a manual visual review of every template on physical phones.

## Newsroom workflow currently included in the Android build

The Android build patch adds a home-screen RSS panel with four configured feeds:
- Google News India (English)
- Google News India (Hindi)
- BBC Hindi
- BBC World

The feed panel refreshes headlines through the external rss2json service. A user can open the original source or choose **Create poster**. That action creates an editable A3 design with the headline, RSS summary, available feed image, source, and date. This is a deterministic field-to-layer mapping; it does not rewrite or verify the full article, fetch arbitrary full article text, or generate posters automatically in the background. Feed availability depends on the external RSS feeds, rss2json, network access, and publisher image permissions.

## Authentication and cloud sync

The build patch includes Firebase email/password registration and sign-in, password reset, Google sign-in integration, per-user Firestore metadata, and Firebase Storage-backed design/upload sync. Cloud restore is non-blocking: the editor opens while cloud designs/uploads restore in the background.

Important setup and verification requirements:
- The committed `google-services.json` currently has an empty `oauth_client` array. Google Sign-In is **not verified/configured** until a refreshed Firebase Android config containing the correct OAuth client is committed.
- Publish the restrictive `firestore.rules` and `storage.rules` to Firebase project `ghost-b9156`; the presence of rule files in this repository does not prove they have been deployed.
- Real-device tests are still required for Google Sign-In, cloud conflict handling, large image restore, offline behavior, and Android export/share.

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for the exact Firebase setup checklist.

## Build Android APK

Run **Actions → Build NEWS Android APK → Run workflow**. Download the `NEWS-Studio-Android-APK` artifact from the completed workflow run.

The workflow currently produces an **unsigned-for-Play-Store debug APK** unless all four persistent release-signing GitHub Actions secrets are configured. A successful debug build is not a Play Store release and does not prove physical-device compatibility.

## Remaining work

- Replace the upstream editor with a genuinely independent implementation. This has not been completed.
- Finish Firebase OAuth setup, deploy rules, and verify Google/email login and cloud media restore on real Android devices.
- Test layouts and touch interactions on a representative range of Android screen sizes, densities, and Android versions.
- Add automated tests for RSS parsing, feed failure/retry, and article-to-poster mapping; manually verify every template.
- Configure a persistent release keystore and Firebase release SHA fingerprints, then build and verify a signed release APK/AAB.

## License

NEWS Android shell code: MIT. The embedded editor is from [noah-thing/opentempl](https://github.com/noah-thing/opentempl) and is distributed under its MIT license; see `OPEN-TEMPL-LICENSE`. Required notices remain in the distributed materials even though upstream branding is removed from the normal app UI.
