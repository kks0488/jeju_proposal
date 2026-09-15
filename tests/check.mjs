import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { Script } from 'node:vm';
import handler from '../api/public-site.mjs';
const root=new URL('../',import.meta.url);
const data=JSON.parse(await fs.readFile(new URL('portfolio-data.json',root),'utf8'));
const html=await fs.readFile(new URL('public-portfolio.html',root),'utf8');
assert.equal(data.companies.length,3);assert.equal(data.projects.length,15);
assert.equal(new Set(data.projects.map(p=>p.id)).size,data.projects.length);
assert.deepEqual(data.companies.map(c=>[c.id,c.rank,c.score]),[['ia',1,78],['gau',1,78],['atelier',3,60]]);
assert.deepEqual(data.companies.map(c=>data.projects.filter(p=>p.company===c.id).length),[6,6,3]);
assert.equal(data.projects.reduce((n,p)=>n+p.photos.length,0),12);
for(const c of data.companies){assert.equal(c.points.reduce((a,b)=>a+b,0),c.score);assert(data.projects.some(p=>p.id===c.hero&&p.photos.length));}
for(const p of data.projects){assert(/^[a-z0-9-]+$/.test(p.id));assert(data.companies.some(c=>c.id===p.company));assert(p.caution&&p.credit&&p.evidence);for(const [,u] of p.sources)assert.equal(new URL(u).protocol,'https:');for(const photo of p.photos){assert.equal(new URL(photo.url).protocol,'https:');assert(photo.caption&&photo.credit);}}
assert.equal(data.projects.find(p=>p.id==='nunmoe').rc,false);
assert.match(data.projects.find(p=>p.id==='oneul').place,/서울/);
assert.match(data.projects.find(p=>p.id==='osiri').area,/단지 전체/);
new Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
assert(html.includes('aria-labelledby="detail-title"'));
try{const ranking=JSON.parse(await fs.readFile(new URL('ranking.json',root),'utf8'));const entries=Object.values(ranking).find(v=>Array.isArray(v)&&v.some(x=>x&&x.id==='ia'&&x.total!==undefined));if(entries)for(const c of data.companies){const row=entries.find(x=>x.id===c.id);assert.equal(row.total,c.score);assert.equal(row.rank,c.rank);}}catch(e){if(e.code!=='ENOENT')throw e;}
async function invoke(method,file){const headers={};let body;const req={method,query:{file}};const res={setHeader:(k,v)=>{headers[k]=v;},end:b=>{body=b;}};await handler(req,res);return {status:res.statusCode,headers,body};}
assert.equal((await invoke('GET','../../secrets')).status,404);
assert.equal((await invoke('POST','public-portfolio.html')).status,405);
assert.equal((await invoke('GET','constructor')).status,404);
assert.equal((await invoke('GET','robots.txt')).status,200);
console.log('PASS: 3 companies, 15 projects, 12 photographs, rank ties, structure distinctions, script syntax, path/method restrictions.');
