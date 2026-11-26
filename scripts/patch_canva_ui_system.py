from pathlib import Path
import re

src = Path("opentempl/apps/editor/src")
main = src / "main.tsx"
if not main.exists():
    raise SystemExit("Editor entry point missing; refusing to apply UI system.")

css = r"""
/* NEWS Studio — unified Canva-inspired Android design system.
   Original NEWS Studio styling; existing editor controls and data flows are untouched. */
:root {
  --ns-bg: #f7f7fb;
  --ns-surface: #ffffff;
  --ns-surface-2: #f3f2fa;
  --ns-ink: #181827;
  --ns-muted: #707087;
  --ns-line: #e8e7f0;
  --ns-primary: #7657f6;
  --ns-primary-hover: #6445e8;
  --ns-radius: 16px;
  --ns-shadow: 0 5px 22px rgba(28, 24, 65, .07);
  color-scheme: light;
}
html, body, #root { max-width:100%; min-width:0; }
body { background:var(--ns-bg); color:var(--ns-ink); }
button, input, select, textarea { font-family:inherit; }
button { -webkit-tap-highlight-color:transparent; }
:focus-visible { outline:3px solid rgba(118,87,246,.35); outline-offset:2px; }

/* Shared page frame and navigation */
.ns-projects,.ns-templates-page,.ns-newsroom,.ns-profile {
  background:var(--ns-bg)!important; color:var(--ns-ink)!important;
}
.ns-projects-head,.ns-newsroom-head,.ns-profile-head {
  min-height:64px!important; background:rgba(255,255,255,.94)!important;
  border-bottom:1px solid var(--ns-line)!important; box-shadow:0 2px 12px rgba(25,20,55,.035);
  padding-left:clamp(14px,3vw,36px)!important; padding-right:clamp(14px,3vw,36px)!important;
}
.ns-projects-head .btn,.ns-newsroom-head .btn,.ns-profile-head button {
  min-height:40px; border-radius:11px!important; font-weight:650;
}
.ns-bottom-nav {
  min-height:70px!important; background:rgba(255,255,255,.96)!important;
  border-top:1px solid var(--ns-line)!important; box-shadow:0 -5px 22px rgba(25,20,55,.06);
  backdrop-filter:blur(20px);
}
.ns-bottom-nav>a { color:#85849a!important; font-weight:550; }
.ns-bottom-nav>a.active { color:var(--ns-primary)!important; }
.ns-bottom-nav>a.ns-bottom-create {
  background:linear-gradient(145deg,#9278ff,#6949ed)!important;
  box-shadow:0 7px 18px rgba(118,87,246,.28)!important;
}

/* Home: spacious creative dashboard */
.home { background:var(--ns-bg)!important; color:var(--ns-ink)!important; }
.home-top {
  min-height:66px!important; background:rgba(255,255,255,.96)!important;
  border-bottom:1px solid var(--ns-line)!important; box-shadow:0 2px 12px rgba(25,20,55,.035);
  padding-left:clamp(14px,3vw,40px)!important; padding-right:clamp(14px,3vw,40px)!important;
}
.home-top .home-nav a,.home-top .home-nav button { color:#5e5d72!important; font-weight:600; }
.home-top .home-nav a:hover,.home-top .home-nav button:hover { color:var(--ns-primary)!important; }
.home-top .btn-primary,.home .btn-primary {
  background:var(--ns-primary)!important; border-color:var(--ns-primary)!important;
  color:#fff!important; border-radius:11px!important; box-shadow:0 4px 12px rgba(118,87,246,.18);
}
.home-top .btn-primary:hover,.home .btn-primary:hover { background:var(--ns-primary-hover)!important; }
.home main { max-width:1440px!important; padding-left:clamp(14px,3vw,42px)!important; padding-right:clamp(14px,3vw,42px)!important; }
.ns-dashboard { max-width:1180px!important; }
.ns-welcome h1 { color:var(--ns-ink)!important; }
.ns-welcome h1 span { color:var(--ns-primary)!important; }
.ns-eyebrow { color:#8a879f!important; }
.ns-pro-badge { background:#f0edff!important; border-color:#e3dcff!important; color:#6849e8!important; }
.ns-main-search,.ns-global-search {
  background:#fff!important; border:1px solid var(--ns-line)!important; border-radius:14px!important;
  box-shadow:0 2px 8px rgba(25,20,55,.025);
}
.ns-main-search:focus-within,.ns-global-search:focus-within {
  border-color:#b9aaff!important; box-shadow:0 0 0 4px rgba(118,87,246,.09);
}
.ns-quick-grid>button { color:var(--ns-ink)!important; }
.ns-quick-grid>button:active { transform:scale(.97); }
.ns-quick-icon { border-radius:15px!important; box-shadow:0 5px 14px rgba(36,30,80,.12)!important; }
.ns-feature-strip>a,.home-section {
  background:var(--ns-surface)!important; border:1px solid var(--ns-line)!important;
  border-radius:var(--ns-radius)!important; box-shadow:var(--ns-shadow);
}
.home-section { padding:20px!important; }
.home-section-head h2 { color:var(--ns-ink)!important; }
.home-section-head .muted,.home .muted { color:var(--ns-muted)!important; }
.ns-feature-strip>a { color:var(--ns-ink)!important; }
.ns-feature-icon { background:#f0edff!important; color:var(--ns-primary)!important; }
.design-grid { gap:16px!important; }
.design-grid>* { border-radius:13px!important; }
.design-thumb { background:#f0eff6!important; border:1px solid var(--ns-line)!important; }
.ns-see-all,.ns-section-label>a { color:var(--ns-primary)!important; }

/* Templates: true discovery gallery with legible categories and image-first cards */
.ns-templates-page { min-height:100dvh; padding-bottom:calc(90px + env(safe-area-inset-bottom)); }
.ns-template-search { width:min(100% - 32px,920px); margin:18px auto 14px!important; }
.ns-template-categories {
  width:min(100% - 32px,1120px); margin:0 auto 22px; padding:3px 0 9px;
  display:flex; gap:8px; overflow-x:auto; scrollbar-width:none;
}
.ns-template-categories::-webkit-scrollbar { display:none; }
.ns-template-categories button {
  flex:none; min-height:37px; padding:8px 14px; border:1px solid var(--ns-line);
  border-radius:999px; background:#fff; color:#66647b; font-size:12px; font-weight:650;
}
.ns-template-categories button.active {
  color:#fff; background:var(--ns-primary); border-color:var(--ns-primary);
}
.ns-template-section { width:min(100% - 32px,1120px); margin:0 auto 34px; }
.ns-template-section-head { display:flex; align-items:end; justify-content:space-between; gap:12px; margin:0 0 15px; }
.ns-template-section-head h2 { margin:0; color:var(--ns-ink); font-size:21px; letter-spacing:-.035em; }
.ns-template-section-head p,.ns-template-section-head>span { margin:5px 0 0; color:var(--ns-muted); font-size:11px; }
.ns-template-grid {
  display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px;
}
.ns-template-card {
  min-width:0; padding:0; overflow:hidden; text-align:left; color:var(--ns-ink);
  background:#fff; border:1px solid var(--ns-line); border-radius:13px;
  box-shadow:0 3px 12px rgba(28,24,65,.045); transition:transform .16s ease,box-shadow .16s ease;
}
.ns-template-card:active { transform:scale(.985); }
.ns-template-thumb { width:100%; aspect-ratio:4/5; display:grid; place-items:center; overflow:hidden; background:#f0eff6; }
.ns-template-thumb img { width:100%; height:100%; object-fit:contain; }
.ns-template-meta { display:grid; gap:4px; padding:10px 11px 12px; }
.ns-template-meta b { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:12px; font-weight:700; }
.ns-template-meta small { color:var(--ns-muted); font-size:10px; }
.ns-template-skeleton { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px; }
.ns-template-skeleton i { aspect-ratio:4/5; border-radius:13px; background:linear-gradient(100deg,#eeedf4 20%,#faf9fc 45%,#eeedf4 70%); background-size:220% 100%; }

/* Projects and profile */
.ns-projects-intro,.ns-project-stats,.ns-project-tools,.ns-project-grid,.ns-project-list,.ns-project-empty { width:min(100% - 32px,1120px)!important; }
.ns-projects-intro h1,.ns-profile-card h1 { color:var(--ns-ink)!important; }
.ns-project-stats>div,.ns-project-card,.ns-project-tools .ns-main-search {
  background:#fff!important; border:1px solid var(--ns-line)!important; border-radius:13px!important;
  box-shadow:0 2px 10px rgba(28,24,65,.035);
}
.ns-project-card { overflow:hidden; }
.ns-project-card:active { transform:scale(.99); }
.ns-project-thumb { background:#f2f1f7!important; }
.ns-project-filters button,.ns-view-toggle button {
  background:#fff!important; border-color:var(--ns-line)!important; color:#68667d!important;
  border-radius:10px!important; min-height:36px;
}
.ns-project-filters button.active,.ns-view-toggle button.active {
  background:#f0edff!important; border-color:#d8ceff!important; color:#6949e8!important;
}
.ns-profile { min-height:100dvh; }
.ns-profile-card,.ns-profile-stats>div,.ns-profile-design,.ns-profile-file {
  background:#fff!important; border-color:var(--ns-line)!important; box-shadow:0 3px 12px rgba(28,24,65,.04);
}
.ns-profile-tabs button.active { color:var(--ns-primary)!important; border-color:var(--ns-primary)!important; }
.ns-profile-save { background:var(--ns-primary)!important; border-radius:11px!important; }

/* Dedicated Newsroom */
.ns-newsroom { min-height:100dvh; padding-bottom:calc(90px + env(safe-area-inset-bottom)); }
.ns-newsroom-intro h1 { color:var(--ns-ink)!important; }
.ns-newsroom-kicker { color:var(--ns-primary)!important; }
.ns-newsroom-feed .home-section { background:#fff!important; border:1px solid var(--ns-line)!important; box-shadow:var(--ns-shadow); }
.ns-newsroom-feed article {
  background:#fff!important; border:1px solid var(--ns-line)!important; border-radius:13px!important;
  box-shadow:0 2px 10px rgba(28,24,65,.035);
}
.ns-newsroom-feed article h3 { color:var(--ns-ink)!important; }

/* Start-design / format picker */
.start { background:var(--ns-bg)!important; color:var(--ns-ink)!important; }
.start-head h1 { color:var(--ns-ink)!important; }
.start-size,.start-tpl,.start-tool,.start-card {
  border-radius:14px!important; border-color:var(--ns-line)!important; background:#fff!important;
  box-shadow:0 2px 10px rgba(28,24,65,.04);
}
.start-size:hover,.start-tpl:hover { border-color:#b9aaff!important; }
.start-tabs button[aria-selected=true],.start-tabs button.active { color:var(--ns-primary)!important; }

/* Editor workspace — retain canvas and editing controls; unify chrome, panels and touch targets. */
.editor,.editor-root,.editor-shell,.editor-layout,.editor-workspace,.canvas-editor {
  color:var(--ns-ink);
}
.editor-toolbar,.editor-topbar,.workspace-toolbar,[data-editor-toolbar] {
  background:#fff!important; border-color:var(--ns-line)!important; box-shadow:0 2px 12px rgba(28,24,65,.045);
}
.editor-sidebar,.editor-panel,.workspace-sidebar,[data-editor-panel] {
  background:#fff!important; border-color:var(--ns-line)!important;
}
.editor-toolbar button,.editor-topbar button,.workspace-toolbar button,
.editor-sidebar button,.editor-panel button,[data-editor-toolbar] button,[data-editor-panel] button {
  min-height:36px; border-radius:9px; transition:background .15s ease,color .15s ease;
}
.editor-toolbar button:hover,.editor-topbar button:hover,.workspace-toolbar button:hover,
.editor-sidebar button:hover,.editor-panel button:hover,[data-editor-toolbar] button:hover,[data-editor-panel] button:hover {
  background:#f0edff!important; color:var(--ns-primary)!important;
}
.editor-sidebar input,.editor-panel input,.editor-panel select,.editor-panel textarea,
[data-editor-panel] input,[data-editor-panel] select,[data-editor-panel] textarea {
  min-height:40px; border:1px solid var(--ns-line); border-radius:9px; background:#fff;
}
.canvas-wrap,.canvas-stage,.editor-canvas-area { background:#eeedf4!important; }
@media(max-width:720px) {
  .ns-projects-intro,.ns-project-stats,.ns-project-tools,.ns-project-grid,.ns-project-list,.ns-project-empty,
  .ns-template-search,.ns-template-categories,.ns-template-section,.ns-newsroom-intro,.ns-newsroom-feed {
    width:calc(100% - 24px)!important;
  }
  .ns-projects-intro { padding-top:19px; }
  .ns-template-grid { gap:9px; }
  .ns-template-meta { padding:8px 8px 10px; }
  .ns-template-meta b { font-size:11px; }
  .ns-template-meta small { font-size:9px; }
  .home main { padding-bottom:calc(92px + env(safe-area-inset-bottom))!important; }
  .home-section { padding:14px!important; }
  .ns-bottom-nav { min-height:66px!important; }
}
@media(min-width:720px) {
  .ns-template-grid { grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:17px; }
  .ns-project-grid { grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:16px; }
}
@media(prefers-reduced-motion:reduce) {
  *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; animation:none!important; }
}
"""
css_path = src / "news-studio-design-system.css"
css_path.write_text(css, encoding="utf-8")

text = main.read_text(encoding="utf-8")
if "news-studio-design-system.css" not in text:
    imports = list(re.finditer(r"^import\s+.*?;\s*$", text, re.M))
    if imports:
        pos = imports[-1].end()
        text = text[:pos] + "\nimport './news-studio-design-system.css';" + text[pos:]
    else:
        text = "import './news-studio-design-system.css';\n" + text
    main.write_text(text, encoding="utf-8")
print("Applied unified NEWS Studio design system across Home, Templates, Projects, Newsroom, Profile, Start and editor chrome.")
