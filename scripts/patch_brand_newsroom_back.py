from pathlib import Path
import re, json, base64

root = Path("opentempl/apps/editor/src")
public = Path("opentempl/apps/editor/public")
public.mkdir(parents=True, exist_ok=True)
logo_b64 = Path("scripts/news-studio-logo.webp.b64")
if not logo_b64.exists():
    raise SystemExit("Supplied NEWS Studio logo source is missing.")
(public / "news-studio-logo.webp").write_bytes(base64.b64decode(logo_b64.read_text().strip()))
logo = root / "ui/Logo.tsx"
logo.write_text("""export function Mark({ size = 28 }: { size?: number }) {
  return <img src={import.meta.env.BASE_URL + 'news-studio-logo.webp'} width={size} height={size} alt="NEWS Studio" draggable={false} style={{ display: 'block', flex: 'none', objectFit: 'contain' }} />;
}
export function Wordmark({ size = 22 }: { size?: number }) {
  return <span style={{ display: 'inline-flex', alignItems: 'center', gap: size * 0.4, fontWeight: 700, fontSize: size, letterSpacing: '-0.045em' }}><Mark size={size * 1.25} />NEWS Studio</span>;
}
export function Sign({ size = 40 }: { size?: number; mood?: string }) {
  return <Mark size={size} />;
}
""", encoding="utf-8")
app = root / "App.tsx"
s = app.read_text(encoding="utf-8")

# Remove desktop-only integration code; keep Android-native import/export flows.
s = re.sub(r"declare global \{\s*interface Window \{\s*tavlaDesktop\?:.*?\n\}\n\n// Inside the desktop app:.*?\n\}\n", "", s, flags=re.S)
if "tavlaDesktop" in s:
    raise SystemExit("Desktop bridge remains in App.tsx; refusing partial cleanup.")
s = s.replace("import { Sign } from './ui/Logo';\n", "")
s = s.replace("import { Home } from './home/Home';", "import { Home } from './home/Home';\nimport { Newsroom } from './home/Newsroom';")
if "if (path === '/newsroom') return <Newsroom />;" not in s:
    s = s.replace("  if (path === '/icons') return <IconSheet />;", "  if (path === '/newsroom') return <Newsroom />;\n  if (path === '/icons') return <IconSheet />;", 1)
s = s.replace("document.title = 'OpenTempl';", "document.title = 'NEWS Studio';")
app.write_text(s, encoding="utf-8")

# Dedicated RSS newsroom page: same RSS parser and original article-to-template action.
newsroom = root / "home/Newsroom.tsx"
newsroom.write_text("""import { NewsFeed } from './NewsFeed';
import { navigate } from '../App';
import { Wordmark } from '../ui/Logo';
import './home.css';

export function Newsroom() {
  return <main className='ns-newsroom'>
    <header className='ns-newsroom-head'>
      <button className='btn btn-outline' onClick={() => navigate('/')}>← Home</button>
      <Wordmark size={21}/>
      <span className='ns-newsroom-spacer'/>
      <button className='btn btn-primary' onClick={() => navigate('/start')}>Create design</button>
    </header>
    <section className='ns-newsroom-intro'>
      <span className='ns-newsroom-kicker'>NEWS STUDIO · LIVE FEEDS</span>
      <h1>Newsroom</h1>
      <p>Choose a news source, review the original headline and details, then create an editable poster from the selected story.</p>
    </section>
    <div className='ns-newsroom-feed'><NewsFeed /></div>
  </main>;
}
""", encoding="utf-8")

css = root / "home/home.css"
c = css.read_text(encoding="utf-8")
if ".ns-newsroom{" not in c:
    c += """
.ns-newsroom{height:100dvh;overflow:auto;background:var(--paper);color:var(--ink);padding-bottom:env(safe-area-inset-bottom)}
.ns-newsroom-head{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:12px;min-height:60px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line)}
.ns-newsroom-spacer{flex:1}
.ns-newsroom-intro{width:min(100% - 32px,1100px);margin:28px auto 16px}
.ns-newsroom-kicker{font-size:11px;font-weight:800;letter-spacing:.12em;color:var(--accent,#304ffe)}
.ns-newsroom-intro h1{font-size:clamp(28px,5vw,42px);letter-spacing:-.04em;margin:8px 0}
.ns-newsroom-intro p{max-width:680px;color:var(--ink-2);font-size:14px;line-height:1.55}
.ns-newsroom-feed{width:min(100% - 32px,1100px);margin:0 auto 40px}
.ns-newsroom-feed .home-section{border:0!important;padding:0!important}
@media(max-width:520px){.ns-newsroom-head{padding:8px 12px;gap:8px}.ns-newsroom-intro,.ns-newsroom-feed{width:calc(100% - 24px)}.ns-newsroom-intro{margin-top:18px}}
"""
css.write_text(c, encoding="utf-8")

