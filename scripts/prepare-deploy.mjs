import fs from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { Script } from 'node:vm';
import assert from 'node:assert/strict';
// Preserve the former gateway byte-for-byte; never execute an unpinned remote module.
const base='https://raw.githubusercontent.com/kks0488/jeju_proposal/';
const version='de820e1706dcbffb60acd2cb6a45bab8e43a286a';
const expected='d8374e2a7293bcb454441941f5f96e45022c85cb';
await fs.mkdir('lib',{recursive:true});
let bytes;try{bytes=await fs.readFile('lib/legacy-site.mjs');}catch(e){if(e.code!=='ENOENT')throw e;const r=await fetch(base+version+'/api/public-site.mjs',{signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error('Cannot fetch preserved gateway '+r.status);bytes=Buffer.from(await r.arrayBuffer());}
assert.equal(createHash('sha1').update(Buffer.concat([Buffer.from('blob '+bytes.length+'\0'),bytes])).digest('hex'),expected);
await fs.writeFile('lib/legacy-site.mjs',bytes);
const {mergeData,upgradeHtml}=await import('../api/public-site.mjs');
async function text(file){try{return await fs.readFile(file,'utf8');}catch(e){if(e.code!=='ENOENT')throw e;const r=await fetch(base+'master/'+file+'?check='+Date.now(),{signal:AbortSignal.timeout(20000)});if(!r.ok)throw Error(file+': '+r.status);return r.text();}}
const [baseData,extra,ranks,html,js]=await Promise.all(['portfolio-data.json','portfolio-expansion.json','ranking.json','public-portfolio.html','portfolio-enhancements.js'].map(text));
const data=mergeData(JSON.parse(baseData),JSON.parse(extra),JSON.parse(ranks));
assert.deepEqual(data.companies.map(c=>c.id),['ia','gau','dabom','atelier']);
assert.equal(data.projects.length,20);
assert.equal(data.projects.reduce((n,p)=>n+p.photos.length,0),40);
assert.equal(data.projects.filter(p=>p.company==='dabom').length,5);
assert.equal(data.projects.filter(p=>p.company==='dabom'&&p.rc).length,2);
assert.equal(data.companies.find(c=>c.id==='dabom').rank,4);
assert.equal(data.companies.find(c=>c.id==='atelier').rank,3);
const page=upgradeHtml(html,js);
const scripts=[...page.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.equal(scripts.length,2);scripts.forEach(s=>new Script(s[1]));
assert(page.includes('data-company="dabom"'));
assert(page.includes('id="photo-coverage"'));
assert(page.includes('portfolio-data.json?edition=dabom-gallery-v2'));
assert(page.includes('&edition=dabom-gallery-v2'));
assert(!page.includes('}}init();'));
assert(page.includes("window.dispatchEvent(new Event('portfolio:ready'))"));
console.log(JSON.stringify({test:'portfolio-v2-source-validation',passed:true,companies:4,projects:20,photos:40,dabomProjects:5,dabomFullRC:2,scoreRankingUnchanged:true,scriptSyntax:'both scripts compiled',scope:'source integration checks; not a real-browser end-to-end test'}));
