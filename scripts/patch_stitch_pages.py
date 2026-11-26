from pathlib import Path
import re

root = Path("opentempl/apps/editor/src")
home = root / "home/Home.tsx"
s = home.read_text(encoding="utf-8")

# Account identity in the dashboard header.
if "import { auth } from '../auth/firebase';" not in s:
    s = s.replace("import { Wordmark } from '../ui/Logo';", "import { Wordmark } from '../ui/Logo';\nimport { auth } from '../auth/firebase';", 1)
# Strip all AI generation concepts from the home module; the app is intentionally non-AI.
s = s.replace("import { loadLooks, sampleUrl, type Look } from '../generate/looks';\n", "")
# Remove unused artwork generator from the retired AI/looks dashboard.
s = re.sub(r"// Drawn in a 600 x 640 design space\..*?// The template wall:", "// The template wall:", s, flags=re.S)
s = s.replace("  const [looks, setLooks] = useState<Look[]>([]);\n", "")
s = s.replace("    loadLooks().then(setLooks);\n", "")
s = re.sub(r"\s*\{looks\.length \? \(.*?\n\s*\) : null\}\n", "\n", s, flags=re.S)
# Remove the hero canvas artwork and replace the old desktop-first hero with a compact greeting panel.
s = re.sub(r"\s*<section className=\"hero\">.*?</section>\s*<main>", "\n      <main>", s, flags=re.S)
# Remove obsolete AI/looks imports and source strings from the page.
s = s.replace("import { Credit, GitHubLink, SHOW_SOURCE } from '../ui/Credit';\n", "")
s = s.replace("import { REPO_URL } from '../links';\n", "")
s = s.replace("import { Subscribe } from '../ui/Subscribe';\n", "")
s = s.replace("import { SHOW_USAGE_FROM, useUsage } from '../stats/client';\n", "")
s = s.replace("  const usage = useUsage();\n", "")
s = s.replace("const DESKTOP_LINK = !window.tavlaDesktop;", "const DESKTOP_LINK = false;")
s = s.replace("document.title = 'OpenTempl';", "document.title = 'NEWS Studio';")
# Hide old footer and desktop drop copy; keep local file import functionality via the open-file action.
s = re.sub(r"\s*<footer className=\"home-foot\">.*?</footer>", "", s, flags=re.S)
s = s.replace("Drop an .opentempl file, PDF or PowerPoint file to open it", "Drop a NEWS Studio design, PDF or PowerPoint file to open it")
# Remove desktop/upstream controls from the header; add dedicated account actions.
s = s.replace("        <span className=\"home-gh\">\n          <GitHubLink />\n        </span>\n", "")
s = s.replace("          <GitHubLink label />\n", "")
s = s.replace("          <Credit />\n", "")
s = s.replace("          <Credit />\n", "")
s = s.replace("          <a href=\"#/generate\">Generate</a>\n", "")
s = s.replace("            <a href=\"#/generate\">Generate</a>\n", "")
s = s.replace("          <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>", "          <a href=\"#/templates\">Templates</a>", 1)
s = s.replace("          <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>Your designs</button>", "          <a href=\"#/projects\">My Projects</a>", 1)
s = s.replace("            <button onClick={() => wallRef.current?.scrollIntoView({ behavior: 'smooth' })}>Templates</button>", "            <a href=\"#/templates\">Templates</a>", 1)
s = s.replace("            <button onClick={() => document.getElementById('your-designs')?.scrollIntoView({ behavior: 'smooth' })}>Your designs</button>", "            <a href=\"#/projects\">My Projects</a>", 1)
if 'href="#/newsroom"' not in s:
    s=s.replace('<nav className="home-nav">','<nav className="home-nav"><a href="#/newsroom">Newsroom</a>',1)
    s=s.replace('<nav className="home-sheet" onClick={() => setMenu(false)}>','<nav className="home-sheet" onClick={() => setMenu(false)}><a href="#/newsroom">Newsroom</a>',1)
# Replace hero remnants in header actions with account profile and user avatar.
s = s.replace('        <a className="btn btn-primary" href="#/start">\n          Start designing\n        </a>', """        <a className="btn btn-primary" href="#/start">Create design</a>
        <a className="ns-account-avatar" href="#/profile" aria-label="Open profile">
          {auth.currentUser?.photoURL ? <img src={auth.currentUser.photoURL} alt="" /> : <span>{(auth.currentUser?.displayName || auth.currentUser?.email || 'N').slice(0,1).toUpperCase()}</span>}
        </a>""", 1)
