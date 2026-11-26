import { useEffect, useState } from 'react';
import { auth } from '../auth/firebase';
import { signOut, updateProfile } from 'firebase/auth';
import { listDesigns, getThumb, onDesignsChange, type DesignEntry } from '../io/designs';
import { listUploads, onUploadsChange } from '../io/uploads';
import { navigate } from '../App';

type UploadEntry = Awaited<ReturnType<typeof listUploads>>[number];

export function Profile() {
  const user = auth.currentUser;
  const [designs, setDesigns] = useState<DesignEntry[]>([]);
  const [uploads, setUploads] = useState<UploadEntry[]>([]);
  const [thumbs, setThumbs] = useState<Record<string,string>>({});
  const [name, setName] = useState(user?.displayName || '');
  const [tab, setTab] = useState<'designs'|'uploads'|'account'>('designs');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    let live = true;
    const refresh = async () => {
      const [d,u] = await Promise.all([listDesigns(),listUploads()]);
      if (!live) return;
      setDesigns(d); setUploads(u);
      const pairs = await Promise.all(d.map(async item => {
        const blob = await getThumb(item.id);
        return [item.id, blob ? URL.createObjectURL(blob) : ''] as const;
      }));
      if (live) setThumbs(Object.fromEntries(pairs.filter(([,url]) => !!url)));
      else pairs.forEach(([,url]) => url && URL.revokeObjectURL(url));
    };
    const onCloudRestored = () => { void refresh(); };
    void refresh();
    const a = onDesignsChange(() => { void refresh(); });
    const b = onUploadsChange(() => { void refresh(); });
    window.addEventListener('news-cloud-restored', onCloudRestored);
    return () => { live=false; a(); b(); window.removeEventListener('news-cloud-restored', onCloudRestored); };
  }, []);

  const saveName = async () => {
    if (!user || !name.trim()) return;
    setSaving(true); setMessage('');
    try { await updateProfile(user,{displayName:name.trim()}); setMessage('Profile updated.'); }
    catch { setMessage('Could not update profile. Check your connection.'); }
    finally { setSaving(false); }
  };

  return <div className="ns-profile">
    <header className="ns-profile-head">
      <button onClick={()=>navigate('/')}>← Studio</button><b>My Profile</b>
      <button className="ns-profile-signout" onClick={()=>signOut(auth)}>Sign out</button>
    </header>
    <main className="ns-profile-main">
      <section className="ns-profile-card">
        <div className="ns-profile-avatar">{user?.photoURL?<img src={user.photoURL} alt=""/>:(user?.displayName||user?.email||'N').slice(0,1).toUpperCase()}</div>
        <div><h1>{user?.displayName||'Your Studio Account'}</h1><p>{user?.email||'Signed-in account'}</p><small>Account ID: {user?.uid}</small></div>
      </section>
      <section className="ns-profile-stats">
        <div><b>{designs.length}</b><span>Saved designs</span></div>
        <div><b>{uploads.length}</b><span>Uploaded files</span></div>
        <div><b>{user?.metadata.creationTime?new Date(user.metadata.creationTime).toLocaleDateString():'—'}</b><span>Member since</span></div>
      </section>
      <nav className="ns-profile-tabs">
        <button className={tab==='designs'?'active':''} onClick={()=>setTab('designs')}>My designs</button>
        <button className={tab==='uploads'?'active':''} onClick={()=>setTab('uploads')}>My files</button>
        <button className={tab==='account'?'active':''} onClick={()=>setTab('account')}>Account details</button>
      </nav>
      {tab==='designs'?<section className="ns-profile-list"><h2>All saved designs</h2>
        {designs.length?<div className="ns-profile-grid">{designs.map(d=><button className="ns-profile-design" key={d.id} onClick={()=>navigate('/d/'+d.id)}>
          <div className="ns-profile-preview">{thumbs[d.id]?<img src={thumbs[d.id]} alt=""/>:<span>NEWS Studio</span>}</div>
          <b>{d.title}</b><small>{d.width} × {d.height} · {d.pages} pages</small>
        </button>)}</div>:<p className="ns-profile-empty">Your saved designs will appear here.</p>}
      </section>:null}
      {tab==='uploads'?<section className="ns-profile-list"><h2>My uploaded files</h2>
        {uploads.length?<div className="ns-profile-files">{uploads.map(f=><div className="ns-profile-file" key={f.id}>
          <span className="ns-profile-file-icon">{f.mime.startsWith('image/')?'▧':'▤'}</span><div><b>{f.name}</b><small>{f.mime||'File'} · {f.width&&f.height?f.width+' × '+f.height:'Saved upload'}</small></div>
        </div>)}</div>:<p className="ns-profile-empty">Files uploaded in the editor will appear here.</p>}
      </section>:null}
      {tab==='account'?<section className="ns-profile-list ns-profile-account"><h2>Account details</h2>
        <label>Display name<input value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label>
        <label>Email address<input value={user?.email||''} readOnly/></label>
        <label>Account ID<input value={user?.uid||''} readOnly/></label>
        <button className="ns-profile-save" disabled={saving||!name.trim()} onClick={saveName}>{saving?'Saving…':'Save profile'}</button>
        {message?<p role="status">{message}</p>:null}
      </section>:null}
      <p className="ns-profile-foot">Your files stay in your local workspace and sync to this account when connected.</p>
    </main>
  </div>;
}
