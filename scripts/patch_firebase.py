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
import type { Asset } from '../doc/types';
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
  const stateBuffer = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(stateBuffer).set(bytes);
  await uploadBytes(ref(storage, path), new Blob([stateBuffer], { type: 'application/octet-stream' }), { contentType: 'application/octet-stream' });
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

export async function syncUploadCloud(uid: string, asset: Asset & { addedAt: number }) {
  if (!uid || !asset.id) return;
  const path = `users/${uid}/uploads/${asset.id}`;
  const assetBuffer = new ArrayBuffer(asset.bytes.byteLength);
  new Uint8Array(assetBuffer).set(asset.bytes);
  await uploadBytes(ref(storage, path), new Blob([assetBuffer], { type: asset.mime }), { contentType: asset.mime || 'application/octet-stream' });
  await setDoc(fsDoc(firestore, 'users', uid, 'uploads', asset.id), {
    id: asset.id, name: asset.name, mime: asset.mime, width: asset.width,
    height: asset.height, addedAt: asset.addedAt, path, syncedAt: serverTimestamp(),
  }, { merge: true });
}

export async function deleteUploadCloud(uid: string, id: string) {
  const remote = fsDoc(firestore, 'users', uid, 'uploads', id);
  const snapshot = await getDoc(remote);
  const data = snapshot.data() as { path?: string } | undefined;
  await deleteDoc(remote);
  if (data?.path) await deleteObject(ref(storage, data.path)).catch(() => undefined);
}

export async function restoreCloudUploads(uid: string) {
  const rows = await getDocs(collection(firestore, 'users', uid, 'uploads'));
  const remoteIds = new Set(rows.docs.map((row) => row.id));
  for (const row of rows.docs) {
    const remote = row.data() as { id: string; name: string; mime: string; width: number; height: number; addedAt: number; path: string };
    if (!remote.id || !remote.path) continue;
    const local = await db.get<Asset & { addedAt: number }>('uploads', remote.id);
    if (local && local.addedAt >= remote.addedAt) continue;
    const bytes = await getBytes(ref(storage, remote.path));
    await db.set('uploads', remote.id, {
      id: remote.id, name: remote.name, mime: remote.mime, width: remote.width,
      height: remote.height, bytes: new Uint8Array(bytes), addedAt: remote.addedAt,
    } satisfies Asset & { addedAt: number });
  }
  const locals = await db.all<Asset & { addedAt: number }>('uploads');
  for (const item of locals) {
    if (remoteIds.has(item.value.id)) {
      const row = rows.docs.find((entry) => entry.id === item.value.id);
      if ((row?.data().addedAt ?? 0) >= item.value.addedAt) continue;
    }
    await syncUploadCloud(uid, item.value).catch((e) => console.error('Upload library cloud backup failed', e));
  }
}
""")

(src / "auth/AuthGate.tsx").write_text("""import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { onAuthStateChanged, createUserWithEmailAndPassword, signInWithEmailAndPassword, sendPasswordResetEmail, signOut, GoogleAuthProvider, signInWithPopup, signInWithCredential, updateProfile, setPersistence, indexedDBLocalPersistence, browserSessionPersistence } from 'firebase/auth';
import { Capacitor } from '@capacitor/core';
import { FirebaseAuthentication } from '@capacitor-firebase/authentication';
import { auth, authReady } from './firebase';
import { restoreCloudDesigns, restoreCloudUploads } from './cloud';

