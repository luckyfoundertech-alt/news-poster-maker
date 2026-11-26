from pathlib import Path
import re

root = Path("opentempl/apps/editor/src")
home = root / "home/Home.tsx"
s = home.read_text(encoding="utf-8")

if 'className="ns-global-search"' not in s:
    anchor = """        <a className="home-brand" href="#/" aria-label="OpenTempl home">
          <Wordmark size={21} />
        </a>
        <nav className="home-nav">"""
    replacement = """        <a className="home-brand" href="#/" aria-label="NEWS Studio home">
          <Wordmark size={21} />
        </a>
        <form className="ns-global-search" role="search" onSubmit={(e) => { e.preventDefault(); setQ(tq); setTplFilter('All'); wallRef.current?.scrollIntoView({ behavior: 'smooth' }); }}>
          <Icon name="search" size={18} />
          <input aria-label="Search templates, designs and news" value={tq} onChange={(e) => { setTq(e.target.value); setQ(e.target.value); }} placeholder="Search templates, designs, news…" autoComplete="off" />
          {tq ? <button type="button" aria-label="Clear search" onClick={() => { setTq(''); setQ(''); }}>×</button> : null}
        </form>
        <nav className="home-nav">"""
    if anchor not in s:
        raise SystemExit("Home header insertion point not found; no changes applied.")
    s = s.replace(anchor, replacement, 1)

s = s.replace("document.title = 'OpenTempl';", "document.title = 'NEWS Studio';", 1)
s = s.replace('aria-label="OpenTempl home"', 'aria-label="NEWS Studio home"')
s = s.replace("""          <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>
          <a href="#/generate">Generate</a>
          {DESKTOP_LINK ? <a href="/download">Desktop app</a> : null}
          <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>Your designs</button>""",
"""          <button onClick={() => document.getElementById('news-feed')?.scrollIntoView({ behavior: 'smooth' })}>Newsroom</button>
          <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>My designs</button>
          <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>""", 1)
s = s.replace("""            <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>
            <a href="#/generate">Generate</a>
            <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>Your designs</button>""",
"""            <button onClick={() => document.getElementById('news-feed')?.scrollIntoView({ behavior: 'smooth' })}>Newsroom</button>
            <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>My designs</button>
            <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>""", 1)

if "<NewsFeed />" in s:
    s = s.replace("<NewsFeed />", '<div id="news-feed"><NewsFeed query={tq} /></div>', 1)
elif "NewsFeed query={tq}" not in s:
    raise SystemExit("RSS NewsFeed component is missing before mobile workspace patch.")
s = s.replace('<section className="home-section" ref={wallRef}>', '<section className="home-section" id="template-library" ref={wallRef}>', 1)
s = s.replace("<h2>Your designs</h2>", "<h2>My designs</h2>", 1)
s = s.replace('placeholder="Search your designs"', 'placeholder="Filter your saved designs"', 1)
home.write_text(s, encoding="utf-8")

news = root / "home/NewsFeed.tsx"
if not news.exists():
    raise SystemExit("RSS NewsFeed source missing.")
n = news.read_text(encoding="utf-8")
n = n.replace("export function NewsFeed() {", "export function NewsFeed({ query = '' }: { query?: string }) {", 1)
if "const visibleItems" not in n:
    pattern = r"(?=\s+const makePoster = \(item: NewsItem\) => \{)"
    filtered = "            const visibleItems: NewsItem[] = items.filter((item) => !query.trim() || (item.title + ' ' + item.summary + ' ' + item.source).toLowerCase().includes(query.trim().toLowerCase()));\n"
    n, count = re.subn(pattern, filtered, n, count=1)
    if count != 1:
        raise SystemExit("NewsFeed search insertion point not found.")
n = n.replace("{items.map((item, i) =>", "{visibleItems.map((item, i) =>", 1)
n = n.replace("{loaded && !items.length && !error ?", "{loaded && !visibleItems.length && !error ?", 1)
n = n.replace("No stories found in this feed.", "No stories match this search in the selected feed.", 1)
news.write_text(n, encoding="utf-8")

