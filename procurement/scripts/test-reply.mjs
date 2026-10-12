// Tests a local-only draft editor with synthetic values. No accounts or bid submission.
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {chromium}=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE).href);
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH});
const results=[],errors=[],requests=[];
try {
for(const colorScheme of ['light','dark'])for(const width of [390,1440]){
 const context=await browser.newContext({viewport:{width,height:960},colorScheme,acceptDownloads:true});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort()});
 await page.goto(pathToFileURL(path.join(root,'contractor','reply.html')).href);
 await page.waitForFunction(()=>window.bidDraft&&document.querySelectorAll('#a-rows details').length===61);
 assert.equal(await page.locator('#subtotal').innerText(),'미입력');
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2),false);
 const row=page.locator('details[data-row-id="GEN-01"]');await row.locator('summary').click();
 await row.getByLabel('응답상태',{exact:true}).selectOption('priced');
 await row.getByLabel('수량 · 기준단위 식',{exact:true}).fill('2');
 await row.getByLabel('복합단가 · 원/단위 · 세전',{exact:true}).fill('50000');
 assert.equal((await page.evaluate(()=>window.bidDraft.snapshot())).a_rows[0].amount,100000);
 await row.getByLabel('제시 모델·사양',{exact:true}).fill('=TEST-SYNTHETIC');
 await page.locator('#add-b').click();const b=page.locator('#b-rows .proposal').first();
 await b.getByLabel('관련 항목ID(쉼표 구분)',{exact:true}).fill('HVAC-01');
 await b.getByLabel('제안 제목',{exact:true}).fill('TEST 대안');
 await b.getByLabel('해당 범위 A 금액(원)',{exact:true}).fill('100000');
 await b.getByLabel('해당 범위 B 완성금액(원)',{exact:true}).fill('80000');
 await b.getByLabel('성능·부하·선정 근거',{exact:true}).fill('시험 데이터이며 실제 냉방설계가 아닙니다.');
 assert((await b.locator('.result').innerText()).includes('-20,000'));
 await page.locator('#add-q').click();await page.locator('#q-rows').getByLabel('질의·코멘트',{exact:true}).fill('<b>TEST 문자를 그대로 보관</b>');
 const before=await page.evaluate(()=>window.bidDraft.snapshot());assert.equal(before.identity_verified,false);assert.equal(before.status,'local_draft_not_submitted');
 const rejection=await page.evaluate(()=>{const bad=window.bidDraft.snapshot();bad.package_id='OLD';try{window.bidDraft.parseImported(bad);return false}catch{return true}});assert(rejection);
 const boolRejected=await page.evaluate(()=>{const bad=window.bidDraft.snapshot();bad.a_rows[0].qty=true;try{window.bidDraft.parseImported(bad);return false}catch{return true}});assert(boolRejected);
 let down=page.waitForEvent('download');await page.locator('#save-csv').click();let f=await down;const csv=await fs.readFile(await f.path(),'utf8');assert(csv.includes("'=TEST-SYNTHETIC"));
 down=page.waitForEvent('download');await page.locator('#save-html').click();f=await down;const html=await fs.readFile(await f.path(),'utf8');assert(html.includes('&lt;b&gt;TEST'));assert(!html.includes('<b>TEST 문자를'));assert(html.includes('미제출·미인증'));
 down=page.waitForEvent('download');await page.locator('#save-json').click();f=await down;const saved=JSON.parse(await fs.readFile(await f.path(),'utf8'));assert.equal(saved.a_rows[0].amount,100000);assert.equal(saved.b_proposals.length,1);assert.equal(saved.comments.length,1);assert.equal(saved.identity_verified,false);
 await page.locator('#import').setInputFiles({name:'synthetic.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(saved))});
 await page.waitForFunction(()=>document.getElementById('message').textContent.includes('불러왔습니다'));
 assert.equal((await page.evaluate(()=>window.bidDraft.snapshot())).a_rows[0].amount,100000);
 if(width===1440&&colorScheme==='light'){const p=path.join(root,'..','.local','procurement-r2');await fs.mkdir(p,{recursive:true});await page.screenshot({path:path.join(p,'reply-qa.png')});}
 results.push({width,colorScheme,checks:'61 rows, blank/quantity math, B negative delta, literal comments, revision/type rejection, CSV/HTML escaping, JSON save/import',passed:true});await context.close();
}
}finally{await browser.close()}
const report={passed:errors.length===0&&requests.length===0,configurations:results.length,results,errors,external_requests:requests,authentication_or_private_server_tested:false,scope:'Local file input/export smoke; not deployed bid service security certification'};
await fs.writeFile(path.join(root,'reply-validation-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
