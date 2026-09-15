import legacy from '../lib/legacy-site.mjs';
import { createHash } from 'node:crypto';
const ROOT='https://raw.githubusercontent.com/kks0488/jeju_proposal/master/';
const FILES=new Set(['public-portfolio.html','portfolio-data.json','portfolio-expansion.json','portfolio-enhancements.js','ranking.json']);
const HOSTS=new Set(['raw.githubusercontent.com','iacompany.co.kr','www.iacompany.co.kr','vmspace.com','www.vmspace.com','images.squarespace-cdn.com','static.wixstatic.com','t1.daumcdn.net','media.brique.co']);
const cache=new Map(), pending=new Map();
export const config={maxDuration:60};
class HTTPError extends Error {constructor(status,message){super(message);this.status=status;}}
async function cached(key,fn,ttl=60000){
  const hit=cache.get(key);if(hit&&Date.now()-hit.time<ttl)return hit.value;
  if(pending.has(key))return pending.get(key);
  const p=(async()=>{try{const value=await fn();cache.set(key,{value,time:Date.now()});while(cache.size>64)cache.delete(cache.keys().next().value);return value;}finally{pending.delete(key);}})();
  pending.set(key,p);return p;
}
async function download(address,limit=4*1024*1024){
  let url=new URL(address);
  for(let redirects=0;redirects<4;redirects++){
    if(url.protocol!=='https:'||!HOSTS.has(url.hostname))throw new HTTPError(400,'Disallowed image origin');
    const r=await fetch(url,{redirect:'manual',signal:AbortSignal.timeout(14000),headers:{'User-Agent':'Jeju-Portfolio/2.0 (attributed project reference viewer)'}});
    if(r.status>=300&&r.status<400){const to=r.headers.get('location');await r.body?.cancel();if(!to)throw new HTTPError(502,'Missing redirect');url=new URL(to,url);continue;}
    if(!r.ok){await r.body?.cancel();throw new HTTPError(r.status===404?404:502,'Upstream '+r.status);}
    if(Number(r.headers.get('content-length')||0)>limit){await r.body?.cancel();throw new HTTPError(502,'Image exceeds limit');}
    const chunks=[];let size=0;
    for await(const chunk of r.body){size+=chunk.length;if(size>limit)throw new HTTPError(502,'Response exceeds limit');chunks.push(chunk);}
    return {body:Buffer.concat(chunks),type:r.headers.get('content-type')||'application/octet-stream'};
  }
  throw new HTTPError(502,'Too many redirects');
}
async function source(file){
  if(!FILES.has(file))throw new HTTPError(404,'Unknown source');
  return cached('source:'+file,async()=>{const r=await download(ROOT+file+'?v='+Math.floor(Date.now()/60000),2*1024*1024);return r.body.toString('utf8');});
}
export function mergeData(base,expansion,ranking){
  const d=structuredClone(base);
  const add=(original,items)=>{for(const item of items){const at=original.findIndex(x=>x.id===item.id);if(at<0)original.push(structuredClone(item));else original[at]={...original[at],...structuredClone(item)};}};
  add(d.companies,expansion.companies);add(d.projects,expansion.projects);
  for(const [id,patch] of Object.entries(expansion.projectPatches)){
    const p=d.projects.find(p=>p.id===id);if(!p)throw Error('Missing base project '+id);
    const {extraSources,...rest}=patch;Object.assign(p,structuredClone(rest));
    if(extraSources)p.sources=[...p.sources,...extraSources].filter((s,i,a)=>a.findIndex(x=>x[1]===s[1])===i);
  }
  const order=expansion.displayOrder;
  d.companies.sort((a,b)=>order.indexOf(a.id)-order.indexOf(b.id));
  d.projects.sort((a,b)=>order.indexOf(a.company)-order.indexOf(b.company));
  for(const c of d.companies){const score=ranking.candidates.find(x=>x.id===c.id);if(score){c.rank=score.rank;c.score=score.total;c.points=score.points;}}
  d.updated=expansion.updated;d.version=expansion.version;d.notice=expansion.notice;
  d.scope='기존 검토에 다봄 5개 프로젝트와 사진 표시를 추가했습니다. 전 업체의 현 상태를 재실사한 결과가 아닙니다.';
  if(new Set(d.projects.map(p=>p.id)).size!==d.projects.length)throw Error('Duplicate project');
  for(const p of d.projects)for(const photo of p.photos){
    if(Number.isInteger(photo.galleryIndex)){if(photo.galleryIndex<0||photo.galleryIndex>25)throw Error('Invalid archived photo');}
    else {const u=new URL(photo.url);if(u.protocol!=='https:'||!HOSTS.has(u.hostname))throw Error('Unapproved image host');}
  }
  return d;
}
async function data(){return cached('merged',async()=>{
  const [base,ext,ranking]=await Promise.all(['portfolio-data.json','portfolio-expansion.json','ranking.json'].map(source));
  return mergeData(JSON.parse(base),JSON.parse(ext),JSON.parse(ranking));
});}
const CSS=`
.company-grid{grid-template-columns:repeat(4,minmax(0,1fr))}.company-body{padding:18px}.company-body h3{font-size:20px}.cover{height:210px}.score-meta{max-width:95px}.company-card[data-company-id=dabom]{border-color:#afbaa7}.company-card[data-company-id=atelier] .rank{background:#eee9dd;color:#795d25}.photo-strip{display:flex;gap:7px;padding:9px 10px;background:#f3f3ed;overflow-x:auto}.photo-thumb{position:relative;flex:1 0 60px;max-width:140px;height:66px;border:2px solid transparent;border-radius:7px;overflow:hidden;padding:0;background:#e3e6dc}.photo-thumb img{width:100%;height:100%;object-fit:cover;display:block}.photo-thumb span{position:absolute;bottom:3px;right:4px;font-size:10px;color:white;background:#173d35d9;border-radius:3px;padding:0 5px}.photo-thumb[aria-pressed=true]{border-color:#173d35}.photo-thumb.thumb-error{min-height:60px}.card-photo-credit{padding:6px 13px 0;margin:0;font-size:10px;line-height:1.55;color:#66736b}.modal-strip{justify-content:center;background:white;padding:5px 20px 16px}.modal-strip .photo-thumb{height:75px;max-width:120px}.comparison{min-width:870px}.intro-note{font-size:13px}.rank-note#photo-coverage{margin-top:12px}
@media(max-width:1100px){.company-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.cover{height:225px}}
@media(max-width:700px){.company-grid{grid-template-columns:1fr}.cover{height:100%;min-height:290px}.company-body h3{font-size:19px}.filters .filter{flex:0 1 auto}.photo-thumb{height:49px;flex-basis:42px}.photo-strip{padding:7px;gap:5px}.modal-strip .photo-thumb{height:62px}.card-photo-credit{font-size:9px;padding:6px 10px 0}.intro-note{font-size:12px}.score-meta{max-width:90px}}
@media print{.company-grid{grid-template-columns:repeat(4,1fr)}.photo-strip{display:none}.cover{height:110px;min-height:0}.company-body{padding:8px}.company-body h3{font-size:13px}.comparison{min-width:0}.company-card{display:block}}
`;
export function upgradeHtml(html,js){
  if(!html.includes('}}init();')||!html.includes('id="comparison"'))throw Error('Base template changed; review transformation');
  html=html.replace(/<title>[\s\S]*?<\/title>/,'<title>제주 시공사 포트폴리오 — 하백·GAU·다봄 / 아틀리에</title>');
  html=html.replace(/상위 세 후보/g,'주요 세 후보와 추가 비교 업체').replace('먼저 비교할 세 업체','주요 세 업체 + 추가 비교');
  html=html.replace(/<div class="intro-note">[\s\S]*?<\/div>/,'<div class="intro-note"><strong>비교 대상과 점수순을 구분합니다.</strong><p><b>하백·이아 / GAU / 다봄</b>을 주요 비교 대상으로, <b>아틀리에</b>를 추가 비교로 배치했습니다. 기존 점수는 변경하지 않았습니다. 사진만으로 계약 적격이나 시공품질을 보증하지 않습니다.</p></div>');
  html=html.replace('78·78·60점은 수행 능력 실측 점수가 아닌 공개근거 기반 잠정 점수입니다. 제주 현지팀이 확인되지 않은 3위는 조건부 비교 후보입니다.','화면 배치 순서는 계약 순위가 아닙니다. 기존 점수순: 하백·GAU 공동 1위(78점), 아틀리에 3위(60점), 다봄 4위(57점). 다봄은 주요 비교 대상이지만 계약 주체·소원재 보수 경위 확인 전 조건부입니다.');
  html=html.replace('<button type="button" class="filter" data-company="atelier"','<button type="button" class="filter" data-company="dabom" aria-pressed="false">다봄 5</button><button type="button" class="filter" data-company="atelier"');
  html=html.replace('<p class="rank-note">RC는','<p class="rank-note" id="photo-coverage"></p><p class="rank-note">RC는');
  html=html.replace('기존 조사와 채점표는 그대로 보존했습니다. 다봄은 현재 채점표상 4위(57점)이며, 상위 세 업체와 구분하여 이전 사진집에서 확인할 수 있습니다.','다봄의 5개 프로젝트와 사진을 메인 화면에 통합했습니다. 기존 조사·채점표·26장 사진집은 그대로 보존했습니다. 표기된 사진가와 출처는 각 상세 화면에서 확인하세요.');
  html=html.replace('15개 프로젝트 · 대표 사진 12장','20개 프로젝트 · 사진 불러오는 중').replace('상위 세 후보 · 15개 프로젝트 · 사진과 근거로 비교하기','하백·GAU·다봄과 아틀리에 · 20개 프로젝트 사진 비교');
  html=html.replace('</style>',CSS+'\n</style>');
  html=html.replace("fetch('portfolio-data.json')","fetch('portfolio-data.json?edition=dabom-gallery-v2')");
  html=html.replace("&index=${i}`","&index=${i}&edition=dabom-gallery-v2`");
  html=html.replace('}}init();',"}}window.addEventListener('portfolio:ready',init,{once:true});");
  return html.replace('</body>','<script>\n'+js.replace(/<\/script/gi,'<\\/script')+'\n</script></body>');
}
async function archivedPhoto(index){
  const headers={};let body;
  const req={method:'GET',query:{file:'gallery-photo',index:String(index)},url:'/gallery-photo?index='+index};
  const res={statusCode:200,setHeader(k,v){headers[k.toLowerCase()]=v;},end(b){body=b;}};
  await legacy(req,res);
  if(res.statusCode!==200||!Buffer.isBuffer(body))throw new HTTPError(502,'Archived photo unavailable');
  return {body,type:headers['content-type']};
}
async function photo(p,index){return cached('photo:'+p.id+':'+index,async()=>{
  const x=p.photos[index];if(!x)throw new HTTPError(404,'Unknown photo');
  if(Number.isInteger(x.galleryIndex))return archivedPhoto(x.galleryIndex);
  const u=new URL(x.url);if(u.hostname==='images.squarespace-cdn.com')u.searchParams.set('format','1200w');
  const r=await download(u.href);if(!/^image\/(jpeg|png|webp|avif)/i.test(r.type))throw new HTTPError(502,'Invalid image response');return r;
},3600000);}
function send(req,res,status,body,type='application/json; charset=utf-8',ttl=60){
  res.statusCode=status;res.setHeader('Content-Type',type);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('X-Frame-Options','DENY');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');
  res.setHeader('X-Source-Repository','kks0488/jeju_proposal');res.setHeader('X-Source-Branch','master');res.setHeader('X-Portfolio-Edition','dabom-gallery-v2');
  res.setHeader('Cache-Control',status===200?`public, max-age=0, s-maxage=${ttl}, stale-while-revalidate=60`:'no-store');
  res.setHeader('ETag','"'+createHash('sha256').update(body).digest('hex').slice(0,24)+'"');res.end(req.method==='HEAD'?undefined:body);
}
async function mapLimit(items,limit,fn){const out=new Array(items.length);let at=0;await Promise.all(Array.from({length:Math.min(limit,items.length)},async()=>{while(at<items.length){const index=at++;out[index]=await fn(items[index]);}}));return out;}
export default async function handler(req,res){
  if(req.method!=='GET'&&req.method!=='HEAD'){res.setHeader('Allow','GET, HEAD');return send(req,res,405,'Method not allowed','text/plain; charset=utf-8');}
  const q=req.query||Object.fromEntries(new URL(req.url,'https://jeju-proposal.vercel.app').searchParams);
  let file=typeof q.file==='string'?q.file:'public-portfolio.html';if(file==='index.html'||file==='')file='public-portfolio.html';
  try{
    if(file==='public-portfolio.html'){const [html,js]=await Promise.all(['public-portfolio.html','portfolio-enhancements.js'].map(source));return send(req,res,200,upgradeHtml(html,js),'text/html; charset=utf-8');}
    if(file==='portfolio-data.json')return send(req,res,200,JSON.stringify(await data()));
    if(file==='photo'){
      if(typeof q.project!=='string'||!/^\d{1,2}$/.test(String(q.index??'')))throw new HTTPError(404,'Unknown photo');
      const d=await data(),p=d.projects.find(p=>p.id===q.project),index=Number(q.index);if(!p||!p.photos[index])throw new HTTPError(404,'Unknown photo');
      const r=await photo(p,index);return send(req,res,200,r.body,r.type,3600);
    }
    if(file==='health'){
      const d=await data();const result={ok:true,mode:'github-origin+curated-overlay',version:d.version,repository:'kks0488/jeju_proposal',branch:'master',companies:d.companies.length,projects:d.projects.length,photos:d.projects.reduce((n,p)=>n+p.photos.length,0),photoProjects:d.projects.filter(p=>p.photos.length).length,missingPhotos:d.projects.filter(p=>!p.photos.length).map(p=>({id:p.id,name:p.name})),companyBreakdown:d.companies.map(c=>({id:c.id,rank:c.rank,score:c.score,projects:d.projects.filter(p=>p.company===c.id).length,photos:d.projects.filter(p=>p.company===c.id).reduce((n,p)=>n+p.photos.length,0)}))};
      if(q.images==='1'){
        result.assets=await mapLimit(d.projects.flatMap(p=>p.photos.map((_,index)=>({p,index}))),4,async({p,index})=>{try{const r=await photo(p,index);return {project:p.id,index,ok:true,bytes:r.body.length,type:r.type};}catch(e){return {project:p.id,index,ok:false,status:e.status||502};}});
        result.assetsOk=result.assets.every(x=>x.ok);
      }
      if(q.links==='1'){
        result.anonymousChecks=await mapLimit(['/','/portfolio-data.json','/photo?project=jeoji&index=0','/photo?project=simyang&index=1','/ranking.html','/contractor-gallery.html','/review.html'],4,async path=>{try{const r=await fetch('https://jeju-proposal.vercel.app'+path,{redirect:'manual',signal:AbortSignal.timeout(14000)});const body=await r.arrayBuffer();return {path,status:r.status,bytes:body.byteLength,ok:r.status===200};}catch{return {path,ok:false};}});
        result.anonymousAccessOk=result.anonymousChecks.every(x=>x.ok);result.probeCredentials='No cookies, Authorization or protection-bypass headers sent';
      }
      return send(req,res,200,JSON.stringify(result));
    }
    return legacy(req,res);
  }catch(e){console.error('Portfolio v2',{file,message:e.message});return send(req,res,e.status||502,JSON.stringify({error:e.status===404?'자료를 찾을 수 없습니다.':'자료를 불러오지 못했습니다. 새로고침해 주세요.'}));}
}
