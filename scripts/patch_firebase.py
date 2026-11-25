from pathlib import Path
import json, sys

root = Path(sys.argv[1])
src = root / "apps/editor/src"
pkg_path = root / "apps/editor/package.json"
pkg = json.loads(pkg_path.read_text())
pkg.setdefault("dependencies", {})["firebase"] = "^12.6.0"
pkg["dependencies"]["@capacitor-firebase/authentication"] = "^7.2.0"
pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")

(src / "auth").mkdir(exist_ok=True)
(src / "auth/firebase.ts").write_text("""import { initializeApp, getApps } from 'firebase/app';
import { getAuth, setPersistence, indexedDBLocalPersistence } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const config = {
  apiKey: 'AIzaSyDsCRBHw7EGuu1F3PwSyr2gGLwhLoqAjqE',
  authDomain: 'ghost-b9156.firebaseapp.com',
  projectId: 'ghost-b9156',
  storageBucket: 'ghost-b9156.firebasestorage.app',
  messagingSenderId: '519573612826',
  appId: '1:519573612826:android:8568296d317fa86bcfa4a3',
};
export const firebaseApp = getApps().length ? getApps()[0] : initializeApp(config);
export const auth = getAuth(firebaseApp);
export const firestore = getFirestore(firebaseApp);
export const storage = getStorage(firebaseApp);
export const authReady = setPersistence(auth, indexedDBLocalPersistence).catch(() => undefined);
""")

(src / "auth/cloud.ts").write_text("""import * as Y from 'yjs';
import { IndexeddbPersistence } from 'y-indexeddb';
import { collection, deleteDoc, doc as fsDoc, getDoc, getDocs, serverTimestamp, setDoc } from 'firebase/firestore';
import { deleteObject, getBytes, ref, uploadBytes } from 'firebase/storage';
import type { DesignDoc } from '../doc/design';
import type { DesignEntry } from '../io/designs';
import { db } from '../io/db';
import { firestore, storage } from './firebase';

const localName = (id: string) => `tavla-design-${id}`;
const remoteRef = (uid: string, id: string) => fsDoc(firestore, 'users', uid, 'designs', id);

export async function syncDesignCloud(uid: string, design: DesignDoc) {
  const id = design.snapshot.meta.id;
  if (!uid || !id || !design.snapshot.pageOrder.length) return;
  const bytes = Y.encodeStateAsUpdate(design.ydoc);
  const path = `users/${uid}/designs/${id}/state.ydoc`;
  await uploadBytes(ref(storage, path), new Blob([bytes], { type: 'application/octet-stream' }), { contentType: 'application/octet-stream' });
  const mediaFiles: Array<{ id: string; path: string; mime: string }> = [];
  const mediaIds = new Set<string>();
  for (const element of Object.values(design.snapshot.elements)) if (element.type === 'video') mediaIds.add(element.mediaId);
  if (design.snapshot.meta.soundtrack?.mediaId) mediaIds.add(design.snapshot.meta.soundtrack.mediaId);
  for (const mediaId of mediaIds) {
    const blob = await db.get<Blob>('media', mediaId);
    if (!blob) continue;
    const mediaPath = `users/${uid}/designs/${id}/media/${mediaId}`;
    await uploadBytes(ref(storage, mediaPath), blob, { contentType: blob.type || 'application/octet-stream' });
    mediaFiles.push({ id: mediaId, path: mediaPath, mime: blob.type || 'application/octet-stream' });
  }
  const m = design.snapshot.meta;
  await setDoc(remoteRef(uid, id), {
    id, title: m.title, width: m.width, height: m.height, formatId: m.formatId ?? null,
    createdAt: m.createdAt, updatedAt: m.updatedAt ?? Date.now(),
    pages: design.snapshot.pageOrder.length, statePath: path, mediaFiles, syncedAt: serverTimestamp(),
  }, { merge: true });
}

export async function deleteDesignCloud(uid: string, id: string) {
  const snapshot = await getDoc(remoteRef(uid, id));
  const data = snapshot.data() as { statePath?: string; mediaFiles?: Array<{ path: string }> } | undefined;
  await deleteDoc(remoteRef(uid, id));
  if (data?.statePath) await deleteObject(ref(storage, data.statePath)).catch(() => undefined);
  for (const file of data?.mediaFiles ?? []) await deleteObject(ref(storage, file.path)).catch(() => undefined);
}

export async function restoreCloudDesigns(uid: string) {
  const rows = await getDocs(collection(firestore, 'users', uid, 'designs'));
  const remoteById = new Map(rows.docs.map((row) => [row.id, row.data()]));
  for (const row of rows.docs) {
    const remote = row.data() as { id: string; title: string; width: number; height: number; formatId?: string | null; createdAt: number; updatedAt: number; pages: number; statePath: string };
    if (!remote.id || !remote.statePath) continue;
    const local = await db.get<DesignEntry>('designs', remote.id);
    if (local && local.updatedAt >= remote.updatedAt) continue;
    const update = await getBytes(ref(storage, remote.statePath));
    const ydoc = new Y.Doc();
    Y.applyUpdate(ydoc, new Uint8Array(update));
    const persistence = new IndexeddbPersistence(localName(remote.id), ydoc);
    await persistence.whenSynced;
    const { DesignDoc } = await import('../doc/design');
    const design = new DesignDoc(ydoc);
    const mediaFiles = (remote as typeof remote & { mediaFiles?: Array<{ id: string; path: string; mime: string }> }).mediaFiles ?? [];
    for (const file of mediaFiles) {
      const mediaBytes = await getBytes(ref(storage, file.path));
      await db.set('media', file.id, new Blob([mediaBytes], { type: file.mime || 'application/octet-stream' }));
    }
    const meta = design.snapshot.meta;
    await db.set('designs', remote.id, {
      id: remote.id, title: remote.title || meta.title, width: remote.width || meta.width,
      height: remote.height || meta.height, formatId: remote.formatId || undefined,
      createdAt: remote.createdAt || meta.createdAt, updatedAt: remote.updatedAt || Date.now(),
      pages: remote.pages || design.snapshot.pageOrder.length,
    } satisfies DesignEntry);
    try {
      const firstPage = design.snapshot.pageOrder[0];
      if (firstPage) {
        const { thumbnail } = await import('../export/render');
        await db.set('thumbs', remote.id, await thumbnail(design, design.toSnapshot(), firstPage));
      }
    } catch (e) { console.warn('Cloud thumbnail restore skipped', e); }
    await persistence.destroy();
    design.destroy();
  }
  // Back up designs that were created locally before the user registered.
  const locals = await db.all<DesignEntry>('designs');
  for (const item of locals) {
    const remote = remoteById.get(item.value.id) as { updatedAt?: number } | undefined;
    if (remote && (remote.updatedAt ?? 0) >= item.value.updatedAt) continue;
    const ydoc = new Y.Doc();
    const persistence = new IndexeddbPersistence(localName(item.value.id), ydoc);
    await persistence.whenSynced;
    const { DesignDoc } = await import('../doc/design');
    const design = new DesignDoc(ydoc);
    await syncDesignCloud(uid, design).catch((e) => console.error('Initial cloud backup failed', e));
    await persistence.destroy();
    design.destroy();
  }
  window.dispatchEvent(new Event('news-cloud-restored'));
}
""")

