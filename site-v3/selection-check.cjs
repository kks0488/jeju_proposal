'use strict';
const {chromium}=require('playwright');
const http=require('node:http'),fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const root=path.resolve('site-v3/published'),qa=path.resolve('site-v3/qa');await fs.mkdir(qa,{recursive:true});
 const server=http.createServer(async(req,res)=>{try{const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const target=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));if(!target.startsWith(root+path.sep))throw Error('path');const body=await fs.readFile(target);res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css','.webp':'image/webp'})[path.extname(target)]||'application/octet-stream');res.end(body);}catch{res.statusCode=404;res.end('Not found');}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const address='http://127.0.0.1:'+server.address().port+'/';
 const browser=await chromium.launch({headless:true});const results=[];
 try{for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(address,{waitUntil:'networkidle'});assert.equal(await page.title(),'제주집 시공사 선정');assert.equal(await page.locator('h1').innerText(),'제주집 시공사 선정');assert.equal(await page.locator('.company').count(),3);assert.equal(await page.locator('.project').count(),17);
  assert.equal(await page.locator('#project-caution').count(),0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.locator('.filters [data-company=dabom]').click();assert.equal(await page.locator('.project:visible').count(),5);await page.locator('[data-open=jeoji]').first().click();assert(await page.locator('#gallery').evaluate(e=>e.open));await page.locator('#next').click();assert.match(await page.locator('#gallery-count').innerText(),/2 \//);await page.keyboard.press('Escape');await page.locator('.filters [data-company=all]').click();
  await page.locator('#search').fill('용담');assert.equal(await page.locator('.project:visible').count(),1);await page.locator('#search').fill('');
  const imageTest=await page.evaluate(async()=>{const d=JSON.parse(document.getElementById('site-data').textContent),broken=[];let count=0;for(const p of d.projects)for(const x of p.photos){const im=new Image();im.src=x.url;try{await im.decode();count++;}catch{broken.push(x.url);}}return {count,broken};});assert.equal(imageTest.count,178);assert.deepEqual(imageTest.broken,[]);assert.deepEqual(errors,[]);
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(qa,'selection-'+width+'.png')});results.push({width,title:await page.title(),imagesDecoded:imageTest.count,broken:imageTest.broken,jsErrors:errors,filterAndGallery:true});await page.close();
 }}finally{await browser.close();await new Promise(r=>server.close(r));}
 const result={checkedAt:new Date().toISOString(),results};await fs.writeFile(path.join(qa,'selection-report.json'),JSON.stringify(result,null,2));console.log('SELECTION_CHECK '+JSON.stringify(result));
})().catch(e=>{console.error(e);process.exit(1);});