# Remove the RSS feed from the crowded home dashboard; link to its dedicated page.
home = root / "home/Home.tsx"
h = home.read_text(encoding="utf-8")
h = re.sub(r'\s*<div id="news-feed"><NewsFeed query=\{tq\} /></div>', "", h)
h = re.sub(r'\s*<NewsFeed(?: query=\{tq\})?\s*/>', "", h)
h = h.replace("import { NewsFeed } from './NewsFeed';\n", "")
if 'href="#/newsroom"' not in h:
    h = h.replace('<nav className="home-nav">', '<nav className="home-nav">\n          <a href="#/newsroom">Newsroom</a>', 1)
    h = h.replace('<nav className="home-sheet" onClick={() => setMenu(false)}>', '<nav className="home-sheet" onClick={() => setMenu(false)}>\n            <a href="#/newsroom">Newsroom</a>', 1)
home.write_text(h, encoding="utf-8")

# Remove remaining Electron-only bridge references from the Android entry point and metrics.
main_file = root / "main.tsx"
if main_file.exists():
    m = main_file.read_text(encoding="utf-8")
    m = m.replace(" && !('tavlaDesktop' in window)", "")
    m = m.replace("not in the desktop app, which is offline already", "for Android app sessions")
    main_file.write_text(m, encoding="utf-8")

stats = root / "stats/client.ts"
if stats.exists():
    st = stats.read_text(encoding="utf-8")
    st = re.sub(r"function platform\(\): Platform \{.*?\n\}", "function platform(): Platform { return 'web'; }", st, flags=re.S)
    st = st.replace("'opentempl:install'", "'news-studio:install'")
    st = st.replace("'opentempl:share-counts'", "'news-studio:share-counts'")
    st = st.replace("'opentempl:pinged'", "'news-studio:pinged'")
    st = st.replace("'opentempl:subscribed'", "'news-studio:subscribed'")
    st = st.replace("'opentempl:export-note'", "'news-studio:export-note'")
    # Old upstream telemetry is not part of NEWS Studio; keep the API inert.
    st = st.replace("const BASE = (import.meta.env.VITE_STATS_URL as string | undefined) ?? 'https://opentempl-stats.opencursor.workers.dev';", "const BASE = '';")
    st = st.replace("function allowed(): boolean {", "function allowed(): boolean {\n  return false;")
    stats.write_text(st, encoding="utf-8")

# Remove desktop bridge typing from photo search while preserving its configured proxy.
unsplash = root / "panels/unsplash.ts"
if unsplash.exists():
    u = unsplash.read_text(encoding="utf-8")
    u = u.replace("return window.tavlaDesktop || !web ? 'https://opentempl.org' : '';",
                  "return !web ? 'https://opentempl.org' : '';")
    u = u.replace("u.searchParams.set('utm_source', 'opentempl');", "u.searchParams.set('utm_source', 'news-studio');")
    unsplash.write_text(u, encoding="utf-8")

# Use the attached brand mark on authentication screens as well as the editor wordmark.
auth_gate = root / "auth/AuthGate.tsx"
if auth_gate.exists():
    auth_text = auth_gate.read_text(encoding="utf-8")
    auth_text, count = re.subn(r"const LOGO = [^;]+;", "const LOGO = import.meta.env.BASE_URL + 'news-studio-logo.webp';", auth_text, count=1)
    if count != 1: raise SystemExit("Authentication logo source was not found.")
    auth_gate.write_text(auth_text, encoding="utf-8")

# Rebrand all visible source/UI strings while preserving legal and dependency notices.
extensions = {".ts",".tsx",".js",".jsx",".html",".css"}
for folder in [root, Path("opentempl/apps/editor/public")]:
    if not folder.exists(): continue
    for p in folder.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensions: continue
        if any(x in p.parts for x in ["node_modules","licenses","legal","third_party","third-party"]): continue
        try: t = p.read_text(encoding="utf-8")
        except Exception: continue
        original = t
        # Remove visible desktop download/install copy, not internal source/licence records.
        t = re.sub(r"<a\b[^>]*href=[\"'][^\"']*/download[^\"']*[\"'][^>]*>.*?</a>", "", t, flags=re.I|re.S)
        t = re.sub(r"<[^>]+>[^<]*(?:Desktop app|Desktop version|Install on Mac|Mac, Windows and Linux|Windows and macOS)[^<]*</[^>]+>", "", t, flags=re.I|re.S)
        if t != original: p.write_text(t, encoding="utf-8")

