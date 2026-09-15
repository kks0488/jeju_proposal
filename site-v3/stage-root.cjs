'use strict';
// A static-only Vercel build: publish the chosen page and its local images, not old research/private drawings.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..'),OUT=path.join(ROOT,'dist');
const html=fs.readFileSync(path.join(ROOT,'index.html'),'utf8');
assert(html.includes('ranking-main-20260915')&&html.includes('현재 평가 순위에 따라 시공사를 비교합니다.'));
fs.rmSync(OUT,{recursive:true,force:true});fs.mkdirSync(OUT,{recursive:true});
fs.copyFileSync(path.join(ROOT,'index.html'),path.join(OUT,'index.html'));
fs.copyFileSync(path.join(ROOT,'public-portfolio.html'),path.join(OUT,'public-portfolio.html'));
fs.mkdirSync(path.join(OUT,'site-v3'),{recursive:true});
fs.cpSync(path.join(ROOT,'site-v3/published'),path.join(OUT,'site-v3/published'),{recursive:true});
fs.writeFileSync(path.join(OUT,'robots.txt'),'User-agent: *\nDisallow: /\n');
fs.writeFileSync(path.join(OUT,'.nojekyll'),'');
const d=JSON.parse(html.match(/<script type="application\/json" id="site-data">([\s\S]*?)<\/script>/)[1]);
for(const p of d.projects)for(const im of p.photos)for(const key of ['url','thumb'])assert(fs.existsSync(path.join(OUT,im[key])));
const status={edition:'ranking-main-20260915',title:d.title||'제주집 시공사 선정',projects:d.projects.length,images:d.projects.reduce((n,p)=>n+p.photos.length,0),delivery:'static-local-assets',builtAt:new Date().toISOString()};
fs.writeFileSync(path.join(OUT,'site-status.json'),JSON.stringify(status));console.log('STATIC_ROOT '+JSON.stringify(status));