# Add dashboard section before existing designs section.
needle = '<section className="home-section" id="your-designs">'
dashboard = """<section className="ns-dashboard">
          <div className="ns-welcome">
            <div><p className="ns-eyebrow">YOUR CREATIVE WORKSPACE</p><h1>Good {new Date().getHours()<12?'morning':new Date().getHours()<18?'afternoon':'evening'}, {(auth.currentUser?.displayName || 'Creator').split(' ')[0]} <span>✦</span></h1><p>What will you design today?</p></div>
            <a className="ns-pro-badge" href="#/profile">NEWS STUDIO</a>
          </div>
          <form className="ns-main-search" role="search" onSubmit={(e)=>{e.preventDefault();setQ(tq);setTplFilter('All');wallRef.current?.scrollIntoView({behavior:'smooth'});}}>
            <Icon name="search" size={19}/><input value={tq} onChange={e=>{setTq(e.target.value);setQ(e.target.value);}} placeholder="Search templates and your designs…" aria-label="Search templates and designs"/>{tq?<button type="button" onClick={()=>{setTq('');setQ('');}}>×</button>:null}
          </form>
          <div className="ns-section-label"><b>Quick Create</b><a href="#/start">Custom dimensions <Icon name="forward" size={14}/></a></div>
          <div className="ns-quick-grid">
            <button onClick={()=>navigate('/new?format=a3-poster')}><span className="ns-quick-icon blue"><Icon name="sparkle"/></span><b>Breaking Banner</b></button>
            <button onClick={()=>navigate('/new?format=story')}><span className="ns-quick-icon violet"><Icon name="page"/></span><b>News Story</b></button>
            <button onClick={()=>navigate('/new?format=ig-post')}><span className="ns-quick-icon cyan"><Icon name="square"/></span><b>Square Post</b></button>
            <button onClick={()=>navigate('/new?format=ig-post')}><span className="ns-quick-icon rose"><Icon name="text"/></span><b>Quote Post</b></button>
            <button onClick={()=>navigate('/new?format=a4')}><span className="ns-quick-icon amber"><Icon name="star"/></span><b>Fact Check</b></button>
          </div>
          <div className="ns-feature-strip">
            <a href="#/start"><span className="ns-feature-icon"><Icon name="palette"/></span><span><b>Brand & design tools</b><small>Fonts, colours, layers and layouts</small></span><Icon name="forward"/></a>
            <a href="#/projects"><span className="ns-feature-icon"><Icon name="folder"/></span><span><b>My Projects</b><small>{designs?.length ?? 0} saved designs in your workspace</small></span><Icon name="forward"/></a>
          </div>
        </section>
        """
if "className=\"ns-dashboard\"" not in s:
    if needle not in s: raise SystemExit("Home designs section anchor missing")
    s=s.replace(needle,dashboard+needle,1)
# Update recent designs section and template section headings/actions.
s=s.replace("<h2>Your designs</h2>", "<h2>Recent designs</h2>",1)
s=s.replace('<h2>Templates</h2>', '<h2>Trending editorial templates</h2>',1)
s=s.replace("Search your designs","Search recent designs")
# Make view all navigate to the full project library.
s=s.replace('<h2>Recent designs</h2>', '<div><h2>Recent designs</h2><p className=\"muted\">Pick up where you left off</p></div><a className=\"ns-see-all\" href=\"#/projects\">See all <Icon name=\"chevron-right\" size={14}/></a>',1)
# Add bottom app navigation.
bottom = """<nav className="ns-bottom-nav" aria-label="Main navigation">
        <a className="active" href="#/"><Icon name="home"/><span>Home</span></a>
        <a href="#/templates"><Icon name="grid"/><span>Templates</span></a>
        <a className="ns-bottom-create" href="#/start" aria-label="Create design"><Icon name="plus"/></a>
        <a href="#/newsroom"><Icon name="page"/><span>Newsroom</span></a>
        <a href="#/profile"><Icon name="users"/><span>Profile</span></a>
      </nav>
      """
if "className=\"ns-bottom-nav\"" not in s:
    s=s.replace("      {drop ? (", "      "+bottom+"{drop ? (",1)