# Android system back: close the current editor sheet/dialog first, then pop one route.
# The native plugin is installed in the workflow; fallback keeps browser builds functional.
if "installAndroidBackNavigation" not in s:
    s = s.replace("export function App() {", """let backHandlerInstalled = false;
function installAndroidBackNavigation() {
  if (backHandlerInstalled) return;
  backHandlerInstalled = true;
  const handleBack = (exitApp?: () => void) => {
    const keyEvent = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true });
    document.dispatchEvent(keyEvent);
    if (keyEvent.defaultPrevented) return;
    const current = window.location.hash.replace(/^#/, '') || '/';
    if (current !== '/') {
      if (window.history.length > 1) window.history.back();
      else window.location.hash = '#/';
      return;
    }
    exitApp?.();
  };
  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && event.defaultPrevented) return;
  });
  void import('@capacitor/app').then(({ App: NativeApp }) => {
    void NativeApp.addListener('backButton', () => handleBack(() => { void NativeApp.exitApp(); }));
  }).catch(() => {
    window.addEventListener('popstate', () => {});
  });
}

export function App() {
  useEffect(() => { installAndroidBackNavigation(); }, []);""", 1)

# Add a clear newsroom entry in mobile navigation if the earlier patch layout differs.
if 'href="#/newsroom"' not in h:
    raise SystemExit("Newsroom navigation link was not added.")
app.write_text(s, encoding="utf-8")

# Remove upstream marketing/SEO pages and old standalone marks from the Android package.
import shutil
for page in public.rglob("*.html"):
    page.unlink()
for old_mark in public.glob("mark-*.png"):
    old_mark.unlink()
seo_assets = public / "seo"
if seo_assets.exists():
    shutil.rmtree(seo_assets)

manifest = public / "manifest.webmanifest"
if manifest.exists():
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["name"] = "NEWS Studio"
        data["short_name"] = "NEWS Studio"
        data["description"] = "Create, edit and export professional news graphics on Android."
        data["icons"] = [{"src": "news-studio-logo.webp", "sizes": "64x64", "type": "image/webp", "purpose": "any maskable"}]
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    except Exception as exc:
        raise SystemExit("Could not update NEWS Studio app manifest: " + str(exc))

# Android app metadata and legacy desktop/computer copy cleanup.
editor_html = Path("opentempl/apps/editor/index.html")
if editor_html.exists():
    page = editor_html.read_text(encoding="utf-8")
    page = re.sub(r"<title>.*?</title>", "<title>NEWS Studio</title>", page, flags=re.I|re.S)
    if 'name="description"' in page:
        page = re.sub(r'<meta name="description" content="[^"]*"', '<meta name="description" content="NEWS Studio — professional poster and news graphic design on Android."', page, flags=re.I)
    page = page.replace("</head>", '<link rel="icon" type="image/webp" href="/news-studio-logo.webp"></head>')
    editor_html.write_text(page, encoding="utf-8")

for folder in [root, public]:
    if not folder.exists(): continue
    for p in folder.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".ts",".tsx",".js",".jsx",".html",".css"}: continue
        try: t = p.read_text(encoding="utf-8")
        except Exception: continue
        original = t
        t = re.sub(r"on your computer", "on your Android device", t, flags=re.I)
        t = re.sub(r"stays on this computer", "stays in your NEWS Studio account", t, flags=re.I)
        t = re.sub(r"Desktop app for Mac, Windows and Linux", "", t, flags=re.I)
        t = re.sub(r"Desktop app", "Android app", t, flags=re.I)
        t = re.sub(r"desktop version", "Android version", t, flags=re.I)
        t = t.replace(".opentempl,.tavla,.pdf,.pptx", ".newsstudio,.pdf,.pptx")
        t = t.replace(".opentempl,.tavla", ".newsstudio")
        t = t.replace("opentempl|tavla", "newsstudio")
        if t != original: p.write_text(t, encoding="utf-8")

print("NEWS Studio branding cleanup, dedicated RSS Newsroom route, and Android back handler patched.")
