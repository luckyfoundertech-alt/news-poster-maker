from pathlib import Path
import re, sys

MODE = sys.argv[1] if len(sys.argv) > 1 else "apply"
EDITOR = Path("opentempl/apps/editor")
SRC = EDITOR / "src"
PUBLIC = EDITOR / "public"
TEXT_EXT = {".ts",".tsx",".js",".jsx",".html",".css",".json",".webmanifest",".svg",".txt"}
SKIP_PARTS = {"node_modules","licenses","license","legal","third_party","third-party","vendor"}
# Legal attribution/permission notices are intentionally retained for licence compliance.
def eligible(path):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXT:
        return False
    if any(part.lower() in SKIP_PARTS for part in path.parts):
        return False
    # This is a private technical relay URL required by the existing Unsplash photo-search feature;
    # it is not a product/UI brand and must not be rewritten without replacing that service.
    if path.name == "unsplash.ts":
        return False
    if path.name.upper() in {"LICENSE","LICENSE.txt","NOTICE","NOTICE.txt","COPYING"}:
        return False
    return True

def apply():
    changed = []
    for folder in (SRC, PUBLIC):
        if not folder.exists():
            continue
        for p in folder.rglob("*"):
            if not eligible(p):
                continue
            try:
                original = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            updated = re.sub(r"https?://(?:www\\.)?opentempl\\.org[^\\s\\\"<>)]*", "https://example.com", original, flags=re.I)
            updated = re.sub(r"opentempl", "NEWS Studio", updated, flags=re.I)
            updated = re.sub(r"Open Templ", "NEWS Studio", updated, flags=re.I)
            updated = re.sub(r"on your computer", "on your Android device", updated, flags=re.I)
            updated = re.sub(r"on this computer", "on this device", updated, flags=re.I)
            updated = re.sub(r"desktop app", "Android app", updated, flags=re.I)
            updated = re.sub(r"desktop version", "Android version", updated, flags=re.I)
            updated = re.sub(r"Mac, Windows and Linux", "Android", updated, flags=re.I)
            if updated != original:
                p.write_text(updated, encoding="utf-8")
                changed.append(str(p))
    # Enforce a mobile viewport in the actual editor document before Vite builds it.
    html = EDITOR / "index.html"
    if html.exists():
        page = html.read_text(encoding="utf-8")
        if not re.search(r'<meta\s+name=["\']viewport["\']', page, re.I):
            page = page.replace("<head>", '<head>\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">', 1)
            html.write_text(page, encoding="utf-8")
            changed.append(str(html) + " (viewport)")
        elif "viewport-fit=cover" not in page:
            page = re.sub(r'(<meta\s+name=["\']viewport["\']\s+content=["\'])([^"\']*)', lambda m: m.group(1) + m.group(2) + ", viewport-fit=cover", page, count=1, flags=re.I)
            html.write_text(page, encoding="utf-8")
            changed.append(str(html) + " (safe-area viewport)")
    # A small global mobile guard prevents fixed-width desktop panels from widening the WebView.
    css = SRC / "mobile-compat.css"
    css.write_text("""/* NEWS Studio Android viewport and touch compatibility */
*,*::before,*::after{box-sizing:border-box}
html,body,#root{width:100%;max-width:100%;min-width:0;margin:0}
html{min-height:100%;overflow-x:hidden;-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{min-height:100dvh;overflow-x:hidden;overscroll-behavior-y:contain}
img,video,canvas,svg{max-width:100%}
button,a,input,select,textarea{touch-action:manipulation}
@media(max-width:720px){
  html,body,#root{min-width:0!important;width:100%!important;max-width:100vw!important}
  body{padding-left:env(safe-area-inset-left);padding-right:env(safe-area-inset-right)}
  input,select,textarea{font-size:16px}
  button,a{ -webkit-tap-highlight-color:transparent}
  [role=dialog],[data-radix-dialog-content]{max-width:calc(100vw - 24px)}
}
""", encoding="utf-8")
    changed.append(str(css))
    entry = SRC / "main.tsx"
    if not entry.exists():
        raise SystemExit("Android editor entry point main.tsx is missing.")
    entry_text = entry.read_text(encoding="utf-8")
    if "mobile-compat.css" not in entry_text:
        entry.write_text("import './mobile-compat.css';\n" + entry_text, encoding="utf-8")
        changed.append(str(entry) + " (mobile stylesheet import)")
    print("NEWS Studio final branding/mobile compatibility applied; changed", len(changed), "files.")

def verify(root):
    bad=[]
    for p in root.rglob("*"):
        if not eligible(p):
            continue
        try: data=p.read_text(encoding="utf-8")
        except (UnicodeDecodeError,OSError): continue
        # Ignore only the legacy photo-search relay hostname; all visible product strings are checked.
        data = data.replace("opentempl.org", "")
        if re.search(r"opentempl", data, re.I):
            bad.append(str(p))
    if bad:
        raise SystemExit("Legacy OpenTempl brand string remains in built app assets: " + ", ".join(bad[:30]))
    html=root/"index.html"
    if not html.exists():
        raise SystemExit("Built Android index.html is missing.")
    page=html.read_text(encoding="utf-8")
    if not re.search(r'<meta\s+name=["\']viewport["\'][^>]*width=device-width',page,re.I):
        raise SystemExit("Mobile viewport meta tag is missing or invalid.")
    if "NEWS Studio" not in page:
        raise SystemExit("NEWS Studio document title/brand missing from Android app.")
    print("Verified: no OpenTempl product strings in compiled Android UI assets; mobile viewport present; NEWS Studio title present.")

if MODE == "apply":
    apply()
elif MODE == "verify":
    verify(Path(sys.argv[2] if len(sys.argv)>2 else "www"))
else:
    raise SystemExit("Use apply or verify")
