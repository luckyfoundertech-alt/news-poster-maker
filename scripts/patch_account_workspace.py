from pathlib import Path

root = Path("opentempl/apps/editor/src")
tick = chr(96)
interpolation = "$" + "{id}"

db = root / "io/db.ts"
s = db.read_text(encoding="utf-8")
s = s.replace("const DB_NAME = 'tavla'; // legacy name kept on purpose, renaming it would orphan saved designs", "let DB_NAME = 'news-studio-guest';\nlet workspaceKey = 'guest';")
if "export async function setWorkspaceUser" not in s:
    anchor = "let dbp: Promise<IDBDatabase> | null = null;"
    addition = anchor + """

// Switch the app-level IndexedDB namespace before mounting an account workspace.
// Existing legacy data is preserved separately and is never silently assigned to
// whichever account happens to sign in first on a shared device.
export async function setWorkspaceUser(uid: string | null) {
  const nextKey = uid ? encodeURIComponent(uid) : 'guest';
  if (nextKey === workspaceKey) return;
  const previous = dbp;
  dbp = null;
  if (previous) {
    const opened = await previous.catch(() => null);
    opened?.close();
  }
  workspaceKey = nextKey;
  DB_NAME = 'news-studio-' + nextKey;
}
"""
    if anchor not in s:
        raise SystemExit("IndexedDB connection anchor not found.")
    s = s.replace(anchor, addition, 1)
db.write_text(s, encoding="utf-8")

designs = root / "io/designs.ts"
s = designs.read_text(encoding="utf-8")
old = "const dbName = (id: string) => " + tick + "tavla-design-" + interpolation + tick + "; // legacy name kept on purpose, it is where saved designs live"
new = "const dbName = (id: string) => 'news-studio-design-' + encodeURIComponent(auth.currentUser?.uid || 'guest') + '-' + id;"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit("Could not locate the design IndexedDB namespace declaration.")
s = s.replace(
    "if (uid) await syncDesignCloud(uid, doc).catch((e) => console.error('Cloud save failed', e));",
    "if (uid) void syncDesignCloud(uid, doc).catch((e) => console.error('Cloud save failed', e));"
)
old_delete = """export async function deleteDesign(id: string) {
  const uid = auth.currentUser?.uid;
  if (uid) await deleteDesignCloud(uid, id).catch((e) => console.error('Cloud delete failed', e));
  await db.del('designs', id);"""
new_delete = """export async function deleteDesign(id: string) {
  const uid = auth.currentUser?.uid;
  await db.del('designs', id);"""
if old_delete in s:
    s = s.replace(old_delete, new_delete, 1)
    anchor = "  forgetRoom(id);\n  notify();\n}"
    replacement = "  forgetRoom(id);\n  notify();\n  if (uid) void deleteDesignCloud(uid, id).catch((e) => console.error('Cloud delete failed', e));\n}"
    if anchor not in s:
        raise SystemExit("Design delete completion anchor not found.")
    s = s.replace(anchor, replacement, 1)
elif "if (uid) void deleteDesignCloud(uid, id)" not in s:
    raise SystemExit("Could not safely convert cloud design deletion to background work.")
designs.write_text(s, encoding="utf-8")

cloud = root / "auth/cloud.ts"
s = cloud.read_text(encoding="utf-8")
old = "const localName = (id: string) => " + tick + "tavla-design-" + interpolation + tick + ";"
new = "const localName = (uid: string, id: string) => 'news-studio-design-' + encodeURIComponent(uid) + '-' + id;"
s = s.replace(old, new)
s = s.replace("new IndexeddbPersistence(localName(remote.id), ydoc)", "new IndexeddbPersistence(localName(uid, remote.id), ydoc)")
s = s.replace("new IndexeddbPersistence(localName(item.value.id), ydoc)", "new IndexeddbPersistence(localName(uid, item.value.id), ydoc)")
if "tavla-design-" in s:
    raise SystemExit("Legacy Yjs database name still remains in cloud restore.")
cloud.write_text(s, encoding="utf-8")

uploads = root / "io/uploads.ts"
s = uploads.read_text(encoding="utf-8")
s = s.replace(
    "if (uid) await syncUploadCloud(uid, record).catch((e) => console.error('Upload cloud save failed', e));",
    "if (uid) void syncUploadCloud(uid, record).catch((e) => console.error('Upload cloud save failed', e));"
)
s = s.replace(
    "if (uid) await deleteUploadCloud(uid, id).catch((e) => console.error('Upload cloud delete failed', e));",
    "if (uid) void deleteUploadCloud(uid, id).catch((e) => console.error('Upload cloud delete failed', e));"
)
uploads.write_text(s, encoding="utf-8")

gate = root / "auth/AuthGate.tsx"
s = gate.read_text(encoding="utf-8")
if "setWorkspaceUser" not in s:
    s = s.replace(
        "import { restoreCloudDesigns, restoreCloudUploads } from './cloud';",
        "import { restoreCloudDesigns, restoreCloudUploads } from './cloud';\nimport { setWorkspaceUser } from '../io/db';",
        1
    )
start = s.find("export function AuthGate({ children }: { children: ReactNode }) {")
if start < 0:
    raise SystemExit("AuthGate component not found.")
replacement = """export function AuthGate({ children }: { children: ReactNode }) {
 const [user,setUser]=useState(auth.currentUser),[workspaceReady,setWorkspaceReady]=useState(false),[syncing,setSyncing]=useState(false);
 useEffect(()=>{
  let live=true;
  const unsub=onAuthStateChanged(auth,current=>{
   setWorkspaceReady(false);
   void (async()=>{
    try {
     await setWorkspaceUser(current?.uid ?? null);
     if(!live)return;
     setUser(current);
     setWorkspaceReady(true);
     if(current){
      setSyncing(true);
      const results=await Promise.allSettled([restoreCloudDesigns(current.uid),restoreCloudUploads(current.uid)]);
      results.forEach((result)=>{if(result.status==='rejected')console.error('Background cloud restore failed',result.reason);});
      if(live)setSyncing(false);
     } else if(live) setSyncing(false);
    } catch(e) {
     console.error('Workspace initialization failed',e);
     if(live){setUser(current);setWorkspaceReady(true);setSyncing(false);}
    }
   })();
  });
  return()=>{live=false;unsub();};
 },[]);
 if(!workspaceReady)return <div aria-live='polite' style={{minHeight:'100dvh',display:'grid',placeItems:'center',background:'#fff',color:'#475569',fontFamily:'system-ui'}}>Opening workspace…</div>;
 if(!user)return <AuthScreen/>;
 return <>{children}{syncing?<div className='ns-sync-pill' role='status' aria-live='polite'><span className='ns-sync-dot'/>Syncing cloud designs in background…</div>:null}</>;
}
"""
s = s[:start] + replacement
gate.write_text(s, encoding="utf-8")

print("Account-scoped local workspaces and non-blocking cloud operations applied.")