home.write_text(s, encoding="utf-8")

# A dedicated Projects library based on the app's real local design and upload stores.
projects = root / "home/Projects.tsx"
projects.write_text("""import { useEffect, useMemo, useState } from 'react';
import { navigate } from '../App';
import { auth } from '../auth/firebase';
import { getThumb, listDesigns, onDesignsChange, type DesignEntry } from '../io/designs';
import { listUploads } from '../io/uploads';
import { Wordmark } from '../ui/Logo';
import { Icon } from '../ui/icons';
import './home.css';

type UploadEntry = Awaited<ReturnType<typeof listUploads>>[number];
export function Projects() {
 const [designs,setDesigns]=useState<DesignEntry[]>([]);
 const [uploads,setUploads]=useState<UploadEntry[]>([]);
 const [thumbs,setThumbs]=useState<Record<string,string>>({});
 const [query,setQuery]=useState('');
 const [filter,setFilter]=useState('All');
 const [view,setView]=useState<'grid'|'list'>('grid');
 useEffect(()=>{
  let live=true;
  const refresh=async()=>{
   const [d,u]=await Promise.all([listDesigns(),listUploads()]);
   if(!live)return;
   setDesigns(d);setUploads(u);
   const pairs=await Promise.all(d.map(async x=>{const b=await getThumb(x.id);return [x.id,b?URL.createObjectURL(b):''] as const;}));
   if(live)setThumbs(Object.fromEntries(pairs.filter(x=>x[1])));
   else pairs.forEach(x=>x[1]&&URL.revokeObjectURL(x[1]));
  };
  void refresh();const off=onDesignsChange(()=>void refresh());
  return()=>{live=false;off();Object.values(thumbs).forEach(URL.revokeObjectURL);};
 },[]);
 const visible=useMemo(()=>designs.filter(d=>(!query||d.title.toLowerCase().includes(query.toLowerCase()))&&(filter==='All'||(filter==='Square'&&d.width===d.height)||(filter==='Story'&&d.height>d.width)||(filter==='Landscape'&&d.width>d.height))),[designs,query,filter]);
 return <main className='ns-projects'>
  <header className='ns-projects-head'><button className='btn btn-outline' onClick={()=>navigate('/')}>← Home</button><Wordmark size={20}/><span className='grow'/><a className='ns-account-avatar' href='#/profile'>{auth.currentUser?.photoURL?<img src={auth.currentUser.photoURL} alt=''/>:(auth.currentUser?.displayName||'N').slice(0,1)}</a></header>
  <section className='ns-projects-intro'><p className='ns-eyebrow'>YOUR WORKSPACE</p><h1>My Projects</h1><p>All your saved designs and uploaded files, synced to your account.</p></section>
  <section className='ns-project-stats'><div><b>{designs.length}</b><span>Designs</span></div><div><b>{uploads.length}</b><span>Uploads</span></div><div><b>{designs.filter(d=>d.starred).length}</b><span>Starred</span></div></section>
  <div className='ns-project-tools'><div className='ns-main-search'><Icon name='search'/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder='Search your projects…'/></div><div className='ns-project-filters'>{['All','Square','Story','Landscape'].map(x=><button className={filter===x?'active':''} onClick={()=>setFilter(x)} key={x}>{x}</button>)}</div><div className='ns-view-toggle'><button className={view==='grid'?'active':''} onClick={()=>setView('grid')} aria-label='Grid view'><Icon name='grid'/></button><button className={view==='list'?'active':''} onClick={()=>setView('list')} aria-label='List view'><Icon name='list'/></button></div></div>
  {visible.length?<div className={view==='grid'?'ns-project-grid':'ns-project-list'}>{visible.map(d=><button className='ns-project-card' key={d.id} onClick={()=>navigate('/d/'+d.id)}><div className='ns-project-thumb'>{thumbs[d.id]?<img src={thumbs[d.id]} alt=''/>:<span><Wordmark size={13}/></span>}</div><div className='ns-project-meta'><b>{d.title}</b><small>{d.width} × {d.height} · {d.pages} pages</small></div></button>)}</div>:<div className='ns-project-empty'><Icon name='folder-open' size={32}/><b>No projects found</b><p>Create a new design or change your search/filter.</p><button className='btn btn-primary' onClick={()=>navigate('/start')}>Create design</button></div>}
  <nav className='ns-bottom-nav' aria-label='Main navigation'><a href='#/'><Icon name='home'/><span>Home</span></a><a href='#/templates'><Icon name='grid'/><span>Templates</span></a><a className='ns-bottom-create' href='#/start'><Icon name='plus'/></a><a href='#/newsroom'><Icon name='newspaper'/><span>Newsroom</span></a><a href='#/profile'><Icon name='user'/><span>Profile</span></a></nav>
 </main>;
}
""", encoding="utf-8")

