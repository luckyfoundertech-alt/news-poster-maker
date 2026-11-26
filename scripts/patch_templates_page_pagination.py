from pathlib import Path
p=Path("opentempl/apps/editor/src/home/TemplatesPage.tsx")
s=p.read_text(encoding="utf-8")
old_categories = "const quickCategories = ['All','Breaking News','Editorial','Social Stories','Sports','Business','Infographics','Quotes','YouTube Banners'];"
new_categories = "const quickCategories = ['All','Indian News','State & District','Politics & Public','Cricket & Sports','Business & Education','Indian Festivals','National & Culture','Breaking News','Editorial','Social Stories','Sports','Business','Infographics','Quotes','YouTube Banners'];"
if old_categories in s:
    s = s.replace(old_categories, new_categories, 1)
elif new_categories not in s:
    raise SystemExit("Template category filter list missing.")

if "const [limit,setLimit]=useState(80);" not in s:
    marker=" const [loading,setLoading]=useState(true);"
    if marker not in s: raise SystemExit("TemplatesPage loading state missing")
    s=s.replace(marker,marker+"\n const [limit,setLimit]=useState(80);",1)
if "useEffect(()=>setLimit(80),[query,category]);" not in s:
    marker=" },[index,query,category,categories]);"
    if marker not in s: raise SystemExit("TemplatesPage search memo end missing")
    s=s.replace(marker,marker+"\n useEffect(()=>setLimit(80),[query,category]);",1)
s=s.replace("{visible.map(t=><button className='ns-template-card'", "{visible.slice(0,limit).map(t=><button className='ns-template-card'",1)
marker="</div>:<div className='ns-project-empty'>"
addition="""{visible.length>limit?<button className='ns-template-load-more' onClick={()=>setLimit(n=>n+80)}>Load 80 more · showing {Math.min(limit,visible.length)} of {visible.length}</button>:null}</div>:<div className='ns-project-empty'>"""
if marker not in s: raise SystemExit("TemplatesPage grid close marker missing")
s=s.replace(marker,addition,1)
p.write_text(s,encoding="utf-8")
css=Path("opentempl/apps/editor/src/home/home.css")
c=css.read_text(encoding="utf-8")
if ".ns-templates-page .ns-template-load-more" not in c:
    c+="\n.ns-templates-page .ns-template-load-more{grid-column:1/-1;min-height:44px;border:1px solid var(--line);border-radius:12px;background:var(--paper-2);color:var(--ink);font-weight:700;font-size:13px}\n"
    css.write_text(c,encoding="utf-8")
print("Templates route now searches all indexed templates but renders only 80 cards per batch.")