const LOGO = 'https://lh3.googleusercontent.com/aida-public/AB6AXuCmTmy3ETuD5atbGZG4-BP8X4yyDmE5Cd7G-Qu6bEWxcDhhKge-1zvwk3aAtl4tSF2R0kVPFkTFZYkRRvuKDgnXwKzr8jbo0KDpTD1GMZy5kq2Ib9fjBS79SpwcVeV1Id6uC3oJjxoUorjO4qS6vKIbyqw_JVqUiNA3kapyO_-oCdhEPjgQzU1O-VqMXv0Zh0qWk4RzsCFimnQ1Z6uacLqVxTf-8V51vxqtaoTmJTngDWcnyl7EnIDzMQ';
const CSS = `
.ns-auth{min-height:100dvh;background:#fff;color:#0f172a;font-family:'Plus Jakarta Sans',Inter,system-ui,sans-serif;display:flex;flex-direction:column;align-items:center;padding:env(safe-area-inset-top,8px) 20px env(safe-area-inset-bottom,12px);box-sizing:border-box}
.ns-auth *{box-sizing:border-box}.ns-auth button,.ns-auth input{font:inherit}.ns-status{width:100%;max-width:420px;height:28px;display:flex;justify-content:space-between;align-items:center;font-size:12px;font-weight:700;color:#334155}
.ns-wrap{width:100%;max-width:420px;display:flex;flex:1;flex-direction:column}.ns-brand{display:flex;flex-direction:column;align-items:center;text-align:center;margin:22px 0 22px}.ns-logo{width:82px;height:82px;border-radius:20px;padding:5px;background:#fff;border:1px solid #e2e8f0;box-shadow:0 4px 20px -4px #0f172a12;object-fit:cover}.ns-title{font-size:25px;font-weight:800;letter-spacing:-.7px;margin:14px 0 5px}.ns-sub{font-size:13px;line-height:1.55;color:#64748b;max-width:310px;margin:0}.ns-card{width:100%;background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:19px;box-shadow:0 4px 24px -4px #0f172a0f;display:flex;flex-direction:column;gap:14px}
.ns-field{display:flex;flex-direction:column;gap:7px}.ns-field label{display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#334155}.ns-field input{width:100%;height:48px;border:1px solid #cbd5e1;border-radius:12px;background:#f8fafc;padding:0 13px;color:#0f172a;outline:none;font-size:14px}.ns-field input:focus{background:#fff;border-color:#2563eb;box-shadow:0 0 0 3px #2563eb18}.ns-pwd{display:flex;align-items:center;position:relative}.ns-pwd input{padding-right:48px}.ns-eye{position:absolute;right:5px;width:40px;height:40px;border:0;background:transparent;color:#64748b;font-size:18px}.ns-btn{width:100%;min-height:48px;border-radius:12px;border:1px solid #e2e8f0;background:#fff;color:#334155;font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;gap:9px;cursor:pointer}.ns-primary{background:#2563eb;color:#fff;border-color:#2563eb;box-shadow:0 2px 8px #2563eb30}.ns-btn:disabled{opacity:.6;cursor:wait}.ns-link{border:0;background:transparent;color:#2563eb;font-size:12px;font-weight:700;padding:7px 2px;cursor:pointer}.ns-divider{display:flex;align-items:center;gap:12px;color:#94a3b8;font-size:10px;font-weight:700;letter-spacing:1px}.ns-divider:before,.ns-divider:after{content:'';height:1px;background:#e2e8f0;flex:1}.ns-google svg{width:17px;height:17px}.ns-banner{margin-top:15px;padding:12px 14px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:13px;display:flex;align-items:center;gap:11px}.ns-banner-icon{width:34px;height:34px;border-radius:9px;background:#dbeafe;color:#2563eb;display:grid;place-items:center}.ns-footer{margin-top:auto;padding:22px 0 10px;text-align:center;font-size:12px;color:#64748b}.ns-error{padding:10px 12px;border-radius:10px;background:#fef2f2;border:1px solid #fecaca;color:#b91c1c;font-size:12px;line-height:1.5;overflow-wrap:anywhere}.ns-notice{padding:10px 12px;border-radius:10px;background:#ecfdf5;border:1px solid #a7f3d0;color:#047857;font-size:12px}.ns-check{display:flex;gap:8px;align-items:flex-start;font-size:12px;color:#475569;line-height:1.5}.ns-check input{accent-color:#2563eb;margin-top:2px}.ns-badges{display:flex;gap:7px;flex-wrap:wrap;justify-content:center;margin-top:16px}.ns-badge{border-radius:99px;padding:6px 10px;font-size:11px;font-weight:700;background:#eff6ff;color:#1d4ed8;border:1px solid #dbeafe}.ns-badge.red{background:#fef2f2;color:#dc2626;border-color:#fecaca}.ns-hero{background:#fff;border:1px solid #e2e8f0;border-radius:17px;padding:15px;margin:18px 0 0;box-shadow:0 2px 10px #0f172a08}.ns-hero h2{font-size:15px;margin:9px 0 7px}.ns-preview{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:10px;display:flex;gap:10px;align-items:center}.ns-preview img{width:48px;height:48px;object-fit:cover;border-radius:8px}.ns-stats{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}.ns-stat{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:12px;font-size:11px;color:#64748b}.ns-stat b{display:block;font-size:15px;color:#0f172a;margin-bottom:3px}.ns-actions{display:flex;flex-direction:column;gap:10px;margin-top:auto;padding-top:18px}.ns-back{align-self:flex-start;margin:4px 0 0}.ns-status-pill{display:inline-flex;gap:7px;align-items:center;background:#fef2f2;color:#dc2626;border:1px solid #fecaca;border-radius:99px;padding:5px 11px;font-size:10px;font-weight:800;letter-spacing:1px;margin-top:12px}
@media(max-height:720px){.ns-brand{margin:10px 0 14px}.ns-logo{width:68px;height:68px}.ns-card{padding:15px;gap:11px}.ns-hero{margin-top:12px}}
`;