# A separate Templates route uses the real searchable template index and existing editor launch action.
templates = root / "home/TemplatesPage.tsx"
templates.write_text("""import { useEffect, useMemo, useState } from 'react';
import { navigate } from '../App';
import { auth } from '../auth/firebase';
import { loadTemplateIndex, thumbUrl, blended, byScore, type TemplateEntry, type TemplateIndex } from '../templates/packs';
import { TEMPLATES } from '../templates';
import { TemplatePreview } from '../templates/Preview';
import { Wordmark } from '../ui/Logo';
import { Icon } from '../ui/icons';
import './home.css';

const quickCategories = ['All','Breaking News','Editorial','Social Stories','Sports','Business','Infographics','Quotes','YouTube Banners'];
export function TemplatesPage(){
 const [index,setIndex]=useState<TemplateIndex|null>(null);
 const [query,setQuery]=useState('');
 const [category,setCategory]=useState('All');
 const [loading,setLoading]=useState(true);
 useEffect(()=>{let live=true;loadTemplateIndex().then(v=>{if(live){setIndex(v);setLoading(false);}});return()=>{live=false;};},[]);
 const categories=useMemo(()=>index?quickCategories.map(name=>({name,ids:index.templates.filter(t=>name==='All'||(t.category+' '+t.vibe+' '+t.tags.join(' ')).toLowerCase().includes(name.toLowerCase().replace(' news','').replace(' stories',''))).map(t=>t.id)})):[],[index]);
 const visible=useMemo(()=>{
  if(!index)return [];
  const q=query.trim().toLowerCase();
  const ids=categories.find(c=>c.name===category)?.ids;
  const list=index.templates.filter(t=>(!ids||category==='All'||ids.includes(t.id))&&(!q||[t.name,t.category,t.vibe,...t.tags].join(' ').toLowerCase().includes(q)));
  return category==='All'?blended(list):byScore(list);
 },[index,query,category,categories]);
 return <main className='ns-templates-page'>
  <header className='ns-projects-head'><button className='btn btn-outline' onClick={()=>navigate('/')}>← Home</button><Wordmark size={20}/><span className='grow'/><a className='ns-account-avatar' href='#/profile'>{auth.currentUser?.photoURL?<img src={auth.currentUser.photoURL} alt=''/>:(auth.currentUser?.displayName||auth.currentUser?.email||'N').slice(0,1).toUpperCase()}</a></header>
  <section className='ns-projects-intro'><p className='ns-eyebrow'>DESIGN LIBRARY</p><h1>Templates</h1><p>Choose a ready-made layout and make every element your own.</p></section>
  <div className='ns-template-search ns-main-search'><Icon name='search'/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder='Search news, sports, business, quotes…' aria-label='Search templates'/>{query?<button onClick={()=>setQuery('')}>×</button>:null}</div>
  <div className='ns-template-categories'>{quickCategories.map(c=><button key={c} className={category===c?'active':''} onClick={()=>setCategory(c)}>{c}</button>)}</div>
  <section className='ns-template-section'><div className='ns-template-section-head'><div><h2>{category==='All'?'Trending layouts':category}</h2><p>{visible.length} templates available</p></div><span>NEWS Studio Library</span></div>
   {loading?<div className='ns-template-skeleton' aria-label='Loading templates'><i/><i/><i/><i/></div>:visible.length?<div className='ns-template-grid'>{visible.map(t=><button className='ns-template-card' key={t.id} onClick={()=>navigate('/new?template='+encodeURIComponent(t.id))}><div className='ns-template-thumb'><img src={thumbUrl(t.id)} alt='' loading='lazy' onError={e=>{(e.currentTarget as HTMLImageElement).style.opacity='0';}}/></div><div className='ns-template-meta'><b>{t.name}</b><small>{t.category} · {t.width}×{t.height}</small></div></button>)}</div>:<div className='ns-project-empty'><Icon name='search'/><b>No templates found</b><p>Try a different search or category.</p></div>}
  </section>
  <nav className='ns-bottom-nav' aria-label='Main navigation'><a href='#/'><Icon name='home'/><span>Home</span></a><a className='active' href='#/templates'><Icon name='grid'/><span>Templates</span></a><a className='ns-bottom-create' href='#/start'><Icon name='plus'/></a><a href='#/newsroom'><Icon name='page'/><span>Newsroom</span></a><a href='#/profile'><Icon name='users'/><span>Profile</span></a></nav>
 </main>;
}
""",encoding="utf-8")

