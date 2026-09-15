import base from '../lib/portfolio-v2-core.mjs';
import sharp from 'sharp';
import { createHash } from 'node:crypto';
export { mergeData, upgradeHtml } from '../lib/portfolio-v2-core.mjs';
export const config={maxDuration:60};
sharp.cache({memory:32,files:0,items:16});sharp.concurrency(1);
const HOSTS=new Set(['iacompany.co.kr','www.iacompany.co.kr','vmspace.com','www.vmspace.com','images.squarespace-cdn.com','static.wixstatic.com','t1.daumcdn.net','media.brique.co']);
const cache=new Map(),pending=new Map();
async function internal(file,query={}){
  const headers={};let body;
  const res={statusCode:200,setHeader(k,v){headers[k.toLowerCase()]=v;},end(b){body=b;}};
  await base({method:'GET',url:'/'+file,query:{file,...query}},res);
  if(res.statusCode!==200)throw Error('Internal source '+file+' returned '+res.statusCode);
  return {body,type:headers['content-type']};
}
async function data(){const r=await internal('portfolio-data.json');return JSON.parse(r.body.toString());}
async function download(address){
  let u=new URL(address);
  if(u.hostname==='images.squarespace-cdn.com')u.searchParams.set('format','1600w');
  for(let hop=0;hop<4;hop++){
    if(u.protocol!=='https:'||!HOSTS.has(u.hostname))throw Error('Image host is not approved');
    const r=await fetch(u,{redirect:'manual',signal:AbortSignal.timeout(18000)});
    if(r.status>=300&&r.status<400){const to=r.headers.get('location');await r.body?.cancel();if(!to)throw Error('Missing redirect');u=new URL(to,u);continue;}
    if(!r.ok){await r.body?.cancel();throw Error('Image source '+r.status);}
    const limit=32*1024*1024;
    if(Number(r.headers.get('content-length')||0)>limit){await r.body?.cancel();throw Error('Source over 32 MB');}
    if(!/^image\/(jpeg|jpg|png|webp|avif)/i.test(r.headers.get('content-type')||'')){await r.body?.cancel();throw Error('Non-image response');}
    let n=0;const chunks=[];
    for await(const c of r.body){n+=c.length;if(n>limit)throw Error('Source over 32 MB');chunks.push(c);}
    return Buffer.concat(chunks);
  }throw Error('Too many redirects');
}
async function image(p,index){
  const item=p.photos[index];if(!item)throw Error('Unknown photo');
  if(Number.isInteger(item.galleryIndex))return internal('photo',{project:p.id,index:String(index)});
  const key=item.url,hit=cache.get(key);
  if(hit&&Date.now()-hit.time<3600000)return hit.result;
  if(pending.has(key))return pending.get(key);
  const job=(async()=>{try{
    const original=await download(item.url);
    const body=await sharp(original,{limitInputPixels:64000000}).rotate().resize({width:1600,height:1600,fit:'inside',withoutEnlargement:true}).webp({quality:82}).toBuffer();
    if(body.length>4*1024*1024)throw Error('Optimized response too large');
    const result={body,type:'image/webp',sourceBytes:original.length};
    cache.set(key,{result,time:Date.now()});while(cache.size>40)cache.delete(cache.keys().next().value);return result;
  }finally{pending.delete(key);}})();pending.set(key,job);return job;
}
function send(req,res,status,body,type='application/json; charset=utf-8',ttl=60){
  res.statusCode=status;res.setHeader('Content-Type',type);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('X-Frame-Options','DENY');res.setHeader('X-Robots-Tag','noindex, nofollow');res.setHeader('Referrer-Policy','strict-origin-when-cross-origin');res.setHeader('X-Source-Repository','kks0488/jeju_proposal');res.setHeader('X-Source-Branch','master');res.setHeader('X-Portfolio-Edition','dabom-gallery-v2');res.setHeader('Cache-Control',status===200?`public, max-age=0, s-maxage=${ttl}, stale-while-revalidate=60`:'no-store');res.setHeader('ETag','"'+createHash('sha256').update(body).digest('hex').slice(0,24)+'"');res.end(req.method==='HEAD'?undefined:body);
}
async function limited(items,fn){const out=new Array(items.length);let at=0;await Promise.all(Array.from({length:Math.min(3,items.length)},async()=>{while(at<items.length){const i=at++;out[i]=await fn(items[i]);}}));return out;}
export default async function handler(req,res){
  const q=req.query||Object.fromEntries(new URL(req.url,'https://jeju-proposal.vercel.app').searchParams);
  if(req.method!=='GET'&&req.method!=='HEAD')return base(req,res);
  if(q.file!=='photo'&&q.file!=='health')return base(req,res);
  try{
    const d=await data();
    if(q.file==='photo'){
      const p=d.projects.find(p=>p.id===q.project);
      if(typeof q.project!=='string'||!/^\d{1,2}$/.test(String(q.index??''))||!p?.photos[Number(q.index)])return send(req,res,404,'{"error":"사진을 찾을 수 없습니다."}');
      const r=await image(p,Number(q.index));return send(req,res,200,r.body,r.type,3600);
    }
    const result={ok:true,mode:'github-origin+curated-overlay',version:d.version,repository:'kks0488/jeju_proposal',branch:'master',companies:d.companies.length,projects:d.projects.length,photos:d.projects.reduce((n,p)=>n+p.photos.length,0),photoProjects:d.projects.filter(p=>p.photos.length).length,missingPhotos:d.projects.filter(p=>!p.photos.length).map(p=>({id:p.id,name:p.name})),companyBreakdown:d.companies.map(c=>({id:c.id,rank:c.rank,score:c.score,projects:d.projects.filter(p=>p.company===c.id).length,photos:d.projects.filter(p=>p.company===c.id).reduce((n,p)=>n+p.photos.length,0)}))};
    if(q.images==='1'){
      result.assets=await limited(d.projects.flatMap(p=>p.photos.map((_,index)=>({p,index}))),async({p,index})=>{try{const r=await image(p,index);return {project:p.id,index,ok:true,bytes:r.body.length,type:r.type,...(r.sourceBytes?{sourceBytes:r.sourceBytes}:{})};}catch(e){return {project:p.id,index,ok:false,reason:e.message};}});
      result.assetsOk=result.assets.every(x=>x.ok);
    }
    if(q.links==='1'){
      result.anonymousChecks=await limited(['/','/portfolio-data.json','/photo?project=jeoji&index=0','/photo?project=simyang&index=1','/photo?project=jaejaesoso&index=0','/ranking.html','/contractor-gallery.html','/review.html'],async path=>{try{const r=await fetch('https://jeju-proposal.vercel.app'+path,{redirect:'manual',signal:AbortSignal.timeout(20000)});const body=await r.arrayBuffer();return {path,status:r.status,bytes:body.byteLength,ok:r.status===200};}catch(e){return {path,ok:false,reason:e.message};}});
      result.anonymousAccessOk=result.anonymousChecks.every(x=>x.ok);result.probeCredentials='No cookies, Authorization or protection-bypass headers sent';
    }
    return send(req,res,200,JSON.stringify(result));
  }catch(e){console.error('Portfolio image gateway',e.message);return send(req,res,502,'{"error":"사진 자료를 불러오지 못했습니다. 새로고침해 주세요."}');}
}