(src / "auth/AuthGate.tsx").write_text("""import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { onAuthStateChanged, createUserWithEmailAndPassword, signInWithEmailAndPassword, sendPasswordResetEmail, signOut, GoogleAuthProvider, signInWithPopup, signInWithCredential } from 'firebase/auth';
import { Capacitor } from '@capacitor/core';
import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import { auth, authReady } from './firebase';
import { restoreCloudDesigns } from './cloud';

function AuthScreen() {
  const [mode, setMode] = useState<'login'|'signup'|'reset'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const submit = async (e: FormEvent) => {
    e.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      await authReady;
      if (mode === 'signup') await createUserWithEmailAndPassword(auth, email.trim(), password);
      else if (mode === 'reset') { await sendPasswordResetEmail(auth, email.trim()); setNotice('Password reset link email par bhej diya gaya hai.'); }
      else await signInWithEmailAndPassword(auth, email.trim(), password);
    } catch (e) { setError((e as Error).message || 'Authentication failed'); }
    finally { setBusy(false); }
  };
  const google = async () => {
    setBusy(true); setError('');
    try {
      await authReady;
      if (Capacitor.isNativePlatform()) {
        const result = await FirebaseAuthentication.signInWithGoogle();
        const idToken = result.credential?.idToken;
        if (!idToken) throw new Error('Google ID token nahi mila. Firebase Android SHA-1 aur OAuth client configure karein.');
        await signInWithCredential(auth, GoogleAuthProvider.credential(idToken));
      } else {
        await signInWithPopup(auth, new GoogleAuthProvider());
      }
    } catch (e) { setError((e as Error).message || 'Google sign-in failed'); }
    finally { setBusy(false); }
  };
  return <main style={{ minHeight:'100dvh', display:'grid', placeItems:'center', padding:20, background:'var(--paper)' }}>
    <form onSubmit={submit} style={{ width:'min(100%,420px)', padding:28, border:'1px solid var(--line)', borderRadius:18, background:'var(--panel,white)', display:'grid', gap:14 }}>
      <div><h1 style={{ margin:0 }}>NEWS Studio</h1><p className="muted">Sign in to save your designs and photos securely in your cloud.</p></div>
      {mode !== 'reset' ? <button type="button" className="btn btn-outline" disabled={busy} onClick={google}>Continue with Google</button> : null}
      {mode !== 'reset' ? <div className="muted" style={{textAlign:'center'}}>or continue with email</div> : null}
      <label>Email<input required type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} /></label>
      {mode !== 'reset' ? <label>Password<input required minLength={6} type="password" autoComplete={mode==='signup'?'new-password':'current-password'} value={password} onChange={e=>setPassword(e.target.value)} /></label> : null}
      {error ? <p role="alert" style={{color:'#b42318',overflowWrap:'anywhere'}}>{error}</p> : null}
      {notice ? <p role="status">{notice}</p> : null}
      <button className="btn btn-primary" disabled={busy}>{busy ? 'Please wait…' : mode==='signup'?'Create account':mode==='reset'?'Send reset link':'Sign in'}</button>
      <div style={{display:'flex',justifyContent:'space-between',gap:8,flexWrap:'wrap'}}>
        <button type="button" className="text-link" onClick={()=>{setMode(mode==='signup'?'login':'signup');setError('');}}>{mode==='signup'?'Already have an account? Sign in':'Create account'}</button>
        <button type="button" className="text-link" onClick={()=>{setMode(mode==='reset'?'login':'reset');setError('');}}>{mode==='reset'?'Back to sign in':'Forgot password?'}</button>
      </div>
    </form>
  </main>;
}

export function AuthGate({ children }: { children: ReactNode }) {
  const [user, setUser] = useState(auth.currentUser);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let live = true;
    const unsub = onAuthStateChanged(auth, async current => {
      if (!live) return;
      setUser(current);
      if (current) {
        try { await restoreCloudDesigns(current.uid); } catch (e) { console.error('Cloud restore failed', e); }
      }
      if (live) setReady(true);
    });
    return () => { live = false; unsub(); };
  }, []);
  if (!user) return <AuthScreen />;
  if (!ready) return <div style={{minHeight:'100dvh',display:'grid',placeItems:'center'}}>Restoring your cloud designs…</div>;
  return <>{children}<button onClick={()=>signOut(auth)} title="Sign out" style={{position:'fixed',right:12,bottom:12,zIndex:10000}} className="btn btn-outline">Sign out · {user.email || 'Google account'}</button></>;
}
""")