# Add routes to the app shell, retaining existing editor and template builder.
app = root / "App.tsx"
a = app.read_text(encoding="utf-8")
if "import { Projects } from './home/Projects';" not in a:
    a=a.replace("import { Home } from './home/Home';","import { Home } from './home/Home';\nimport { Projects } from './home/Projects';\nimport { TemplatesPage } from './home/TemplatesPage';",1)
if "if (path === '/projects') return <Projects />;" not in a:
    a=a.replace("  if (path === '/newsroom') return <Newsroom />;","  if (path === '/newsroom') return <Newsroom />;\n  if (path === '/projects') return <Projects />;\n  if (path === '/templates') return <TemplatesPage />;",1)
app.write_text(a,encoding="utf-8")

# Stitch-inspired responsive visual system. Use actual NEWS Studio feature data, not mock modules.
css = root / "home/home.css"
c = css.read_text(encoding="utf-8")
c += """
/* NEWS Studio Stitch-inspired Android workspace */
.ns-dashboard{width:min(100%,1120px);margin:0 auto 20px;padding:12px 0 4px}
.ns-welcome{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:4px 0 18px}
.ns-eyebrow{font-size:10px;font-weight:800;letter-spacing:.14em;color:#64748b;margin:0 0 8px}
.ns-welcome h1,.ns-projects-intro h1{font-size:clamp(25px,5vw,34px);letter-spacing:-.045em;line-height:1.12;margin:0;color:var(--ink)}
.ns-welcome h1 span{color:#2563eb}.ns-welcome p:last-child,.ns-projects-intro>p:last-child{font-size:13px;color:var(--ink-2);margin:6px 0 0}
.ns-pro-badge{flex:none;padding:8px 11px;border-radius:99px;background:#eff6ff;color:#1d4ed8;border:1px solid #dbeafe;font-size:10px;font-weight:800;letter-spacing:.08em}
.ns-main-search{display:flex;align-items:center;gap:10px;min-height:48px;padding:0 14px;border:1px solid var(--line);border-radius:14px;background:var(--paper-2);color:var(--ink-2);margin:0 0 22px}
.ns-main-search input{width:100%;min-width:0;border:0;outline:0;background:transparent;color:var(--ink);font:14px system-ui}.ns-main-search input::placeholder{color:var(--ink-3)}.ns-main-search button{font-size:20px;color:var(--ink-2)}
.ns-section-label{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 13px;font-size:14px}.ns-section-label>a,.ns-see-all{display:flex;align-items:center;gap:3px;color:#2563eb;font-size:12px;font-weight:700;text-decoration:none}
.ns-quick-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-bottom:20px}
.ns-quick-grid>button{display:flex;align-items:center;flex-direction:column;gap:8px;min-width:0;padding:0 2px;background:transparent;color:var(--ink);font-size:11px}
.ns-quick-grid>button b{font-size:11px;text-align:center;line-height:1.25;font-weight:650}
.ns-quick-icon{width:52px;height:52px;display:grid;place-items:center;border-radius:50%;color:white;box-shadow:0 5px 14px #1e293b22}.ns-quick-icon svg{width:21px;height:21px}
.ns-quick-icon.blue{background:linear-gradient(145deg,#168bff,#1749dc)}.ns-quick-icon.violet{background:linear-gradient(145deg,#6366f1,#4338ca)}.ns-quick-icon.cyan{background:linear-gradient(145deg,#38bdf8,#0284c7)}.ns-quick-icon.rose{background:linear-gradient(145deg,#f43f5e,#be123c)}.ns-quick-icon.amber{background:linear-gradient(145deg,#f59e0b,#d97706)}
.ns-feature-strip{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:22px}.ns-feature-strip>a{min-width:0;display:flex;align-items:center;gap:10px;padding:12px;border:1px solid var(--line);border-radius:14px;background:var(--paper-2);color:var(--ink);text-decoration:none}.ns-feature-strip>a>span:nth-child(2){min-width:0;flex:1}.ns-feature-strip b,.ns-feature-strip small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ns-feature-strip b{font-size:12px}.ns-feature-strip small{font-size:10px;color:var(--ink-3);margin-top:4px}.ns-feature-icon{width:38px;height:38px;flex:none;display:grid;place-items:center;border-radius:10px;background:#eef2ff;color:#4f46e5}
.ns-account-avatar{width:38px;height:38px;flex:none;display:grid;place-items:center;border-radius:50%;overflow:hidden;background:#dbeafe;color:#1d4ed8;font-weight:800;text-decoration:none}.ns-account-avatar img{width:100%;height:100%;object-fit:cover}
.ns-bottom-nav{position:fixed;z-index:80;left:0;right:0;bottom:0;min-height:66px;padding:7px max(12px,env(safe-area-inset-right)) calc(7px + env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left));display:grid;grid-template-columns:repeat(5,minmax(0,1fr));align-items:center;background:color-mix(in srgb,var(--paper) 94%,transparent);backdrop-filter:blur(18px);border-top:1px solid var(--line)}
.ns-bottom-nav>a{display:flex;align-items:center;justify-content:center;flex-direction:column;gap:3px;min-height:48px;color:var(--ink-3);font-size:10px;text-decoration:none}.ns-bottom-nav>a svg{width:19px;height:19px}.ns-bottom-nav>a.active{color:#2563eb;font-weight:750}.ns-bottom-nav>a.ns-bottom-create{width:52px;height:52px;min-height:52px;justify-self:center;align-self:start;margin-top:-22px;border-radius:50%;background:linear-gradient(145deg,#3b82f6,#4338ca);color:#fff;box-shadow:0 6px 18px #2563eb55}.ns-bottom-nav>a.ns-bottom-create svg{width:25px;height:25px}
.home{padding-bottom:calc(82px + env(safe-area-inset-bottom))}.home main{padding-top:8px}.home-top{position:sticky;top:0;z-index:70;background:var(--paper);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}.home-top .home-brand{min-width:0}.home-top .home-nav{gap:15px}.home-top .home-open{display:none}
.home-section{margin-top:24px}.home-section-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.home-section-head h2{font-size:18px;letter-spacing:-.025em;margin:0}.home-section-head .muted{font-size:12px;margin:4px 0 0}.home-section-head .ns-see-all{flex:none}
.ns-projects{height:100dvh;overflow:auto;background:var(--paper);color:var(--ink);padding:0 0 calc(86px + env(safe-area-inset-bottom))}
.ns-projects-head{height:60px;position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:12px;padding:8px 16px;background:var(--paper);border-bottom:1px solid var(--line)}
.ns-projects-intro,.ns-project-stats,.ns-project-tools,.ns-project-grid,.ns-project-list,.ns-project-empty{width:min(100% - 32px,1120px);margin-left:auto;margin-right:auto}
.ns-projects-intro{padding:28px 0 12px}.ns-projects-intro h1{font-size:32px}
.ns-project-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}.ns-project-stats>div{padding:13px;border:1px solid var(--line);border-radius:13px;background:var(--paper-2)}.ns-project-stats b{display:block;font-size:21px}.ns-project-stats span{font-size:11px;color:var(--ink-3)}
.ns-project-tools{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:20px;margin-bottom:14px}.ns-project-tools .ns-main-search{flex:1;min-width:170px;margin:0}.ns-project-filters{display:flex;gap:5px;overflow:auto}.ns-project-filters button,.ns-view-toggle button{padding:8px 10px;border:1px solid var(--line);border-radius:9px;background:var(--paper-2);color:var(--ink-2);font-size:11px}.ns-project-filters button.active,.ns-view-toggle button.active{background:#eff6ff;color:#1d4ed8;border-color:#bfdbfe}.ns-view-toggle{display:flex;gap:4px}
.ns-project-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:13px}.ns-project-card{min-width:0;text-align:left;overflow:hidden;border:1px solid var(--line);border-radius:13px;background:var(--paper-2);color:var(--ink)}.ns-project-thumb{aspect-ratio:4/3;display:grid;place-items:center;overflow:hidden;background:var(--paper)}.ns-project-thumb img{width:100%;height:100%;object-fit:contain}.ns-project-meta{padding:10px}.ns-project-meta b,.ns-project-meta small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ns-project-meta b{font-size:12px}.ns-project-meta small{font-size:10px;color:var(--ink-3);margin-top:4px}
.ns-project-list{display:grid;gap:8px}.ns-project-list .ns-project-card{display:flex;align-items:center}.ns-project-list .ns-project-thumb{width:90px;aspect-ratio:1.2;flex:none}.ns-project-list .ns-project-meta{flex:1}
.ns-project-empty{display:grid;justify-items:center;gap:9px;padding:48px 12px;color:var(--ink-2);text-align:center}.ns-project-empty p{font-size:12px;color:var(--ink-3);margin:0}
@media(max-width:720px){.home{height:100dvh;min-height:100dvh;overflow:auto}.home-top{padding:calc(7px + env(safe-area-inset-top)) 13px 8px;gap:8px;flex-wrap:nowrap}.home-top .home-nav,.home-top .home-open{display:none}.home-top .home-brand{flex:1}.home-top .btn-primary{padding:9px 11px;font-size:11px}.home-top .home-menu-btn{display:none}.home-top .ns-account-avatar{width:36px;height:36px}.home main{padding:8px 14px 20px}.ns-dashboard{padding-top:12px}.ns-quick-grid{gap:5px}.ns-quick-icon{width:48px;height:48px}.ns-quick-grid>button b{font-size:10px}.ns-feature-strip{gap:8px}.ns-feature-strip>a{padding:9px}.ns-feature-icon{width:32px;height:32px}.home-section{margin-top:25px}.design-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.masonry{grid-template-columns:repeat(2,minmax(0,1fr))!important}.ns-project-tools{align-items:stretch}.ns-project-tools .ns-main-search{flex-basis:100%}.ns-project-filters{flex:1}.ns-view-toggle{margin-left:auto}}
@media(max-width:370px){.ns-quick-grid{gap:2px}.ns-quick-icon{width:43px;height:43px}.ns-quick-grid>button b{font-size:9px}.ns-welcome h1{font-size:24px}.ns-feature-strip{grid-template-columns:1fr}}
"""
css.write_text(c,encoding="utf-8")

