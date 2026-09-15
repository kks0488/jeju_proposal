'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..'),DIR=path.join(__dirname,'published');
const substitutions=[
 ['하백·이아 / GAU / 다봄 중에서 선정합니다.','현재 평가 순위에 따라 시공사를 비교합니다.'],
 ['우리 집을 지을 세 업체 비교','평가 순위별 업체 비교'],
 ['하백·이아, GAU, 다봄의 실제 시공 사례를 보고<br>우리 집을 맡길 업체를 고릅니다.','평가 순위와 실제 시공 사례를 바탕으로<br>제주집에 맞는 시공사를 비교합니다.'],
 ['세 업체 비교와 상담','업체별 비교와 상담'],
 ['<small>하백·이아 · GAU · 다봄</small>','<small>평가 순위 · 포트폴리오</small>'],
 ['제주집 시공사 선정. 하백·이아, GAU, 다봄의 포트폴리오와 상담 내용을 한곳에서 비교합니다.','제주집 시공사 선정. 평가 순위별 포트폴리오와 시공 사례를 비교합니다.']
];
function wording(s){for(const [a,b] of substitutions)s=s.split(a).join(b);return s;}
function refresh(){
 const before=JSON.parse(fs.readFileSync(path.join(DIR,'catalog.json'),'utf8'));
 const originalImages=before.projects.flatMap(p=>p.photos.map(x=>x.url));
 assert.equal(originalImages.length,178);
 for(const file of [path.join(DIR,'index.html'),path.join(__dirname,'template.html')]){
  if(fs.existsSync(file))fs.writeFileSync(file,wording(fs.readFileSync(file,'utf8')));
 }
 const editor=path.join(__dirname,'selection-edit.cjs');
 if(fs.existsSync(editor)){
  let s=wording(fs.readFileSync(editor,'utf8'));
  if(!s.includes("require('./ranking-root.cjs').refresh()"))s+="\n// Preserve neutral ranking wording and the actual root page on future edits.\nrequire('./ranking-root.cjs').refresh();\n";
  fs.writeFileSync(editor,s);
 }
 // Keep the original gallery URL working while putting the full page at the root.
 let html=fs.readFileSync(path.join(DIR,'index.html'),'utf8');
 assert(html.includes('현재 평가 순위에 따라 시공사를 비교합니다.'));
 assert(!html.includes('중에서 선정합니다.'));
 assert(!/http-equiv=["']refresh|<iframe/i.test(html));
 html=html.split('./assets/').join('./site-v3/published/assets/');
 html=html.replace(/(href=["'])\.\/style\.css(?:\?[^"']*)?(["'])/g,'$1./site-v3/published/style.css?v=ranking-main-20260915$2');
 html=html.replace(/(src=["'])\.\/app\.js(?:\?[^"']*)?(["'])/g,'$1./site-v3/published/app.js?v=ranking-main-20260915$2');
 html=html.replace('</head>','<meta name="site-edition" content="ranking-main-20260915"></head>');
 fs.writeFileSync(path.join(ROOT,'index.html'),html);
 fs.writeFileSync(path.join(ROOT,'public-portfolio.html'),html);
 const rootData=JSON.parse(html.match(/<script type="application\/json" id="site-data">([\s\S]*?)<\/script>/)[1]);
 assert.equal(rootData.projects.flatMap(p=>p.photos).length,178);
 for(const p of rootData.projects)for(const x of p.photos){assert(x.url.startsWith('./site-v3/published/assets/'));assert(fs.existsSync(path.join(ROOT,x.url)));assert(fs.existsSync(path.join(ROOT,x.thumb)));}
 assert.deepEqual(before.projects.flatMap(p=>p.photos.map(x=>x.url)),originalImages);
 console.log(JSON.stringify({edition:'ranking-main-20260915',title:'제주집 시공사 선정',neutralWording:true,rootContainsFullPage:true,images:178,imagesPreserved:true}));
}
module.exports={refresh};if(require.main===module)refresh();
