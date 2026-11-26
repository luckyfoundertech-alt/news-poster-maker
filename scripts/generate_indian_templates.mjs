import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const editor = path.join(root, 'opentempl/apps/editor');
const vibesDir = path.join(editor, 'templates/vibes');
const vibesFile = path.join(editor, 'templates/vibes.json');
const fontFile = path.join(editor, 'src/fonts/google-fonts.json');
if (!fs.existsSync(path.join(editor, 'templates/kit.mjs'))) throw new Error('Pinned OpenTempl source is missing.');

const { tpl, page, T, rect, circle, L, frame, pattern, linear, solid } = await import('../opentempl/apps/editor/templates/kit.mjs');
const formats = [
  { id: 'post', w: 1080, h: 1350, format: 'post' },
  { id: 'story', w: 1080, h: 1920, format: 'story' },
  { id: 'poster', w: 1123, h: 1587, format: 'poster' },
  { id: 'thumb', w: 1280, h: 720, format: 'thumb' },
  { id: 'square', w: 1080, h: 1080, format: 'square' },
];
const palettes = [
  ['#101828','#F8FAFC','#F04438','#FEC84B'],
  ['#111827','#FFFFFF','#DC2626','#FDE047'],
  ['#14213D','#F8F4E8','#FCA311','#E5E5E5'],
  ['#172554','#EFF6FF','#2563EB','#F97316'],
  ['#052E2B','#F0FDFA','#0D9488','#F59E0B'],
  ['#3B0764','#FAF5FF','#9333EA','#F9A8D4'],
  ['#431407','#FFF7ED','#EA580C','#FACC15'],
  ['#1F2937','#F9FAFB','#16A34A','#86EFAC'],
  ['#450A0A','#FFF1F2','#E11D48','#FDA4AF'],
  ['#0F172A','#F1F5F9','#38BDF8','#FDE68A'],
  ['#292524','#FAFAF9','#B45309','#D6D3D1'],
  ['#052e16','#F0FDF4','#22C55E','#FDE047'],
  ['#312E81','#EEF2FF','#6366F1','#FBBF24'],
  ['#18181B','#FAFAFA','#F43F5E','#A1A1AA'],
  ['#083344','#ECFEFF','#0891B2','#FB923C'],
  ['#3F1D2E','#FFF1F2','#BE185D','#FBCFE8'],
  ['#1C1917','#FEFCE8','#CA8A04','#FDE68A'],
  ['#0C4A6E','#F0F9FF','#0284C7','#FDBA74'],
  ['#365314','#F7FEE7','#65A30D','#FDE047'],
  ['#581C87','#FAF5FF','#A855F7','#FDE68A'],
];
const groups = [
  { key:'bharat-news', name:'Indian News', blurb:'Hindi and English breaking news, headlines, bulletins and editorial updates.', count:600, category:'Indian News', topics:[['Breaking News','ब्रेकिंग न्यूज़'],['National Headlines','राष्ट्रीय समाचार'],['Weather Update','मौसम अपडेट'],['Crime Report','अपराध समाचार'],['Health Bulletin','स्वास्थ्य खबर'],['Technology News','तकनीकी समाचार'],['Entertainment News','मनोरंजन समाचार'],['Public Alert','जन सूचना']], en:['Breaking News','Top Headlines','Latest Update','News Bulletin','Big Story','News Flash'], hi:['ताज़ा खबर','बड़ी खबर','मुख्य समाचार','आज की खबर','ब्रेकिंग न्यूज़','खास खबर'], tags:['news','breaking news','hindi news','bharat news','ताज़ा खबर','समाचार','ब्रेकिंग न्यूज़','headline','bulletin','भारत'] },
  { key:'state-district', name:'State & District News', blurb:'State, city, district and local reporting layouts for Indian publishers.', count:450, category:'State & District', topics:[['Chhattisgarh News','छत्तीसगढ़ समाचार'],['Madhya Pradesh News','मध्य प्रदेश समाचार'],['Maharashtra News','महाराष्ट्र समाचार'],['Uttar Pradesh News','उत्तर प्रदेश समाचार'],['Bihar News','बिहार समाचार'],['Rajasthan News','राजस्थान समाचार'],['Delhi News','दिल्ली समाचार'],['District Bulletin','जिला समाचार'],['City Update','शहर अपडेट']], en:['State Update','District Report','City News','Local Bulletin','Ground Report','Public Update'], hi:['राज्य समाचार','जिला खबर','शहर की खबर','स्थानीय समाचार','जनता की आवाज़','ग्राउंड रिपोर्ट'], tags:['state news','district news','local news','city news','राज्य समाचार','जिला समाचार','स्थानीय खबर','भारत'] },
  { key:'politics-public', name:'Politics & Public Affairs', blurb:'Election, government, civic, policy and public affairs editorial layouts.', count:350, category:'Politics & Public', topics:[['Election News','चुनाव समाचार'],['Parliament Update','संसद अपडेट'],['Assembly News','विधानसभा समाचार'],['Government Policy','सरकारी नीति'],['Public Issues','जनहित मुद्दे'],['Civic Update','नागरिक अपडेट'],['Political Debate','राजनीतिक बहस']], en:['Election Update','Public Affairs','Policy Watch','Assembly News','Civic Report','Political Desk'], hi:['चुनाव अपडेट','राजनीति','जनहित खबर','सरकारी अपडेट','विधानसभा समाचार','जनता की बात'], tags:['politics','election','government','public affairs','चुनाव','राजनीति','सरकार','जनहित','लोकसभा','विधानसभा'] },
  { key:'cricket-sports', name:'Cricket & Sports', blurb:'Match day, score cards, team lineups, player profiles and sports news.', count:400, category:'Cricket & Sports', topics:[['Cricket News','क्रिकेट समाचार'],['IPL Match','आईपीएल मैच'],['T20 Cricket','टी20 क्रिकेट'],['Test Cricket','टेस्ट क्रिकेट'],['Football News','फुटबॉल समाचार'],['Hockey Update','हॉकी अपडेट'],['Kabaddi News','कबड्डी समाचार'],['Olympics','ओलंपिक']], en:['Match Day','Live Score','Team Update','Player Spotlight','Final Score','Sports Bulletin'], hi:['मैच डे','लाइव स्कोर','खेल समाचार','टीम अपडेट','आज का मुकाबला','खिलाड़ी'], tags:['cricket','sports','match','score','team','खेल','क्रिकेट','लाइव स्कोर','मैच','खिलाड़ी','भारत'] },
  { key:'business-education', name:'Business & Education', blurb:'Business, economy, jobs, exam, school, college and career announcements.', count:350, category:'Business & Education', topics:[['Job Alert','नौकरी अलर्ट'],['Exam Update','परीक्षा अपडेट'],['School News','स्कूल समाचार'],['College News','कॉलेज समाचार'],['Market News','बाजार समाचार'],['Business Update','कारोबार अपडेट'],['Career Guidance','करियर मार्गदर्शन']], en:['Business Brief','Career Update','Education News','Market Watch','Exam Alert','Job Bulletin'], hi:['कारोबार खबर','रोजगार अपडेट','शिक्षा समाचार','बाजार अपडेट','परीक्षा अलर्ट','नौकरी खबर'], tags:['business','education','jobs','career','exam','market','economy','व्यापार','शिक्षा','रोजगार','नौकरी','परीक्षा'] },
  { key:'indian-festivals', name:'Indian Festivals', blurb:'Indian festivals, religious celebrations, greetings and seasonal events.', count:500, category:'Indian Festivals', topics:[['Diwali','दीवाली'],['Holi','होली'],['Eid','ईद'],['Navratri','नवरात्रि'],['Durga Puja','दुर्गा पूजा'],['Ganesh Chaturthi','गणेश चतुर्थी'],['Dussehra','दशहरा'],['Christmas','क्रिसमस'],['Onam','ओणम'],['Pongal','पोंगल'],['Baisakhi','बैसाखी'],['Raksha Bandhan','रक्षाबंधन'],['Janmashtami','जन्माष्टमी'],['Chhath Puja','छठ पूजा'],['Makar Sankranti','मकर संक्रांति'],['Guru Nanak Jayanti','गुरु नानक जयंती']], en:['Festival Greetings','Celebration Special','Festive Wishes','Culture & Faith','Festival Guide','Special Day'], hi:['त्योहार की शुभकामनाएं','पर्व विशेष','शुभकामनाएं','उत्सव','धार्मिक पर्व','मंगलकामनाएं'], tags:['festival','indian festival','celebration','त्योहार','भारतीय पर्व','शुभकामनाएं','भारत'] },
  { key:'national-culture', name:'National Days & Culture', blurb:'National days, Indian heritage, regional culture and community events.', count:350, category:'National & Culture', topics:[['Republic Day','गणतंत्र दिवस'],['Independence Day','स्वतंत्रता दिवस'],['Gandhi Jayanti','गांधी जयंती'],['Constitution Day','संविधान दिवस'],['Indian Heritage','भारतीय विरासत'],['Regional Culture','क्षेत्रीय संस्कृति'],['Tribal Culture','आदिवासी संस्कृति']], en:['India Special','Heritage Stories','National Day','Culture Connect','Pride of India','Community Event'], hi:['भारत विशेष','राष्ट्रीय पर्व','भारतीय संस्कृति','देश की पहचान','विरासत','गौरव'], tags:['national day','indian culture','heritage','independence day','republic day','regional','राष्ट्रीय पर्व','भारतीय संस्कृति','विरासत','भारत','स्वतंत्रता दिवस','गणतंत्र दिवस'] },
];