# Newsroom and Profile get the same persistent mobile app navigation.
newsroom = root / "home/Newsroom.tsx"
if newsroom.exists():
 n=newsroom.read_text(encoding="utf-8")
 if "className='ns-bottom-nav'" not in n:
  n=n.replace("    <div className='ns-newsroom-feed'><NewsFeed /></div>\n  </main>;", """    <div className='ns-newsroom-feed'><NewsFeed /></div>
    <nav className='ns-bottom-nav' aria-label='Main navigation'><a href='#/'><span>⌂</span><span>Home</span></a><a href='#/templates'><span>▦</span><span>Templates</span></a><a className='ns-bottom-create' href='#/start'><span>＋</span></a><a className='active' href='#/newsroom'><span>▤</span><span>Newsroom</span></a><a href='#/profile'><span>♙</span><span>Profile</span></a></nav>
  </main>;""")
 newsroom.write_text(n,encoding="utf-8")

profile = root / "profile/Profile.tsx"
if profile.exists():
 p=profile.read_text(encoding="utf-8")
 if "className=\"ns-bottom-nav\"" not in p:
  p=p.replace("      <p className=\"ns-profile-foot\">", """      <p className="ns-profile-foot">""")
  p=p.replace("    </main>\n  </div>;", """    </main>
    <nav className="ns-bottom-nav" aria-label="Main navigation"><a href="#/"><span>⌂</span><span>Home</span></a><a href="#/templates"><span>▦</span><span>Templates</span></a><a className="ns-bottom-create" href="#/start"><span>＋</span></a><a href="#/newsroom"><span>▤</span><span>Newsroom</span></a><a className="active" href="#/profile"><span>♙</span><span>Profile</span></a></nav>
  </div>;""")
 profile.write_text(p,encoding="utf-8")

print("NEWS Studio Stitch-inspired Home, Projects, Templates navigation and responsive app shell applied.")
