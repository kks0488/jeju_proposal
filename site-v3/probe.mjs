import fs from 'node:fs/promises';
import {load} from 'cheerio';
await fs.mkdir('site-v3/diagnostics',{recursive:true});
const pages=[['eoheung','https://iacompany.co.kr/projects/eoeum/'],['yeongpyeong','https://iacompany.co.kr/projects/Yeongpyeongdong-house/'],['ora','https://www.masterbuilder.kr/portfolio/oradong-hyeonine'],['gau','https://www.gauaf.com/'],['jeoji','https://www.arootarchitecture.com/저지오름아래']];
const report=[];
for(const [id,url] of pages){try{const r=await fetch(url,{signal:AbortSignal.timeout(20000)});const html=await r.text();const $=load(html);report.push({id,url,status:r.status,title:$('title').text(),h1:$('h1').text(),images:$('img').map((i,e)=>({src:$(e).attr('src'),lazy:$(e).attr('data-src'),srcset:$(e).attr('srcset')?.slice(0,350),alt:$(e).attr('alt'),parent:$(e).parent().attr('class')})).get(),links:$('a').map((i,e)=>({href:$(e).attr('href'),text:$(e).text().trim().slice(0,80)})).get().filter(x=>/오라|현이|project|portfolio|Work/i.test(x.text+' '+x.href))});await fs.writeFile('site-v3/diagnostics/'+id+'.html',html);}catch(e){report.push({id,url,error:e.message});}}
await fs.writeFile('site-v3/diagnostics/report.json',JSON.stringify(report,null,2));console.log('SOURCE_PROBE '+JSON.stringify(report));