css = root / "home/home.css"
c = css.read_text(encoding="utf-8")
if ".ns-global-search" not in c:
    c += """
/* NEWS Studio mobile workspace navigation and unified search */
.ns-global-search { display:flex; align-items:center; gap:9px; width:min(360px,32vw); min-width:180px; height:42px; padding:0 12px; border:1px solid var(--line); border-radius:12px; background:var(--paper-2); color:var(--ink-2); flex:none; }
.ns-global-search input { width:100%; min-width:0; border:0; outline:0; background:transparent; color:var(--ink); font:inherit; font-size:14px; }
.ns-global-search input::placeholder { color:var(--ink-3); }
.ns-global-search button { width:28px; height:28px; flex:none; border-radius:8px; background:var(--hover); font-size:20px; line-height:1; }
#news-feed, #your-designs, #template-library { scroll-margin-top:calc(var(--bar, 64px) + 16px); }
#news-feed { padding-top:20px; }
@media(max-width:900px) { .ns-global-search { width:min(330px,38vw); min-width:150px; } }
@media(max-width:720px) {
  .home-top { display:flex; flex-wrap:wrap; align-items:center; }
  .home-top .ns-global-search { order:4; display:flex; width:100%; max-width:none; min-width:0; height:44px; margin:4px 0 2px; }
  .home-top .home-nav { display:none; }
  .home-top .home-menu-btn { display:grid; }
  .home-top .home-sheet { z-index:30; max-height:min(65dvh,520px); overflow:auto; }
  .home main { padding-left:14px; padding-right:14px; }
  #news-feed, #your-designs, #template-library { scroll-margin-top:130px; }
}
@media(max-width:360px) { .home-top .ns-global-search { height:42px; } .ns-global-search input { font-size:13px; } }
"""
css.write_text(c, encoding="utf-8")

start = root / "start/Start.tsx"
t = start.read_text(encoding="utf-8")
t = t.replace("document.title = 'Start a design · OpenTempl';", "document.title = 'Start a design · NEWS Studio';")
t = t.replace('aria-label="OpenTempl home"', 'aria-label="NEWS Studio home"')
start.write_text(t, encoding="utf-8")


# Dedicated profile page with account details, saved designs and uploaded files.
profile_source = Path("scripts/profile_module.tsx")
if not profile_source.exists():
    raise SystemExit("NEWS Studio profile module source is missing.")
profile = root / "profile/Profile.tsx"
profile.parent.mkdir(parents=True, exist_ok=True)
profile.write_text(profile_source.read_text(encoding="utf-8"), encoding="utf-8")

app = root / "App.tsx"
body = app.read_text(encoding="utf-8")
if "import { Profile } from './profile/Profile';" not in body:
    body = "import { Profile } from './profile/Profile';\n" + body
if "if (path === '/profile') return <Profile />;" not in body:
    body = body.replace("  if (path === '/icons') return <IconSheet />;", "  if (path === '/profile') return <Profile />;\n  if (path === '/icons') return <IconSheet />;", 1)
body = body.replace('  return <Loading label="Laying out a fresh sheet" />;', '  return <div className="ns-opening-sheet" aria-live="polite">Opening your design…</div>;')
app.write_text(body, encoding="utf-8")

# Move sign-out into Profile; remove the floating bottom-right account control.
gate = root / "auth/AuthGate.tsx"
body = gate.read_text(encoding="utf-8")
body = re.sub(r"<button onClick=\{\(\)=>signOut\(auth\)\} title='Sign out'.*?</button>", "", body)
gate.write_text(body, encoding="utf-8")

home = root / "home/Home.tsx"
body = home.read_text(encoding="utf-8")
if 'href="#/profile"' not in body:
    body = body.replace('<button className="btn btn-outline home-open" onClick={openPicked}>', '<a className="btn btn-outline" href="#/profile">My Profile</a>\n        <button className="btn btn-outline home-open" onClick={openPicked}>', 1)
    body = body.replace('<button onClick={openPicked}>Open a file</button>', '<button onClick={openPicked}>Open a file</button>\n            <a href="#/profile">My Profile</a>', 1)
home.write_text(body, encoding="utf-8")

