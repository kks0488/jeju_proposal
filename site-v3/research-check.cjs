'use strict';
const {chromium}=require('playwright');const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
(async()=>{
 const ROOT=path.resolve('dist'),qa=path.resolve('site-v3/qa');await fs.mkdir(qa,{recursive:true});let server,base=process.env.BASE_URL;
 if(!base){server=http.createServer(async(req,res)=>{try{const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);let target=path.resolve(ROOT,'.'+name);if(!target.startsWith(ROOT+path.sep)&&target!==ROOT)throw Error('path');if((await fs.stat(target)).isDirectory())target=path.join(target,'index.html');const body=await fs.readFile(target);res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.json':'application/json','.webp':'image/webp'})[path.extname(target)]||'application/octet-stream');res.end(body);}catch{res.statusCode=404;res.end('Not found');}});await new Promise(r=>server.listen(0,'127.0.0.1',r));base='http://127.0.0.1:'+server.address().port+'/';}
 const browser=await chromium.launch({headless:true});const results=[];
 try{
  for(const width of [1440,390,320]){
   const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
   const response=await page.goto(base,{waitUntil:'networkidle'});assert.equal(response.status(),200);assert.equal(await page.title(),'제주집 시공사 선정');
   assert.equal(await page.locator('.research-strip').count(),1);assert.equal(await page.locator('.company').count(),3);assert.equal(await page.locator('.project').count(),17);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.screenshot({path:path.join(qa,'research-main-'+width+'.png')});
   await page.locator('.research-strip a').click();await page.waitForSelector('html[data-research-ready=true]');assert.equal(await page.locator('.candidate').count(),24);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.screenshot({path:path.join(qa,'research-list-'+width+'.png')});
   for(const [filter,n] of [['other',21],['scored',13],['additional',11],['all',24]]){await page.locator('[data-filter='+filter+']').click();assert.equal(await page.locator('.candidate:visible').count(),n);}
   await page.locator('#query').fill('포엠');assert.equal(await page.locator('.candidate:visible').count(),1);await page.locator('#expand').click();assert(await page.locator('#poem details').evaluate(e=>e.open));
   await page.locator('#query').fill('검색결과없음111');assert(await page.locator('#empty').isVisible());await page.locator('#reset').click();assert.equal(await page.locator('.candidate:visible').count(),24);
   await page.locator('.doc-card').first().click();assert((await page.title()).includes('기초 업체 조사'));assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.locator('.back').first().click();assert.equal(await page.locator('.candidate').count(),24);
   await page.goto(new URL('research/?view=other&q=%ED%8F%AC%EC%97%A0',base).href);await page.waitForSelector('html[data-research-ready=true]');assert.equal(await page.locator('.candidate:visible').count(),1);
   assert.deepEqual(errors,[]);results.push({width,status:200,counts:[24,21,13,11],search:true,details:true,documentNavigation:true,deepLink:true,overflow:false,jsErrors:errors});await page.close();
  }
  const page=await browser.newPage();await page.goto(base,{waitUntil:'networkidle'});
  await page.locator('.filters [data-company=dabom]').click();assert.equal(await page.locator('.project:visible').count(),5);await page.locator('[data-open=jeoji]').first().click();assert(await page.locator('#gallery').evaluate(e=>e.open));await page.locator('#next').click();await page.keyboard.press('Escape');
  const images=await page.evaluate(async()=>{const d=JSON.parse(document.getElementById('site-data').textContent),broken=[];let count=0;for(const p of d.projects)for(const x of p.photos){const im=new Image();im.src=x.url;try{await im.decode();count++;}catch{broken.push(x.url);}}return {count,broken};});assert.equal(images.count,178);assert.deepEqual(images.broken,[]);
  const cat=await (await page.request.get(new URL('research/catalog.json',base).href)).json();assert.equal(cat.stats.total,24);assert.equal(cat.stats.scored,13);
  for(const doc of cat.documents){const r=await page.request.get(new URL('research/'+doc.url,base).href);assert.equal(r.status(),200);}
  const report={checkedAt:new Date().toISOString(),base,anonymous:true,results,images,documents:8,stats:cat.stats};await fs.writeFile(path.join(qa,'research-report.json'),JSON.stringify(report,null,2));console.log('RESEARCH_BROWSER_CHECK '+JSON.stringify(report));
 }finally{await browser.close();if(server)await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exit(1);});