app = src / "App.tsx"
body = app.read_text()
if "import { AuthGate } from './auth/AuthGate';" not in body:
    body = "import { AuthGate } from './auth/AuthGate';\n" + body
body = body.replace("export function App() {", "function AppRoutes() {", 1)
body += "\nexport function App() { return <AuthGate><AppRoutes /></AuthGate>; }\n"
app.write_text(body)

designs = src / "io/designs.ts"
body = designs.read_text()
if "syncDesignCloud" not in body:
    body = "import { auth } from '../auth/firebase';\nimport { syncDesignCloud, deleteDesignCloud } from '../auth/cloud';\n" + body
body = body.replace("  notify();\n}\n\nexport async function updateEntry", "  notify();\n  const uid = auth.currentUser?.uid;\n  if (uid) void syncDesignCloud(uid, doc).catch((e) => console.error('Cloud save failed', e));\n}\n\nexport async function updateEntry", 1)
body = body.replace("export async function deleteDesign(id: string) {\n", "export async function deleteDesign(id: string) {\n  const uid = auth.currentUser?.uid;\n  if (uid) await deleteDesignCloud(uid, id).catch((e) => console.error('Cloud delete failed', e));\n", 1)
designs.write_text(body)

print("Firebase email/Google auth gate and per-user Yjs cloud backup/restore patches applied.")