const layouts = [
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,0,W,H*.14,c[2]),T('NEWS DESK',W*.06,H*.035,W*.7,{size:W*.035,weight:800,color:c[1],font:'Noto Sans Devanagari'}),T(t.hi,W*.06,H*.21,W*.86,{size:W*.105,weight:900,color:c[1],font:'Noto Sans Devanagari',lh:1.08}),rect(W*.06,H*.66,W*.88,H*.012,c[3]),T(t.en,W*.06,H*.70,W*.8,{size:W*.043,weight:800,color:c[1]}),T('भारत · समाचार · अपडेट',W*.06,H*.91,W*.8,{size:W*.026,weight:600,color:c[3],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,0,W*.24,H,c[0]),T('24',W*.035,H*.05,W*.18,{size:W*.10,weight:900,color:c[2]}),T(t.hi,W*.31,H*.12,W*.62,{size:W*.085,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.31,H*.42,W*.62,H*.32),rect(W*.31,H*.80,W*.62,H*.09,c[2]),T(t.en,W*.34,H*.82,W*.55,{size:W*.035,weight:800,color:c[1]}),T('ताज़ा अपडेट',W*.31,H*.93,W*.6,{size:W*.026,weight:700,color:c[0],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,H*.07,W,H*.13,c[2]),T('BREAKING',W*.06,H*.095,W*.86,{size:W*.08,weight:900,color:c[1]}),T(t.hi,W*.06,H*.29,W*.88,{size:W*.11,weight:900,color:c[1],font:'Noto Sans Devanagari',lh:1.1}),frame(W*.06,H*.58,W*.88,H*.23),rect(W*.06,H*.85,W*.88,H*.075,c[3]),T('LIVE  •  INDIA  •  NEWS',W*.09,H*.87,W*.8,{size:W*.028,weight:800,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),circle(W*.58,H*.08,W*.54,c[3]),circle(W*.68,H*.18,W*.30,c[2]),T(t.en,W*.07,H*.13,W*.72,{size:W*.10,weight:900,color:c[0]}),T(t.hi,W*.07,H*.34,W*.82,{size:W*.095,weight:900,color:c[0],font:'Noto Sans Devanagari'}),rect(W*.07,H*.68,W*.86,H*.16,c[0]),T('NEWS UPDATE',W*.11,H*.72,W*.78,{size:W*.052,weight:800,color:c[1]}),T('भारत की हर बड़ी खबर',W*.07,H*.90,W*.8,{size:W*.03,weight:700,color:c[0],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,0,W*.055,H,c[2]),T('01',W*.10,H*.06,W*.25,{size:W*.16,weight:900,color:c[3]}),T(t.hi,W*.10,H*.30,W*.82,{size:W*.10,weight:900,color:c[1],font:'Noto Sans Devanagari'}),L(W*.10,H*.56,W*.90,H*.56,c[2],8),frame(W*.10,H*.62,W*.80,H*.22),T(t.en,W*.10,H*.88,W*.82,{size:W*.038,weight:800,color:c[1]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(W*.06,H*.06,W*.88,H*.88,c[0]),rect(W*.10,H*.10,W*.80,H*.13,c[2]),T('NEWS / INDIA',W*.14,H*.135,W*.7,{size:W*.035,weight:900,color:c[1]}),T(t.hi,W*.12,H*.31,W*.76,{size:W*.09,weight:900,color:c[1],font:'Noto Sans Devanagari'}),frame(W*.12,H*.56,W*.76,H*.22),T(t.en,W*.12,H*.82,W*.76,{size:W*.04,weight:800,color:c[3]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,0,W,H*.42,c[2]),T(t.en,W*.06,H*.08,W*.86,{size:W*.10,weight:900,color:c[1]}),T(t.hi,W*.06,H*.50,W*.86,{size:W*.09,weight:900,color:c[0],font:'Noto Sans Devanagari'}),rect(W*.06,H*.77,W*.88,H*.012,c[0]),T('TOP STORY  /  INDIA',W*.06,H*.82,W*.88,{size:W*.03,weight:800,color:c[0]}),circle(W*.80,H*.86,W*.10,c[3])],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,H*.08,W,H*.22,c[3]),T('LIVE',W*.06,H*.12,W*.30,{size:W*.12,weight:900,color:c[0]}),T(t.hi,W*.06,H*.38,W*.88,{size:W*.10,weight:900,color:c[1],font:'Noto Sans Devanagari'}),rect(W*.06,H*.68,W*.88,H*.20,c[1]),T(t.en,W*.10,H*.72,W*.80,{size:W*.052,weight:900,color:c[0]}),T('NEWSROOM  •  24/7',W*.06,H*.93,W*.88,{size:W*.025,weight:700,color:c[3]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),circle(W*.04,H*.07,W*.26,c[2]),circle(W*.16,H*.15,W*.08,c[3]),T(t.hi,W*.34,H*.12,W*.58,{size:W*.09,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.07,H*.42,W*.86,H*.32),T(t.en,W*.07,H*.80,W*.86,{size:W*.045,weight:900,color:c[0]}),L(W*.07,H*.91,W*.93,H*.91,c[2],7)],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),pattern('diagonal',c[2],c[0],5),rect(W*.06,H*.08,W*.88,H*.82,c[1]),T('SPECIAL REPORT',W*.11,H*.13,W*.78,{size:W*.035,weight:900,color:c[2]}),T(t.hi,W*.11,H*.26,W*.78,{size:W*.095,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.11,H*.56,W*.78,H*.20),T(t.en,W*.11,H*.81,W*.78,{size:W*.04,weight:800,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,0,W,H*.12,c[0]),T('भारत समाचार',W*.06,H*.035,W*.88,{size:W*.05,weight:900,color:c[1],font:'Noto Sans Devanagari'}),T(t.en,W*.06,H*.20,W*.88,{size:W*.095,weight:900,color:c[0]}),rect(W*.06,H*.43,W*.88,H*.012,c[2]),T(t.hi,W*.06,H*.50,W*.88,{size:W*.09,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.06,H*.70,W*.88,H*.18),T('आज की बड़ी खबर',W*.06,H*.92,W*.88,{size:W*.026,weight:700,color:c[2],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),circle(W*.58,H*.04,W*.55,c[2]),T('NEWS',W*.07,H*.10,W*.82,{size:W*.17,weight:900,color:c[1]}),T(t.hi,W*.07,H*.39,W*.84,{size:W*.10,weight:900,color:c[1],font:'Noto Sans Devanagari'}),rect(W*.07,H*.70,W*.86,H*.11,c[3]),T(t.en,W*.10,H*.725,W*.8,{size:W*.042,weight:900,color:c[0]}),T('भारत · आज · अभी',W*.07,H*.90,W*.84,{size:W*.03,weight:700,color:c[1],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(W*.06,H*.06,W*.88,H*.88,c[2]),rect(W*.10,H*.10,W*.80,H*.80,c[1]),T('THE DAILY',W*.15,H*.15,W*.7,{size:W*.04,weight:900,color:c[2]}),T(t.hi,W*.15,H*.30,W*.7,{size:W*.10,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.15,H*.56,W*.70,H*.20),T(t.en,W*.15,H*.80,W*.70,{size:W*.038,weight:900,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,H*.12,W,H*.10,c[3]),T('UPDATE',W*.06,H*.14,W*.88,{size:W*.07,weight:900,color:c[0]}),T(t.hi,W*.06,H*.31,W*.88,{size:W*.105,weight:900,color:c[1],font:'Noto Sans Devanagari'}),rect(W*.06,H*.63,W*.88,H*.22,c[2]),T(t.en,W*.10,H*.68,W*.80,{size:W*.052,weight:900,color:c[1]}),T('LIVE NEWS FEED',W*.06,H*.92,W*.88,{size:W*.026,weight:800,color:c[3]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,0,W*.36,H,c[0]),T('NEWS',W*.04,H*.08,W*.28,{size:W*.065,weight:900,color:c[1]}),T('24',W*.04,H*.23,W*.28,{size:W*.18,weight:900,color:c[3]}),T(t.hi,W*.43,H*.16,W*.51,{size:W*.085,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.43,H*.52,W*.51,H*.24),T(t.en,W*.43,H*.82,W*.51,{size:W*.035,weight:800,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(W*.06,H*.08,W*.88,H*.84,c[1]),circle(W*.72,H*.12,W*.20,c[2]),T('भारत',W*.11,H*.13,W*.6,{size:W*.08,weight:900,color:c[2],font:'Noto Sans Devanagari'}),T(t.hi,W*.11,H*.30,W*.78,{size:W*.10,weight:900,color:c[0],font:'Noto Sans Devanagari'}),L(W*.11,H*.58,W*.89,H*.58,c[3],8),T(t.en,W*.11,H*.67,W*.78,{size:W*.05,weight:900,color:c[0]}),T('समाचार • अपडेट',W*.11,H*.85,W*.78,{size:W*.03,weight:700,color:c[2],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,H*.05,W,H*.25,c[0]),T(t.hi,W*.06,H*.10,W*.88,{size:W*.10,weight:900,color:c[1],font:'Noto Sans Devanagari'}),frame(W*.06,H*.37,W*.88,H*.34),rect(W*.06,H*.76,W*.88,H*.12,c[2]),T(t.en,W*.10,H*.785,W*.80,{size:W*.048,weight:900,color:c[1]}),T('SPECIAL EDITION',W*.06,H*.92,W*.88,{size:W*.025,weight:800,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(W*.07,H*.08,W*.86,H*.84,c[1]),T('01 / HEADLINES',W*.12,H*.13,W*.76,{size:W*.03,weight:900,color:c[2]}),T(t.en,W*.12,H*.25,W*.76,{size:W*.08,weight:900,color:c[0]}),T(t.hi,W*.12,H*.43,W*.76,{size:W*.09,weight:900,color:c[0],font:'Noto Sans Devanagari'}),rect(W*.12,H*.69,W*.76,H*.012,c[2]),T('READ • SHARE • CREATE',W*.12,H*.78,W*.76,{size:W*.028,weight:800,color:c[2]}),circle(W*.78,H*.83,W*.10,c[3])],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),circle(W*.03,H*.05,W*.32,c[3]),circle(W*.18,H*.18,W*.14,c[2]),T(t.hi,W*.10,H*.35,W*.80,{size:W*.10,weight:900,color:c[0],font:'Noto Sans Devanagari'}),rect(W*.10,H*.65,W*.80,H*.12,c[0]),T(t.en,W*.14,H*.68,W*.72,{size:W*.045,weight:900,color:c[1]}),T('भारत की आवाज़',W*.10,H*.88,W*.80,{size:W*.03,weight:800,color:c[2],font:'Noto Sans Devanagari'})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),rect(0,0,W*.16,H,c[2]),T('LIVE',W*.025,H*.06,W*.11,{size:W*.045,weight:900,color:c[1]}),T(t.hi,W*.23,H*.16,W*.70,{size:W*.10,weight:900,color:c[1],font:'Noto Sans Devanagari'}),frame(W*.23,H*.48,W*.70,H*.26),T(t.en,W*.23,H*.80,W*.70,{size:W*.042,weight:900,color:c[3]}),L(W*.23,H*.91,W*.93,H*.91,c[2],7)],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(W*.05,H*.05,W*.90,H*.90,c[0]),T('NEWS FLASH',W*.10,H*.10,W*.80,{size:W*.045,weight:900,color:c[3]}),T(t.hi,W*.10,H*.27,W*.80,{size:W*.11,weight:900,color:c[1],font:'Noto Sans Devanagari'}),rect(W*.10,H*.62,W*.80,H*.13,c[2]),T(t.en,W*.14,H*.65,W*.72,{size:W*.045,weight:900,color:c[1]}),T('INDIA  /  UPDATE',W*.10,H*.83,W*.80,{size:W*.028,weight:800,color:c[3]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[1]),rect(0,H*.06,W,H*.06,c[2]),rect(0,H*.88,W,H*.06,c[2]),T(t.en,W*.07,H*.19,W*.86,{size:W*.09,weight:900,color:c[0]}),T(t.hi,W*.07,H*.40,W*.86,{size:W*.10,weight:900,color:c[0],font:'Noto Sans Devanagari'}),frame(W*.07,H*.65,W*.86,H*.17),T('NEWS • INDIA',W*.07,H*.92,W*.86,{size:W*.025,weight:800,color:c[0]})],
  (W,H,c,p,t)=>[rect(0,0,W,H,c[0]),circle(W*.58,H*.08,W*.48,c[3]),rect(W*.07,H*.14,W*.86,H*.72,c[1]),T('TOP STORY',W*.12,H*.19,W*.76,{size:W*.035,weight:900,color:c[2]}),T(t.hi,W*.12,H*.33,W*.76,{size:W*.095,weight:900,color:c[0],font:'Noto Sans Devanagari'}),T(t.en,W*.12,H*.68,W*.76,{size:W*.045,weight:900,color:c[2]}),T('आज की मुख्य खबर',W*.12,H*.79,W*.76,{size:W*.028,weight:700,color:c[0],font:'Noto Sans Devanagari'})],
];
const fonts = JSON.parse(fs.readFileSync(fontFile,'utf8'));
if (!fonts.some(f=>f[0]==='Noto Sans Devanagari')) fonts.push(['Noto Sans Devanagari','sans',[100,200,300,400,500,600,700,800,900],0]);
fs.writeFileSync(fontFile, JSON.stringify(fonts));
const vibes = JSON.parse(fs.readFileSync(vibesFile,'utf8'));
let nextOrder = Math.max(...Object.values(vibes).map(v=>v.order||0))+1;
for (const g of groups) {
  vibes[g.key] = { name:g.name, blurb:g.blurb, order:nextOrder++ };
  const templates = [];
  for (let i=0;i<g.count;i++) {
    const pi = i % palettes.length;
    const c = palettes[pi];
    const fi = (i + Math.floor(i/7)) % formats.length;
    const f = formats[fi];
    const W=f.w,H=f.h;
    const li = (i * 7 + Math.floor(i/11)) % layouts.length;
    const topic = g.topics[i % g.topics.length];
    const title = topic[0] + ' · ' + g.en[i % g.en.length];
    const hindi = topic[1] + ' · ' + g.hi[(i + Math.floor(i/5)) % g.hi.length];
    const elements = layouts[li](W,H,c,pi,{en:title,hi:hindi});
    // Unique editorial issue marker and an editable source/date line on every layout.
    const markY = Math.min(H*.94,H-42);
    elements.push(T(String(i+1).padStart(3,'0'),W*.86,markY,W*.09,{size:Math.max(15,W*.018),weight:800,color:c[2],align:'right'}));
    const tags = [...new Set([...g.tags, topic[0].toLowerCase(), topic[1], g.name.toLowerCase(), title.toLowerCase(), hindi, f.id, ['red bulletin','editorial grid','photo story','modern hindi','regional poster'][li%5]])];
    templates.push(tpl({
      id:`${g.key}-${String(i+1).padStart(3,'0')}`,
      name:`${topic[0]} ${String(i+1).padStart(3,'0')} · ${['Bold Bulletin','Editorial Grid','Photo Story','Modern Hindi','Regional Press'][li%5]}`,
      format:f.format,
      category:g.category,
      tags,
      pages:[page(c[1],elements)],
    }));
  }
  fs.writeFileSync(path.join(vibesDir,`${g.key}.mjs`),`import { tpl, page, T, rect, circle, L, frame, pattern } from '../kit.mjs';\n\nexport default ${JSON.stringify(templates)};\n`);
}
fs.writeFileSync(vibesFile, JSON.stringify(vibes,null,2)+'\n');
const total=groups.reduce((n,g)=>n+g.count,0);
if(total!==3000) throw new Error('Generated template target mismatch: '+total);
console.log(`Generated ${total} original editable Indian templates across ${groups.length} searchable categories. Existing template files were not changed.`);