function GoogleMark(){return <svg viewBox='0 0 24 24' aria-hidden='true'><path fill='#4285F4' d='M23.5 12.2c0-.7-.06-1.4-.18-2.07H12v4.5h6.45a5.5 5.5 0 0 1-2.4 3.62v3h3.88c2.27-2.1 3.57-5.18 3.57-9.05z'/><path fill='#34A853' d='M12 24c3.2 0 5.9-1.06 7.9-2.88l-3.87-3c-1.08.72-2.45 1.14-4.03 1.14-3.1 0-5.73-2.08-6.67-4.9H1.33v3.08A12 12 0 0 0 12 24z'/><path fill='#FBBC05' d='M5.33 14.36a7.2 7.2 0 0 1 0-4.72V6.56H1.33a12 12 0 0 0 0 10.88z'/><path fill='#EA4335' d='M12 4.75c1.75 0 3.32.6 4.56 1.78l3.42-3.42A11.45 11.45 0 0 0 12 0 12 12 0 0 0 1.33 6.56l4 3.08C6.27 6.82 8.9 4.75 12 4.75z'/></svg>}

function AuthScreen(){
 const [page,setPage]=useState<'welcome'|'login'|'signup'|'reset'>('welcome');
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[name,setName]=useState(''),[confirm,setConfirm]=useState('');
 const [showPwd,setShowPwd]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[terms,setTerms]=useState(false);
 const [remember,setRemember]=useState(true);
 const message=(e:unknown)=>{const code=(e as {code?:string})?.code||'';const messages:Record<string,string>={'auth/invalid-email':'Email address sahi nahi hai.','auth/user-not-found':'Is email se account nahi mila. Pehle account create karein.','auth/wrong-password':'Password galat hai. Dobara check karein.','auth/invalid-credential':'Email ya password galat hai.','auth/email-already-in-use':'Is email se account pehle se bana hua hai. Sign in karein.','auth/weak-password':'Password kam se kam 8 characters ka rakhein.','auth/network-request-failed':'Internet connection check karke dobara try karein.','auth/too-many-requests':'Bahut attempts hue. Thodi der baad try karein.','auth/popup-closed-by-user':'Google sign-in cancel ho gaya.','auth/popup-blocked':'Google sign-in popup block hua. Dobara try karein.'};return messages[code]||((e as Error)?.message||'Kuch problem hui. Dobara try karein.');};
 const runGoogle=async()=>{setBusy(true);setError('');setNotice('');try{await authReady;if(Capacitor.isNativePlatform()){const result=await FirebaseAuthentication.signInWithGoogle();const token=result.credential?.idToken;if(!token)throw new Error('Google ID token nahi mila. Firebase Android SHA-1 aur OAuth client verify karein.');await signInWithCredential(auth,GoogleAuthProvider.credential(token));}else await signInWithPopup(auth,new GoogleAuthProvider());}catch(e){setError(message(e));}finally{setBusy(false);}};
 const submit=async(e:FormEvent)=>{e.preventDefault();setBusy(true);setError('');setNotice('');try{await authReady;if(page!=='reset')await setPersistence(auth,remember?indexedDBLocalPersistence:browserSessionPersistence);if(page==='reset'){await sendPasswordResetEmail(auth,email.trim());setNotice('Password reset link aapke email par bhej diya gaya hai.');return;}if(page==='signup'){if(password.length<8)throw new Error('Password kam se kam 8 characters ka hona chahiye.');if(password!==confirm)throw new Error('Dono passwords match nahi kar rahe.');if(!terms)throw new Error('Account banane ke liye Terms accept karein.');const cred=await createUserWithEmailAndPassword(auth,email.trim(),password);if(name.trim())await updateProfile(cred.user,{displayName:name.trim()});}else await signInWithEmailAndPassword(auth,email.trim(),password);}catch(e){setError(message(e));}finally{setBusy(false);}};
 const switchPage=(p:'welcome'|'login'|'signup'|'reset')=>{setPage(p);setError('');setNotice('');};
 return <div className='ns-auth'><style>{CSS}</style><div className='ns-status'><span>NEWS Studio</span><span>● ● ●</span></div><div className='ns-wrap'>
 {page==='welcome'?<>
  <div className='ns-brand'><img className='ns-logo' src={LOGO} alt='NEWS Studio app icon'/><div className='ns-status-pill'>● CREATOR ACCESS</div><h1 className='ns-title'>NEWS <span style={{color:'#2563eb'}}>Studio</span></h1><p className='ns-sub'>Mobile editorial powerhouse for breaking news flyers, posters &amp; stories</p>
   <div className='ns-badges'><span className='ns-badge'>✦ 337+ Layouts</span><span className='ns-badge red'>◉ Live Feeds</span><span className='ns-badge'>✓ 4K Export</span></div></div>
  <div className='ns-hero'><div style={{display:'flex',justifyContent:'space-between',fontSize:11,fontWeight:800,color:'#64748b'}}><span>▣ EDITORIAL ENGINE</span><span style={{color:'#dc2626'}}>● LIVE</span></div><h2>Design Breaking News Posters in Seconds</h2><div className='ns-preview'><img src={LOGO} alt='NEWS Studio'/><div style={{minWidth:0}}><b style={{fontSize:13}}>Your next newsroom design starts here</b><div style={{fontSize:11,color:'#64748b',marginTop:4}}>Templates · Layers · Professional export</div></div></div><div className='ns-stats'><div className='ns-stat'><b>337+</b>Ready-made layouts</div><div className='ns-stat'><b>4K</b>High-resolution export</div></div></div>
  <div className='ns-actions'><button className='ns-btn ns-primary' onClick={()=>switchPage('signup')}>Get Started / Create Account <span>→</span></button><button className='ns-btn' onClick={()=>switchPage('login')}>↪ I Already Have an Account</button><button className='ns-btn ns-google' disabled={busy} onClick={runGoogle}><GoogleMark/>Continue with Google</button></div>
  <div className='ns-footer'>By continuing you accept our Terms of Service and Privacy Policy.</div>
 </>:<>
  <button className='ns-link ns-back' onClick={()=>switchPage('welcome')}>← Back</button>
  <div className='ns-brand' style={{marginTop:12,marginBottom:18}}><img className='ns-logo' src={LOGO} alt='NEWS Studio'/><div className='ns-status-pill'>● CREATOR PORTAL</div><h1 className='ns-title'>{page==='signup'?'Create Studio Account':page==='reset'?'Reset Password':'Welcome Back, Creator'}</h1><p className='ns-sub'>{page==='signup'?'Create your account to save designs and access your studio anywhere.':page==='reset'?'We will email you a secure password reset link.':'Sign in to access your news posters, live layer stacks & creative workspace.'}</p></div>
  <form className='ns-card' onSubmit={submit}>
   {page==='signup'?<div className='ns-field'><label>Full Name <span>CREATOR PROFILE</span></label><input value={name} onChange={e=>setName(e.target.value)} placeholder='Your full name' autoComplete='name' required/></div>:null}
   <div className='ns-field'><label>Work or Creator Email <span style={{color:'#2563eb'}}>STUDIO ID</span></label><input type='email' value={email} onChange={e=>setEmail(e.target.value)} placeholder='editor@pressroom.news' autoComplete='email' required/></div>
   {page!=='reset'?<><div className='ns-field'><label>Password <span style={{color:'#94a3b8'}}>MIN 8 CHARS</span></label><div className='ns-pwd'><input type={showPwd?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder='Enter studio password' autoComplete={page==='signup'?'new-password':'current-password'} minLength={8} required/><button className='ns-eye' type='button' onClick={()=>setShowPwd(!showPwd)} aria-label='Toggle password visibility'>{showPwd?'◉':'◎'}</button></div></div>
   {page==='signup'?<div className='ns-field'><label>Confirm Password</label><input type={showPwd?'text':'password'} value={confirm} onChange={e=>setConfirm(e.target.value)} placeholder='Re-enter password' autoComplete='new-password' required/></div>:<div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><label className='ns-check'><input type='checkbox' checked={remember} onChange={e=>setRemember(e.target.checked)}/>Remember device</label><button type='button' className='ns-link' onClick={()=>switchPage('reset')}>Forgot Password?</button></div>}</>:null}
   {page==='signup'?<label className='ns-check'><input type='checkbox' checked={terms} onChange={e=>setTerms(e.target.checked)}/>I agree to the Studio Terms of Service and Privacy Policy.</label>:null}
   {error?<div className='ns-error' role='alert'>{error}</div>:null}{notice?<div className='ns-notice' role='status'>{notice}</div>:null}
   <button className='ns-btn ns-primary' disabled={busy}>{busy?'Please wait…':page==='signup'?'Create Studio Account':page==='reset'?'Send Reset Link':'Sign In to Studio'} <span>→</span></button>
   {page!=='reset'?<><div className='ns-divider'>OR CONTINUE WITH</div><button type='button' className='ns-btn ns-google' disabled={busy} onClick={runGoogle}><GoogleMark/>{page==='signup'?'Sign up with Google':'Continue with Google'}</button></>:null}
  </form>
  <div className='ns-banner'><div className='ns-banner-icon'>▣</div><div><b style={{display:'block',fontSize:12,color:'#1e293b'}}>337+ Live Templates Ready</b><span style={{fontSize:11,color:'#64748b'}}>Breaking banners, reels &amp; editorial tiles</span></div></div>
  <div className='ns-footer'>{page==='signup'?<>Already have an account? <button className='ns-link' onClick={()=>switchPage('login')}>Sign In</button></>:page==='reset'?<button className='ns-link' onClick={()=>switchPage('login')}>Back to Sign In</button>:<>Don't have a studio account? <button className='ns-link' onClick={()=>switchPage('signup')}>Create account</button></>}</div>
 </>}
 </div></div>;
}

export function AuthGate({ children }: { children: ReactNode }) {
 const [user,setUser]=useState(auth.currentUser),[ready,setReady]=useState(false);
 useEffect(()=>{let live=true;const unsub=onAuthStateChanged(auth,async current=>{if(!live)return;setUser(current);if(current){setReady(false);try{await restoreCloudDesigns(current.uid);await restoreCloudUploads(current.uid);}catch(e){console.error('Cloud restore failed',e);}if(live)setReady(true);}else if(live)setReady(true);});return()=>{live=false;unsub();};},[]);
 if(!user)return <AuthScreen/>;
 if(!ready)return <div style={{minHeight:'100dvh',display:'grid',placeItems:'center',background:'#fff',color:'#0f172a',fontFamily:'system-ui'}}>Restoring your cloud designs…</div>;
 return <>{children}<button onClick={()=>signOut(auth)} title='Sign out' className='btn btn-outline' style={{position:'fixed',right:12,bottom:12,zIndex:10000}}>Sign out · {user.displayName||user.email||'Google account'}</button></>;
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
body = body.replace("  notify();\n}\n\nexport async function updateEntry", "  notify();\n  const uid = auth.currentUser?.uid;\n  if (uid) await syncDesignCloud(uid, doc).catch((e) => console.error('Cloud save failed', e));\n}\n\nexport async function updateEntry", 1)
body = body.replace("export async function deleteDesign(id: string) {\n", "export async function deleteDesign(id: string) {\n  const uid = auth.currentUser?.uid;\n  if (uid) await deleteDesignCloud(uid, id).catch((e) => console.error('Cloud delete failed', e));\n", 1)
designs.write_text(body)

# Keep the standalone Uploads library backed up per signed-in user as well.
uploads = src / "io/uploads.ts"
body = uploads.read_text()
if "syncUploadCloud" not in body:
    body = "import { auth } from '../auth/firebase';\nimport { syncUploadCloud, deleteUploadCloud } from '../auth/cloud';\n" + body
    body = body.replace(
        "  await db.set('uploads', asset.id, { ...asset, addedAt: Date.now() });",
        "  const record = { ...asset, addedAt: Date.now() };\n  await db.set('uploads', asset.id, record);\n  const uid = auth.currentUser?.uid;\n  if (uid) await syncUploadCloud(uid, record).catch((e) => console.error('Upload cloud save failed', e));"
    )
    body = body.replace(
        "  await db.del('uploads', id);",
        "  const uid = auth.currentUser?.uid;\n  if (uid) await deleteUploadCloud(uid, id).catch((e) => console.error('Upload cloud delete failed', e));\n  await db.del('uploads', id);"
    )
    uploads.write_text(body)

print("Firebase email/Google auth gate and per-user Yjs cloud backup/restore patches applied.")
