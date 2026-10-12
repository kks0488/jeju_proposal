// Offline file:// smoke/layout check. No server or browser download.
// Supply PLAYWRIGHT_MODULE when reusing an already-installed playwright-core module.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const pkg=process.env.PLAYWRIGHT_MODULE;
const {chromium}=await import(pkg ? pathToFileURL(pkg).href : 'playwright-core');
const executablePath=process.env.CHROME_PATH;
const browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--disable-background-networking']});
const errors=[],results=[];
try {
 const files=(await fs.readdir(root)).filter(p=>p.endsWith('.html')).sort();
 for (const colorScheme of ['light','dark']) {
  for(const width of [390,1440]) {
   const context=await browser.newContext({viewport:{width,height:960},colorScheme});
   const page=await context.newPage();
   page.on('pageerror',e=>errors.push({width,colorScheme,error:e.message}));
   await page.route(/^https?:/,r=>{errors.push({externalRequest:r.request().url()});return r.abort();});
   for(const file of files) {
    await page.goto(pathToFileURL(path.join(root,file)).href,{waitUntil:'load'});
    const result=await page.evaluate(()=>({title:document.title,h1:document.querySelectorAll('h1').length,bodyOverflow:document.documentElement.scrollWidth>innerWidth+2,articleLength:document.querySelector('article')?.innerText.length||0,currentNav:document.querySelectorAll('nav a[aria-current="page"]').length}));
    if(result.h1!==1||result.bodyOverflow||result.articleLength<100||result.currentNav!==1)errors.push({file,width,colorScheme,...result});
    results.push({file,width,colorScheme,passed:result.h1===1&&!result.bodyOverflow&&result.articleLength>100&&result.currentNav===1});
   }
   await page.goto(pathToFileURL(path.join(root,'contractor','index.html')).href,{waitUntil:'load'});
   const tender=await page.evaluate(()=>({h1:document.querySelectorAll('h1').length,bodyOverflow:document.documentElement.scrollWidth>innerWidth+2,specAnchors:document.querySelectorAll('a[id^="sp-"]').length,hasR2:document.body.innerText.includes('JEJU-HOUSE-RFQ-20261013-R2')}));
   const tenderPassed=tender.h1===1&&!tender.bodyOverflow&&tender.specAnchors===37&&tender.hasR2;
   results.push({file:'contractor/index.html',width,colorScheme,passed:tenderPassed});
   if(!tenderPassed)errors.push({file:'contractor/index.html',width,colorScheme,...tender});
   await page.locator('a[href="#sp-20"]').first().click();
   if(!page.url().endsWith('#sp-20'))errors.push({width,colorScheme,error:'Contractor spec anchor did not navigate'});
   // Follow a real cross-page evidence link, and exercise expandable contents.
   await page.goto(pathToFileURL(path.join(root,'RFI.html')).href);
   await page.locator('details.toc summary').click();
   if(!await page.locator('details.toc').evaluate(e=>e.open))errors.push({width,colorScheme,error:'TOC did not expand'});
   const link=page.locator('article a[href="EVIDENCE.html#a-1aa"]').first();
   await link.click();
   if(!page.url().endsWith('EVIDENCE.html#a-1aa'))errors.push({width,colorScheme,error:'Evidence navigation failed'});
   if(width===1440 && colorScheme==='light'){
    await page.goto(pathToFileURL(path.join(root,'index.html')).href);
    const out=path.join(root,'..','.local','procurement-qa');await fs.mkdir(out,{recursive:true});
    await page.screenshot({path:path.join(out,'portal-desktop.png')});
   }
   await context.close();
  }
 }
} finally {await browser.close();}
const receipt={passed:errors.length===0,scope:'Chrome offline DOM/layout/navigation smoke; not CAD/PDF visual validation or cross-browser certification',pageConfigurations:results.length,viewports:[390,1440],schemes:['light','dark'],cad_visual_check:false,errors,results};
await fs.writeFile(path.join(root,'browser-report.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({passed:receipt.passed,pageConfigurations:results.length,errors},null,2));
if(errors.length)process.exitCode=1;
