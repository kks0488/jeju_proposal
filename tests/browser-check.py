from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import os
import shutil
root=Path(__file__).resolve().parents[1]
output=root/'test-results'
output.mkdir(exist_ok=True)
html=(root/'public-portfolio.html').read_text()
data=json.loads((root/'portfolio-data.json').read_text())
results=[]
# Offline document test: no network-policy changes; fetch/history are application test doubles.
with sync_playwright() as p:
  executable=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
  options={'headless':True}
  if executable:
    options['executable_path']=executable
  browser=p.chromium.launch(**options)
  for w,h in [(1440,1000),(768,1024),(390,844),(320,700)]:
    page=browser.new_page(viewport={'width':w,'height':h},reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.evaluate('(data)=>{window.fetch=async()=>new Response(JSON.stringify(data),{status:200});window.history.replaceState=(a,b,u)=>{window.__qaUrl=String(u)};}',data)
    page.set_content(html,wait_until='load')
    page.wait_for_selector('.project')
    assert page.locator('.company-card').count()==3
    assert page.locator('.project').count()==15
    assert page.locator('.rank').all_text_contents()==['공동 1위','공동 1위','3위']
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'), f'overflow {w}'
    page.locator('[data-company="atelier"]').click()
    assert page.locator('.project').count()==3
    page.locator('#rc-only').check()
    assert page.locator('.project').count()==2
    assert '눈뫼' not in page.locator('#projects').inner_text()
    page.locator('[data-company="all"]').click();page.locator('#rc-only').uncheck()
    page.locator('#search').fill('호미');assert page.locator('.project').count()==1
    page.locator('[data-project="homi"]').first.click()
    assert page.locator('#detail').evaluate('(e)=>e.open')
    assert page.locator('#detail-title').inner_text()=='호미 · HOMI'
    assert '131㎡' in page.locator('#detail-body').inner_text()
    page.locator('#next-photo').click();assert '2 / 2' in page.locator('.photo-tools').inner_text()
    page.keyboard.press('Escape');assert not page.locator('#detail').evaluate('(e)=>e.open')
    page.locator('#search').fill('무조건없는결과');assert page.locator('#empty').is_visible()
    page.locator('#reset').click();assert page.locator('.project').count()==15
    page.locator('[data-company="atelier"]').click()
    page.locator('[data-project="nunmoe"]').first.click()
    assert '스틸패널' in page.locator('#detail-body').inner_text()
    page.locator('#close').click();page.locator('[data-company="all"]').click()
    page.evaluate('window.scrollTo(0,0)')
    page.screenshot(path=str(output/f'qa-{w}.png'),full_page=False)
    assert not errors, errors
    results.append({'viewport':f'{w}x{h}','passed':True,'js_errors':errors,'horizontal_overflow':False,'mode':'offline document test; fetch/history mocked, upstream photographs not verified here'})
    page.close()
  browser.close()
(output/'qa-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
