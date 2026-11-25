# NEWS — Android Design Studio

NEWS is an Android-packaged design studio built around the upstream OpenTempl editor (MIT licensed), with the goal of adding newsroom workflows and account-backed cloud projects.

## Android editor integration
The Android APK workflow checks out the OpenTempl source, builds its complete React editor and template library, packages that editor into the NEWS Capacitor Android shell, and builds a debug APK.

OpenTempl upstream advertises 337 templates, a multi-page editor, layers, smart guides, text effects, charts, tables, vector pen, photo editing, PDF/PowerPoint import, and PNG/JPG/PDF/SVG/PowerPoint/GIF/video export. See https://github.com/noah-thing/opentempl and retain the included MIT license notice.

## Build Android APK
Run **Actions → Build NEWS Android APK → Run workflow**. Download the `NEWS-Studio-Android-APK` artifact from the completed workflow run.

## Important current limitations
- The upstream editor itself is local-first and does not provide NEWS user accounts or central cloud project storage.
- News source fetching and article-to-poster generation are not yet connected to a NEWS backend.
- Live sharing/editor capabilities depend on the upstream services and device/browser support.
- The workflow produces a debug APK, not a Play Store-signed release.
- The build must complete and the APK must be installed and device-tested before claiming Android compatibility for every editor feature.

## License
NEWS Android shell code: MIT. The embedded OpenTempl editor is from https://github.com/noah-thing/opentempl and is distributed under its MIT license; see `OPEN-TEMPL-LICENSE`.
