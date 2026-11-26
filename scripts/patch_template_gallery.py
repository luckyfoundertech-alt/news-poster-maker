from pathlib import Path
import re

home = Path("opentempl/apps/editor/src/home/Home.tsx")
if not home.exists():
    raise SystemExit("OpenTempl Home.tsx missing; cannot optimize the 3000-template gallery.")
s = home.read_text(encoding="utf-8")
if "const [tplLimit, setTplLimit] = useState(80);" not in s:
    marker = "  const [index, setIndex] = useState<TemplateIndex | null>(null);"
    if marker not in s: raise SystemExit("Template index state marker missing.")
    s = s.replace(marker, marker + "\n  const [tplLimit, setTplLimit] = useState(80);", 1)
if "setTplLimit(80), [tplFilter, query]" not in s:
    marker = "  const query = tq.trim().toLowerCase();"
    if marker not in s: raise SystemExit("Template search query marker missing.")
    s = s.replace(marker, marker + "\n  useEffect(() => setTplLimit(80), [tplFilter, query]);", 1)
s = s.replace('placeholder="A gig poster, a menu"', 'placeholder="Search Hindi or English templates…"')
old = '<Masonry items={tplFilter === \'classics\' ? [] : packTpls} vibes={index?.vibes ?? {}} />'
new = """<Masonry items={tplFilter === 'classics' ? [] : packTpls.slice(0, tplLimit)} vibes={index?.vibes ?? {}} />
          {tplFilter !== 'classics' && packTpls.length > tplLimit ? (
            <div className="ns-template-load-more">
              <span>Showing {Math.min(tplLimit, packTpls.length)} of {packTpls.length} matching templates</span>
              <button className="btn btn-outline" onClick={() => setTplLimit((n) => n + 80)}>Load 80 more templates</button>
            </div>
          ) : null}"""
if old in s:
    s=s.replace(old,new,1)
elif "packTpls.slice(0, tplLimit)" not in s:
    raise SystemExit("Template Masonry render point missing.")
home.write_text(s, encoding="utf-8")

css = Path("opentempl/apps/editor/src/home/home.css")
if css.exists():
    c=css.read_text(encoding="utf-8")
    if ".ns-template-load-more" not in c:
        c += """
.ns-template-load-more{display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;padding:22px 8px;color:var(--ink-2);font-size:12px}
.ns-template-load-more .btn{min-height:42px;padding:0 18px}
.vibe-chips{display:flex;flex-wrap:nowrap;overflow-x:auto;max-width:100%;gap:8px;padding:4px 2px 12px;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
.vibe-chips .chip{flex:none;white-space:nowrap}
"""
        css.write_text(c,encoding="utf-8")
print("Template gallery now searches the full index but renders 80 cards at a time to protect Android memory and scrolling.")
