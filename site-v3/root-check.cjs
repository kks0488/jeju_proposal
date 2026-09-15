'use strict';
const {chromium}=require('playwright');
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
(async()=>{
 const qa=path.resolve('site-v3/qa');await fs.mkdir(qa,{recursive:true});let server;
 let base=process.env.BASE_URL;
 if(!base){const root=path.resolve('dist');server=http.createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost');const p=path.resolve(root,'.'+(url.pathname==='/'?'/index.html':decodeURIComponent(url.pathname)));if(!p.startsWith(root+path.sep))throw Error('path');const bytes=await fs.readFile(p);res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.json':'application/json','.webp':'image/webp'})[path.extname(p)]||'application/octet-stream');res.end(bytes);}catch{res.statusCode=404;res.end('not found');}});await new Promise(r=>server.listen(0,'127.0.0.1',r));base='http://127.0.0.1:'+server.address().port+'/';}
 const browser=await chromium.launch({headless:true}),results=[];
 try{for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'}),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const response=await page.goto(base,{waitUntil:'networkidle',timeout:60000});assert.equal(response.status(),200);
  assert.equal(new URL(page.url()).pathname,new URL(base).pathname);
  assert.equal(await page.title(),'제주집 시공사 선정');assert.equal(await page.locator('h1').innerText(),'제주집 시공사 선정');
  assert.match(await page.locator('.notice').innerText(),/현재 평가 순위에 따라 시공사를 비교합니다/);
  assert.equal(await page.locator('iframe').count(),0);
  assert(!(await page.locator('body').innerText()).includes('중에서 선정합니다.'));
  assert.equal(await page.locator('.project').count(),17);assert.equal(await page.locator('.company').count(),3);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.locator('.filters [data-company=dabom]').click();assert.equal(await page.locator('.project:visible').count(),5);
  await page.locator('[data-open=jeoji]').first().click();assert(await page.locator('#gallery').evaluate(e=>e.open));await page.locator('#large-image').evaluate(im=>im.decode());await page.locator('#next').click();await page.locator('#large-image').evaluate(im=>im.decode());assert.match(await page.locator('#gallery-count').innerText(),/2 \//);await page.keyboard.press('Escape');
  await page.locator('.filters [data-company=all]').click();await page.locator('#search').fill('용담');assert.equal(await page.locator('.project:visible').count(),1);await page.locator('#search').fill('');
  const images=await page.evaluate(async()=>{const d=JSON.parse(document.getElementById('site-data').textContent),files=d.projects.flatMap(p=>p.photos.map(x=>x.url)),broken=[];let count=0,at=0;await Promise.all(Array.from({length:6},async()=>{while(at<files.length){const src=files[at++];const im=new Image();im.src=src;try{await im.decode();count++;}catch{broken.push(src);}}}));return {count,broken,local:files.every(x=>new URL(x,location.href).origin===location.origin)};});
  assert.equal(images.count,178);assert.deepEqual(images.broken,[]);assert(images.local);assert.deepEqual(errors,[]);
  await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(qa,'root-'+width+'.png')});
  results.push({width,status:response.status(),url:page.url(),title:await page.title(),imagesDecoded:images.count,broken:images.broken,allImagesSameOrigin:images.local,jsErrors:errors,filterAndGallery:true});await context.close();
 }}finally{await browser.close();if(server)await new Promise(r=>server.close(r));}
 const report={checkedAt:new Date().toISOString(),base,anonymous:true,results};await fs.writeFile(path.join(qa,'root-report.json'),JSON.stringify(report,null,2));console.log('ROOT_CHECK '+JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1;});
