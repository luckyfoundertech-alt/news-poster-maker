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
    pattern = r"(\s+const makePoster = \(item: NewsItem\) => \{)"
    filtered = "            const visibleItems: NewsItem[] = items.filter((item) => !query.trim() || (item.title + ' ' + item.summary + ' ' + item.source).toLowerCase().includes(query.trim().toLowerCase()));\n"
    n, count = re.subn(pattern, filtered + r"\1", n, count=1)
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

print("NEWS Studio workspace and scoped newsroom search patched.")