css = root / "home/home.css"
body = css.read_text(encoding="utf-8")
body += """
.ns-opening-sheet{height:100dvh;display:grid;place-items:center;background:var(--paper);color:var(--ink-2);font:500 13px system-ui,sans-serif}
.ns-profile{height:100dvh;overflow:auto;background:var(--paper);color:var(--ink);padding-bottom:env(safe-area-inset-bottom)}
.ns-profile-head{min-height:60px;position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:16px;padding:10px 16px;background:var(--paper);border-bottom:1px solid var(--line)}
.ns-profile-head>b{font-size:16px}.ns-profile-head button{border:1px solid var(--line);background:var(--paper-2);border-radius:10px;padding:9px 13px;color:var(--ink);font:600 13px system-ui}.ns-profile-head .ns-profile-signout{margin-left:auto;color:#b42318}
.ns-profile-main{width:min(100% - 32px,920px);margin:24px auto 48px}.ns-profile-card{display:flex;align-items:center;gap:16px;padding:22px;border:1px solid var(--line);border-radius:18px;background:var(--paper-2)}
.ns-profile-avatar{width:68px;height:68px;flex:none;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:#dbeafe;color:#1d4ed8;font-size:25px;font-weight:800}.ns-profile-avatar img{width:100%;height:100%;object-fit:cover}
.ns-profile-card h1{font-size:22px;margin:0 0 4px}.ns-profile-card p{margin:0 0 5px;color:var(--ink-2);overflow-wrap:anywhere}.ns-profile-card small,.ns-profile-file small,.ns-profile-design small{display:block;color:var(--ink-3);font-size:12px;margin-top:4px;overflow-wrap:anywhere}
.ns-profile-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}.ns-profile-stats>div{padding:15px;border:1px solid var(--line);border-radius:14px;background:var(--paper-2)}.ns-profile-stats b{display:block;font-size:21px}.ns-profile-stats span{display:block;color:var(--ink-2);font-size:12px;margin-top:4px}
.ns-profile-tabs{display:flex;gap:8px;overflow:auto;border-bottom:1px solid var(--line);margin-top:20px}.ns-profile-tabs button{flex:none;padding:12px 14px;background:transparent;color:var(--ink-2);border-bottom:2px solid transparent;font:600 13px system-ui}.ns-profile-tabs button.active{color:var(--ink);border-color:var(--accent,#2563eb)}
.ns-profile-list{padding:20px 0}.ns-profile-list h2{font-size:18px;margin:0 0 14px}.ns-profile-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}.ns-profile-design{min-width:0;text-align:left;padding:10px;border:1px solid var(--line);border-radius:13px;background:var(--paper-2);color:var(--ink)}.ns-profile-preview{height:145px;display:grid;place-items:center;background:var(--paper);border-radius:9px;overflow:hidden;margin-bottom:9px}.ns-profile-preview img{width:100%;height:100%;object-fit:contain}.ns-profile-design>b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}
.ns-profile-files{display:grid;gap:9px}.ns-profile-file{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid var(--line);border-radius:12px;background:var(--paper-2);min-width:0}.ns-profile-file-icon{width:40px;height:40px;flex:none;display:grid;place-items:center;border-radius:9px;background:var(--paper);font-size:22px}.ns-profile-file>div{min-width:0}.ns-profile-file b{display:block;overflow-wrap:anywhere;font-size:13px}
.ns-profile-account{display:grid;gap:13px;max-width:520px}.ns-profile-account label{display:grid;gap:6px;font-size:12px;font-weight:650}.ns-profile-account input{width:100%;height:44px;padding:0 12px;border:1px solid var(--line);border-radius:10px;background:var(--paper-2);color:var(--ink);font:14px system-ui}.ns-profile-save{min-height:44px;padding:0 16px;border-radius:10px;background:var(--accent,#2563eb);color:white;font-weight:700}.ns-profile-save:disabled{opacity:.55}.ns-profile-empty,.ns-profile-foot{color:var(--ink-3);font-size:13px}.ns-profile-foot{margin-top:28px;padding:14px 0;border-top:1px solid var(--line)}
@media(max-width:520px){.ns-profile-main{width:calc(100% - 24px);margin-top:14px}.ns-profile-card{padding:15px;gap:12px}.ns-profile-avatar{width:54px;height:54px}.ns-profile-card h1{font-size:18px}.ns-profile-stats{gap:7px}.ns-profile-stats>div{padding:11px 9px}.ns-profile-stats b{font-size:18px}.ns-profile-stats span{font-size:10px}.ns-profile-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.ns-profile-preview{height:120px}.ns-profile-tabs button{padding:11px 10px;font-size:12px}}
"""
css.write_text(body, encoding="utf-8")

print("NEWS Studio workspace and scoped newsroom search patched.")
