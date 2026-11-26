from pathlib import Path

root = Path("opentempl/apps/editor/src/home")
root.mkdir(parents=True, exist_ok=True)
news = root / "NewsFeed.tsx"
news.write_text(r"""import { useEffect, useMemo, useRef, useState } from 'react';
import { navigate } from '../App';

type FeedItem = {
  title?: string;
  description?: string;
  content?: string;
  link?: string;
  guid?: string;
  pubDate?: string;
  published?: string;
  updated?: string;
  author?: string;
  thumbnail?: string;
  enclosure?: { link?: string; url?: string } | Array<{ link?: string; url?: string }>;
};
type NewsItem = { title: string; summary: string; source: string; date: string; link: string; image: string };
const FEEDS = [
  { name: 'India — English', url: 'https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en' },
  { name: 'India — Hindi', url: 'https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi' },
  { name: 'BBC Hindi', url: 'https://feeds.bbci.co.uk/hindi/rss.xml' },
  { name: 'BBC World', url: 'https://feeds.bbci.co.uk/news/world/rss.xml' },
];
function clean(value: string) {
  const node = document.createElement('div');
  node.innerHTML = value || '';
  return (node.textContent || '').replace(/\s+/g, ' ').trim();
}
function textOf(node: Element | null, selector: string) {
  return node?.querySelector(selector)?.textContent?.trim() || '';
}
function parseXml(xml: string, feedName: string): NewsItem[] {
  const doc = new DOMParser().parseFromString(xml, 'application/xml');
  if (doc.querySelector('parsererror')) throw new Error('The source returned invalid RSS/XML.');
  const root = doc.documentElement;
  const isAtom = /feed$/i.test(root.localName);
  const nodes = Array.from(doc.querySelectorAll(isAtom ? 'entry' : 'item'));
  const channelTitle = textOf(doc.querySelector('channel'), 'title') || feedName;
  return nodes.map((node) => {
    const title = textOf(node, 'title');
    const description = textOf(node, 'description') || textOf(node, 'summary') || textOf(node, 'content\\:encoded') || textOf(node, 'content');
    const linkNode = node.querySelector('link[rel="alternate"]') || node.querySelector('link');
    const link = linkNode?.getAttribute('href') || linkNode?.textContent?.trim() || textOf(node, 'guid');
    const enclosure = node.querySelector('enclosure, content[url], thumbnail[url]');
    const image = enclosure?.getAttribute('url') || enclosure?.getAttribute('href') || textOf(node, 'thumbnail');
    const date = textOf(node, 'pubDate') || textOf(node, 'published') || textOf(node, 'updated') || textOf(node, 'dc\\:date');
    const author = textOf(node, 'author name') || textOf(node, 'author') || channelTitle;
    return { title: clean(title), summary: clean(description).slice(0, 420), source: clean(author) || feedName, date, link, image };
  }).filter(item => item.title && item.link);
}
function itemKey(item: NewsItem) {
  try {
    const u = new URL(item.link);
    u.hash = '';
    ['utm_source','utm_medium','utm_campaign','ocid','ved','usg'].forEach(k => u.searchParams.delete(k));
    return u.toString().replace(/\/$/, '');
  } catch { return item.title.toLocaleLowerCase().replace(/\s+/g,' ').trim(); }
}
async function fetchFeed(feed: typeof FEEDS[number], signal: AbortSignal): Promise<NewsItem[]> {
  // cors.dev fetches the publisher RSS directly rather than returning rss2json's
  // one-hour cached conversion. No app-side cache is used for a manual refresh.
  const url = 'https://proxy.cors.dev/' + feed.url;
  const response = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    signal,
    headers: { 'Cache-Control': 'no-cache, no-store', Pragma: 'no-cache' },
  });
  if (!response.ok) throw new Error(feed.name + ': HTTP ' + response.status);
  const xml = await response.text();
  if (!xml || xml.length < 30) throw new Error(feed.name + ': empty feed response');
  return parseXml(xml, feed.name).map(item => ({ ...item, source: feed.name }));
}
export function NewsFeed() {
  const [filter, setFilter] = useState('all');
  const [items, setItems] = useState<NewsItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [lastRefreshed, setLastRefreshed] = useState<number | null>(null);
  const busyRef = useRef(false);
  const controllerRef = useRef<AbortController | null>(null);
  const load = async () => {
    if (busyRef.current) return;
    busyRef.current = true;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setBusy(true);
    setErrors([]);
    try {
      const results = await Promise.allSettled(FEEDS.map(feed => fetchFeed(feed, controller.signal)));
      const fresh: NewsItem[] = [];
      const failed: string[] = [];
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') fresh.push(...result.value);
        else failed.push(FEEDS[index].name + ': ' + ((result.reason as Error)?.message || 'Feed unavailable'));
      });
      const unique = new Map<string, NewsItem>();
      for (const item of fresh) {
        const key = itemKey(item);
        if (!unique.has(key)) unique.set(key, item);
      }
      const sorted = [...unique.values()].sort((a,b) => {
        const ta = Date.parse(a.date) || 0;
        const tb = Date.parse(b.date) || 0;
        return tb - ta;
      }).slice(0, 80);
      const successfulSources = results.filter(result => result.status === 'fulfilled').length;
      if (successfulSources > 0) setItems(sorted);
      else if (failed.length === FEEDS.length) throw new Error('All news sources failed. Check your connection and try again.');
      setErrors(failed);
      setLastRefreshed(Date.now());
    } catch (error) {
      setErrors([((error as Error)?.message || 'News refresh failed')]);
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  };
  useEffect(() => {
    void load();
    return () => controllerRef.current?.abort();
  }, []);
  const visible = useMemo(() => filter === 'all' ? items : items.filter(item => item.source === filter), [items, filter]);
  const makePoster = (item: NewsItem) => {
    const q = new URLSearchParams({ format: 'a3-poster', headline: item.title, summary: item.summary, source: item.source, date: item.date, image: item.image });
    navigate('/new?' + q.toString());
  };
  return <section className="home-section" style={{ border: '1px solid var(--line)', borderRadius: 18, padding: 18, marginBottom: 28 }}>
    <div className="home-section-head">
      <div>
        <h2>Latest news</h2>
        <p className="muted">Fresh headlines from all configured sources. Stories are deduplicated before display.</p>
        <p className="muted" aria-live="polite" style={{ fontSize: 11 }}>
          {lastRefreshed ? 'Last refreshed: ' + new Date(lastRefreshed).toLocaleString() : busy ? 'Fetching live news sources…' : 'Not refreshed yet'}
        </p>
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <select aria-label="Filter news source" value={filter} onChange={e => setFilter(e.target.value)} style={{ maxWidth: 190 }}>
          <option value="all">All sources</option>
          {FEEDS.map(feed => <option key={feed.url} value={feed.name}>{feed.name}</option>)}
        </select>
        <button className="btn btn-outline" onClick={() => void load()} disabled={busy}>{busy ? 'Refreshing…' : '↻ Refresh all'}</button>
      </div>
    </div>
    {busy ? <p className="muted" role="status">Checking {FEEDS.length} configured sources for fresh stories…</p> : null}
    {errors.length ? <div role="alert" style={{ border: '1px solid #f0b4b4', borderRadius: 10, padding: 10, margin: '10px 0', color: '#9b1c1c' }}>
      <b>{errors.length === FEEDS.length ? 'News refresh failed' : 'Some sources could not refresh'}</b>
      <ul>{errors.map((error,i) => <li key={i}>{error}</li>)}</ul>
      <button className="btn btn-outline" onClick={() => void load()} disabled={busy}>Retry refresh</button>
    </div> : null}
    {!busy && !visible.length && !errors.length ? <p className="muted">No stories found for this source. Try refreshing.</p> : null}
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(min(100%,260px),1fr))', gap: 12 }}>
      {visible.map((item) => <article key={itemKey(item)} style={{ border: '1px solid var(--line)', borderRadius: 12, padding: 12, minWidth: 0 }}>
        {item.image ? <img src={item.image} alt="" loading="lazy" referrerPolicy="no-referrer" style={{ width: '100%', height: 130, objectFit: 'cover', borderRadius: 8, marginBottom: 8 }} /> : null}
        <h3 style={{ fontSize: 16, lineHeight: 1.35, margin: '4px 0 8px' }}>{item.title}</h3>
        {item.summary ? <p className="muted" style={{ fontSize: 13, lineHeight: 1.45 }}>{item.summary}</p> : null}
        <p className="muted" style={{ fontSize: 11 }}>{item.source}{item.date ? ' · ' + (Number.isNaN(Date.parse(item.date)) ? item.date : new Date(item.date).toLocaleString()) : ''}</p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="btn btn-primary" onClick={() => makePoster(item)}>Create poster</button>
          {item.link ? <a className="text-link" href={item.link} target="_blank" rel="noreferrer">Read source</a> : null}
        </div>
      </article>)}
    </div>
  </section>;
}
""", encoding="utf-8")
print("Installed live all-source RSS refresh with cache bypass, deduplication, timestamps, partial-source errors and retry.")
