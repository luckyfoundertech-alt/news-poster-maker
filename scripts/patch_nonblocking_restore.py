from pathlib import Path

gate = Path("opentempl/apps/editor/src/auth/AuthGate.tsx")
source = gate.read_text(encoding="utf-8")

old = """export function AuthGate({ children }: { children: ReactNode }) {
 const [user,setUser]=useState(auth.currentUser),[ready,setReady]=useState(false);
 useEffect(()=>{let live=true;const unsub=onAuthStateChanged(auth,async current=>{if(!live)return;setUser(current);if(current){setReady(false);try{await restoreCloudDesigns(current.uid);await restoreCloudUploads(current.uid);}catch(e){console.error('Cloud restore failed',e);}if(live)setReady(true);}else if(live)setReady(true);});return()=>{live=false;unsub();};},[]);
 if(!user)return <AuthScreen/>;
 if(!ready)return <div style={{minHeight:'100dvh',display:'grid',placeItems:'center',background:'#fff',color:'#0f172a',fontFamily:'system-ui'}}>Restoring your cloud designs…</div>;
 return <>{children}<button onClick={()=>signOut(auth)} title='Sign out' className='btn btn-outline' style={{position:'fixed',right:12,bottom:12,zIndex:10000}}>Sign out · {user.displayName||user.email||'Google account'}</button></>;
}"""

new = """export function AuthGate({ children }: { children: ReactNode }) {
 const [user,setUser]=useState(auth.currentUser),[syncing,setSyncing]=useState(false);
 useEffect(()=>{let live=true;const unsub=onAuthStateChanged(auth,current=>{if(!live)return;setUser(current);if(current){setSyncing(true);void (async()=>{try{await restoreCloudDesigns(current.uid);await restoreCloudUploads(current.uid);}catch(e){console.error('Background cloud restore failed',e);}finally{if(live)setSyncing(false);}})();}else setSyncing(false);});return()=>{live=false;unsub();};},[]);
 if(!user)return <AuthScreen/>;
 return <>{children}{syncing?<div className='ns-sync-pill' role='status' aria-live='polite'><span className='ns-sync-dot'/>Syncing cloud designs…</div>:null}<button onClick={()=>signOut(auth)} title='Sign out' className='btn btn-outline' style={{position:'fixed',right:'max(12px, env(safe-area-inset-right))',bottom:'max(12px, env(safe-area-inset-bottom))',zIndex:10000,maxWidth:'calc(100vw - 24px)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>Sign out · {user.displayName||user.email||'Google account'}</button></>;
}"""

if old not in source:
    raise SystemExit("Expected original AuthGate block not found; stopping safely.")
source = source.replace(old, new, 1)

css_anchor = ".ns-status-pill{display:inline-flex;gap:7px;align-items:center;background:#fef2f2;color:#dc2626;border:1px solid #fecaca;border-radius:99px;padding:5px 11px;font-size:10px;font-weight:800;letter-spacing:1px;margin-top:12px}"
css_add = css_anchor + """
.ns-sync-pill{position:fixed;top:calc(env(safe-area-inset-top,0px) + 10px);left:50%;transform:translateX(-50%);z-index:9998;display:flex;align-items:center;gap:9px;width:max-content;max-width:calc(100vw - 24px);padding:9px 13px;border:1px solid #bfdbfe;border-radius:999px;background:rgba(239,246,255,.97);color:#1d4ed8;box-shadow:0 4px 16px #0f172a18;font:600 12px/1.3 system-ui,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none;backdrop-filter:blur(8px)}
.ns-sync-dot{width:7px;height:7px;flex:0 0 7px;border-radius:50%;background:#2563eb;box-shadow:0 0 0 3px #2563eb20;animation:ns-sync-pulse 1.2s ease-in-out infinite}@keyframes ns-sync-pulse{50%{opacity:.35;transform:scale(.8)}}
@media(max-width:360px){.ns-sync-pill{font-size:11px;padding:8px 10px;max-width:calc(100vw - 16px)}}"""
if css_anchor not in source:
    raise SystemExit("Expected auth CSS anchor not found; stopping safely.")
source = source.replace(css_anchor, css_add, 1)
gate.write_text(source, encoding="utf-8")
print("Applied non-blocking cloud restore and safe-area responsive status indicator.")
