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
            updated = re.sub(r'https?://(?:www\.)?opentempl\.org[^\s"<>)]*', "https://example.com", original, flags=re.I)
            # Rebrand product-name literals, not internal camelCase identifiers such as opentemplRender.
            updated = updated.replace("OpenTempl", "NEWS Studio").replace("Open Templ", "NEWS Studio")
            updated = re.sub(r"on your computer", "on your Android device", updated, flags=re.I)
            updated = re.sub(r"on this computer", "on this device", updated, flags=re.I)
            updated = re.sub(r"desktop app", "Android app", updated, flags=re.I)
            updated = re.sub(r"desktop version", "Android version", updated, flags=re.I)
            updated = re.sub(r"Mac, Windows and Linux", "Android", updated, flags=re.I)
            if updated != original:
                p.write_text(updated, encoding="utf-8")
                changed.append(str(p))
    # Rebrand the HTML document and remove upstream author/social metadata from JSON-LD.
    html = EDITOR / "index.html"
    if html.exists():
        page = html.read_text(encoding="utf-8")
        page = page.replace("OpenTempl", "NEWS Studio").replace("Open Templ", "NEWS Studio")
        page = page.replace("canva-vs-opentempl", "news-studio-vs-canva")
        page = re.sub(r'"sameAs"\s*:\s*\[[^\]]*\]\s*,?', "", page)
        html.write_text(page, encoding="utf-8")
    # Enforce a mobile viewport in the actual editor document before Vite builds it.
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

    # Apply home/template visual polish last, after Stitch page composition and brand rewrites.
    home_css = SRC / "home" / "home.css"
    if home_css.exists():
        styles = """
/* Final Canva-inspired NEWS Studio home and template layout */
.home{background:#101114;color:#f7f7fa}
.home main{max-width:1440px;padding:22px clamp(12px,3vw,42px) 48px}
.home-top{min-height:66px;gap:10px;padding:10px clamp(12px,3vw,42px);border-bottom:1px solid #30333c}
.home-top .ns-global-search{width:min(390px,34vw);min-width:180px;height:44px;border-radius:12px;background:#1b1d23;border-color:#383b46}
.home-top .btn{min-height:42px;display:inline-flex;align-items:center;justify-content:center;border-radius:10px;white-space:nowrap}
.hero{min-height:0;max-width:1440px;margin:0 auto;border-radius:20px;overflow:hidden;background:linear-gradient(112deg,#202a49,#29265f 60%,#38236d)}
.hero-in{min-height:0;padding:clamp(22px,3.5vw,46px);gap:20px}
.hero-top{grid-template-columns:minmax(0,1.15fr) minmax(220px,.85fr);gap:22px}
.hero-copy h1{max-width:11em;font-size:clamp(35px,4.2vw,60px);line-height:1.04;font-weight:700}
.hero-copy p{max-width:560px;margin:15px 0 19px;line-height:1.6}
.hero-btn{height:44px;border-radius:10px;font-weight:650}
.hero-base{grid-template-columns:repeat(4,minmax(0,1fr));gap:11px;margin-top:10px}
.hero-ask{grid-column:span 2;padding:13px 15px;border:1px solid #ffffff30;border-radius:13px;background:#080c1c30}
.hero-col{grid-column:auto;min-width:0;padding:13px;border:1px solid #ffffff2b;border-radius:13px;background:#080c1c24}
.hero-col b{font-weight:700}.hero-col>span:not(.hero-n){display:block;font-size:12px;line-height:1.5}
.home-section{margin:0 0 22px;padding:19px;border:1px solid #2c2f38;border-radius:16px;background:#15171c}
.home-section-head{align-items:center;margin-bottom:15px}.home-section-head h2{font-size:clamp(21px,2.2vw,28px);font-weight:700}
.design-grid{grid-template-columns:repeat(auto-fill,minmax(min(100%,185px),1fr));gap:14px}
.design-thumb{aspect-ratio:1.2;border:1px solid #30333d;border-radius:12px;overflow:hidden}
#news-feed{margin:0 auto 22px}#news-feed>section{border:1px solid #2c2f38!important;border-radius:16px!important;padding:19px!important;background:#15171c}
#news-feed article{background:#1b1d23;border-color:#343741!important}#news-feed article img{height:auto!important;aspect-ratio:16/9;object-fit:cover}
#template-library{scroll-margin-top:82px}
.chips.vibe-chips{gap:8px;padding:11px 0;margin:0 0 15px;top:var(--bar,66px);background:#15171c;box-shadow:0 0 0 100vmax #15171c,0 1px 0 100vmax #2c2f38}
.vibe-chips .chip{flex:none;min-height:36px;padding:8px 13px;border:1px solid #393d48;border-radius:999px;background:#20232b;color:#c8ccd5;font-size:12px}
.vibe-chips .chip.is-on{background:#6558e8;border-color:#8278ff;color:white}
.masonry{gap:14px}.masonry>div{min-width:0;display:flex;flex-direction:column;gap:14px}
.masonry .wall-card,.wall .wall-card{min-width:0;margin:0;overflow:hidden;border:1px solid #30333d;border-radius:11px;background:#1b1d23;color:#f7f7fa}
.masonry .wall-card img,.wall .wall-card img{display:block;width:100%;height:auto;border-radius:0;box-shadow:none}
.masonry .wall-card:hover img,.wall .wall-card:hover img{transform:none;box-shadow:none}
.masonry .wall-meta,.wall .wall-meta{padding:9px 10px 11px;gap:3px}
.masonry .wall-meta b,.wall .wall-meta b{font-size:12px;line-height:1.4}
.wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,185px),1fr));gap:14px;columns:unset}
@media(max-width:1000px){.hero-top{grid-template-columns:minmax(0,1fr) minmax(200px,.7fr)}.hero-base{grid-template-columns:repeat(2,minmax(0,1fr))}.hero-ask{grid-column:span 2}}
@media(max-width:720px){
 .home-top{display:flex;flex-wrap:wrap;gap:8px;padding:calc(8px + env(safe-area-inset-top)) 12px 8px}
 .home-top .home-brand{order:1;margin:0 auto 0 0}.home-top .btn-primary{order:2;min-height:40px;padding:0 11px}
 .home-top .home-menu-btn{order:3;display:grid;width:40px;height:40px;margin:0}
 .home-top .ns-global-search{order:4;display:flex;width:100%;max-width:none;min-width:0;height:44px;margin:2px 0 0}
 .home-top .home-nav,.home-top .home-open{display:none}
 .home main{padding:12px 10px calc(28px + env(safe-area-inset-bottom))}
 .hero{border-radius:14px}.hero-in{padding:19px 13px 13px;gap:14px}.hero-top{display:block}
 .hero-copy h1{max-width:12em;font-size:clamp(30px,8.7vw,41px);line-height:1.06}
 .hero-copy p{margin:11px 0 15px;font-size:13px;line-height:1.55}
 .hero-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.hero-btn{width:100%;min-width:0;height:42px;justify-content:center;padding:0 7px;font-size:12px}
 .bloom{display:none}.hero-base{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:13px;padding-top:12px}
 .hero-ask{grid-column:1/-1;min-width:0;padding:10px}.hero-ask input{font-size:17px}
 .hero-col{grid-column:auto;min-width:0;padding:9px}.hero-col:nth-of-type(3){grid-column:1/-1}
 .home-section{padding:13px 10px;margin-bottom:15px;border-radius:12px}
 .home-section-head{flex-wrap:wrap;align-items:flex-start;gap:9px;margin-bottom:11px}.home-section-head h2{font-size:20px}
 .home-section-head>.row{width:100%;flex-wrap:wrap}.home-search{width:100%;max-width:none}
 .design-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
 #news-feed{margin-bottom:15px}#news-feed>section{padding:13px 10px!important}#news-feed select{flex:1;min-width:0;max-width:none!important}
 #template-library{scroll-margin-top:124px}
 .chips.vibe-chips{top:var(--bar,116px);margin-bottom:12px;padding:8px 0}
 .vibe-chips .chip{min-height:36px;padding:8px 11px}
 .masonry{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:8px}
 .masonry>div{gap:8px}.masonry .wall-card,.wall .wall-card{border-radius:9px}
 .masonry .wall-meta,.wall .wall-meta{padding:7px 8px 9px}
 .masonry .wall-meta b,.wall .wall-meta b{font-size:11px}
 .wall{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
}
@media(max-width:380px){.hero-actions{grid-template-columns:1fr}.masonry,.wall{gap:7px}}
"""
        current = home_css.read_text(encoding="utf-8")
        if "Final Canva-inspired NEWS Studio home and template layout" not in current:
            home_css.write_text(current + "\n" + styles, encoding="utf-8")
        home_tsx = SRC / "home" / "Home.tsx"
        if home_tsx.exists():
            hs = home_tsx.read_text(encoding="utf-8")
            hs = hs.replace("setCols(Math.max(2, Math.min(6, Math.floor((el.clientWidth + 20) / 240))))", "setCols(Math.max(2, Math.min(5, Math.floor((el.clientWidth + 18) / 220))))")
            home_tsx.write_text(hs, encoding="utf-8")

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
        if "OpenTempl" in data or "Open Templ" in data:
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
