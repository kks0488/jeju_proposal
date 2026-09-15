import { createHash } from 'node:crypto';
// Fixed public repository origin. No token, arbitrary URL, private file or user header is forwarded.
const ORIGIN='https://raw.githubusercontent.com/kks0488/jeju_proposal/master/';
const TYPES={ 'public-portfolio.html':'text/html; charset=utf-8','portfolio-data.json':'application/json; charset=utf-8','overview.html':'text/html; charset=utf-8','ranking.html':'text/html; charset=utf-8','review.html':'text/html; charset=utf-8','portfolio.html':'text/html; charset=utf-8','folio-audit.html':'text/html; charset=utf-8','style.css':'text/css; charset=utf-8','app.js':'text/javascript; charset=utf-8','ranking.json':'application/json; charset=utf-8','contractor-gallery.html':'text/html; charset=utf-8' };
const PHOTO_HOSTS=new Set(['vmspace.com','www.vmspace.com','iacompany.co.kr','www.iacompany.co.kr','images.squarespace-cdn.com']);
const cache=new Map(); const pending=new Map(); const TTL=60000;
export const config={maxDuration:30};
class UpstreamError extends Error{constructor(status,message){super(message);this.status=status;}}
async function fetchLimited(url,allowedHosts,limit){
  for(let i=0;i<4;i++){
    const parsed=new URL(url);if(parsed.protocol!=='https:'||!allowedHosts.has(parsed.hostname))throw new UpstreamError(400,'Disallowed origin');
    const r=await fetch(parsed,{redirect:'manual',signal:AbortSignal.timeout(12000),headers:{'User-Agent':'Jeju-Portfolio/1.0 (public reference viewer)'}});
    if(r.status>=300&&r.status<400){const location=r.headers.get('location');await r.body?.cancel();if(!location)throw new UpstreamError(502,'Invalid redirect');url=new URL(location,parsed).href;continue;}
    if(!r.ok){await r.body?.cancel();throw new UpstreamError(r.status===404?404:502,'Upstream unavailable');}
    if(Number(r.headers.get('content-length')||0)>limit){await r.body?.cancel();throw new UpstreamError(502,'Source exceeds size limit');}
    const chunks=[];let size=0;for await(const chunk of r.body){size+=chunk.length;if(size>limit)throw new UpstreamError(502,'Source exceeds size limit');chunks.push(chunk);}return {body:Buffer.concat(chunks),type:r.headers.get('content-type')||'application/octet-stream'};
  }throw new UpstreamError(502,'Too many redirects');
}
async function cached(key,loader,ttl=TTL){const old=cache.get(key);if(old&&Date.now()-old.at<ttl)return old.value;if(pending.has(key))return pending.get(key);const task=(async()=>{try{const value=await loader();cache.set(key,{value,at:Date.now()});while(cache.size>48)cache.delete(cache.keys().next().value);return value;}finally{pending.delete(key);}})();pending.set(key,task);return task;}
async function source(file){if(!Object.hasOwn(TYPES,file))throw new UpstreamError(404,'Not found');return cached('file:'+file,()=>fetchLimited(ORIGIN+file+'?refresh='+Math.floor(Date.now()/TTL),new Set(['raw.githubusercontent.com']),10*1024*1024));}
async function data(){const raw=await source('portfolio-data.json');const d=JSON.parse(raw.body.toString('utf8'));if(!Array.isArray(d.projects)||!Array.isArray(d.companies))throw new UpstreamError(502,'Invalid portfolio data');return d;}
async function gallery(){return cached('gallery:parsed',async()=>{const raw=await source('contractor-gallery.html');const photos=[];let html=raw.body.toString('utf8').replace(/src\s*=\s*(["'])(data:image\/(?:jpeg|jpg|png|webp);base64,[A-Za-z0-9+/=\s]+)\1/gi,(_m,_quote,value)=>{const id=photos.push(value)-1;return 'src="gallery-photo?index='+id+'" loading="lazy"';});html=html.replace(/(?:\+82[- .]?)?0?1[016789][- .]?\d{3,4}[- .]?\d{4}/g,'[사적 연락처 비공개]');html=html.replace(/<body([^>]*)>/i,'<body$1><div style="padding:14px 20px;background:#173d35;color:white;font:14px/1.6 sans-serif"><a href="/" style="color:white">← 최신 상위 세 업체 비교로 돌아가기</a> · 기존 사진집 보존본(하백·이아 / GAU / 다봄). 아틀리에는 최신 페이지에서 확인하세요.</div>');return {html,photos};});}
function send(req,res,status,body,type,ttl=60){res.statusCode=status;res.setHeader('Content-Type',type);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('X-Frame-Options','DENY');res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('X-Source-Repository','kks0488/jeju_proposal');res.setHeader('X-Source-Branch','master');res.setHeader('Cache-Control',status===200?`public, max-age=0, s-maxage=${ttl}, stale-while-revalidate=60`:'no-store');res.setHeader('ETag','"'+createHash('sha256').update(body).digest('hex').slice(0,24)+'"');return res.end(req.method==='HEAD'?undefined:body);}
export default async function handler(req,res){
  if(req.method!=='GET'&&req.method!=='HEAD'){res.setHeader('Allow','GET, HEAD');return send(req,res,405,'Method not allowed','text/plain; charset=utf-8');}
  const q=req.query||Object.fromEntries(new URL(req.url,'https://jeju-proposal.vercel.app').searchParams);let file=typeof q.file==='string'?q.file:'public-portfolio.html';if(file==='index.html'||file==='')file='public-portfolio.html';
  try{
    if(file==='robots.txt')return send(req,res,200,'User-agent: *\nDisallow: /\n','text/plain; charset=utf-8');
    if(file==='health'){const d=await data();const result={ok:true,mode:'github-origin',repository:'kks0488/jeju_proposal',branch:'master',updated:d.updated,projects:d.projects.length,photos:d.projects.reduce((n,p)=>n+p.photos.length,0)};if(q.images==='1'){result.assets=await Promise.all(d.projects.flatMap(p=>p.photos.map(async(photo,index)=>{try{const u=new URL(photo.url);if(u.hostname==='images.squarespace-cdn.com')u.searchParams.set('format','1200w');const image=await cached('photo:'+u.href,()=>fetchLimited(u.href,PHOTO_HOSTS,4*1024*1024),3600000);return {project:p.id,index,ok:/^image\//.test(image.type),bytes:image.body.length};}catch(e){return {project:p.id,index,ok:false,status:e.status||502};}})));result.assetsOk=result.assets.every(x=>x.ok);}return send(req,res,200,JSON.stringify(result),'application/json; charset=utf-8');}
    if(file==='photo'){
      if(typeof q.project!=='string'||!/^\d{1,2}$/.test(String(q.index??'')))throw new UpstreamError(404,'Unknown photo');
      const d=await data();const p=d.projects.find(p=>p.id===q.project);const photo=p?.photos?.[Number(q.index)];if(!photo)throw new UpstreamError(404,'Unknown photo');
      const u=new URL(photo.url);if(u.hostname==='images.squarespace-cdn.com')u.searchParams.set('format','1200w');
      const image=await cached('photo:'+u.href,()=>fetchLimited(u.href,PHOTO_HOSTS,4*1024*1024),3600000);if(!/^image\/(jpeg|png|webp|avif)/i.test(image.type))throw new UpstreamError(502,'Invalid image');return send(req,res,200,image.body,image.type,3600);
    }
    if(file==='gallery-photo'){
      if(!/^\d{1,3}$/.test(String(q.index??'')))throw new UpstreamError(404,'Unknown photo');const g=await gallery();const image=g.photos[Number(q.index)];if(!image)throw new UpstreamError(404,'Unknown photo');const comma=image.indexOf(',');const body=Buffer.from(image.slice(comma+1),'base64');if(body.length>4*1024*1024)throw new UpstreamError(502,'Image too large');return send(req,res,200,body,image.slice(5,image.indexOf(';')),3600);
    }
    if(file==='contractor-gallery.html'){const g=await gallery();return send(req,res,200,g.html,TYPES[file]);}
    const r=await source(file);let body=r.body;
    if(file.endsWith('.html')&&file!=='public-portfolio.html')body=Buffer.from(body.toString('utf8').replace(/href=(["'])history\/[^"']+\1/gi,'href="/"').replace(/(?:\+82[- .]?)?0?1[016789][- .]?\d{3,4}[- .]?\d{4}/g,'[사적 연락처 비공개]'));
    return send(req,res,200,body,TYPES[file]);
  }catch(e){const status=e.status||502;console.error('Public portfolio request failed',{file,status,message:e.message});return send(req,res,status,'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>자료 연결 확인</title><body style="font:16px/1.8 sans-serif;max-width:650px;margin:12vh auto;padding:25px"><h1>'+(status===404?'공개되지 않은 경로입니다.':'자료를 잠시 불러오지 못했습니다.')+'</h1><p>원본 저장소 연결 또는 이미지 출처의 일시적인 응답 문제일 수 있습니다. 잠시 후 새로고침해 주세요.</p><p><a href="/">최신 비교 페이지로 돌아가기</a></p></body></html>','text/html; charset=utf-8');}
}
