"""Render the audit's deliberately limited Markdown (headings, tables, lists, links)."""
from pathlib import Path
import html,re
R=Path(__file__).resolve().parent
lines=(R/'FOLIO-AUDIT.md').read_text().splitlines()
def inline(s):
 s=html.escape(s)
 return re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)',r'<a href="\2" target="_blank" rel="noopener noreferrer">\1 ↗</a>',s)
out=[];i=0
while i<len(lines):
 s=lines[i]
 if not s.strip():i+=1;continue
 if s.startswith('| '):
  block=[]
  while i<len(lines) and lines[i].startswith('| '):block.append(lines[i]);i+=1
  cells=lambda row:[inline(v.strip()) for v in row.strip('|').split('|')]
  out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+v+'</th>' for v in cells(block[0]))+'</tr></thead><tbody>')
  for row in block[2:]:out.append('<tr>'+''.join('<td>'+v+'</td>' for v in cells(row))+'</tr>')
  out.append('</tbody></table></div>');continue
 if s.startswith('- '):
  out.append('<ul>')
  while i<len(lines) and lines[i].startswith('- '):out.append('<li>'+inline(lines[i][2:])+'</li>');i+=1
  out.append('</ul>');continue
 if s.startswith('#'):
  n=len(s)-len(s.lstrip('#'));out.append(f'<h{n}>'+inline(s[n:].strip())+f'</h{n}>')
 else:out.append('<p>'+inline(s)+'</p>')
 i+=1
page='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>폴리오 재검토와 공정한 시공사 평가</title><style>body{margin:0;background:#f4f3ef;color:#182c29;font:17px/1.8 system-ui,sans-serif}header,main{max-width:1080px;margin:auto;padding:24px}header{display:flex;gap:24px;flex-wrap:wrap}h1{font-size:clamp(28px,5vw,42px);line-height:1.3}h2{margin-top:54px;border-top:2px solid #b5c3bd;padding-top:24px;font-size:25px}h3{margin-top:30px}a{color:#12624f;text-underline-offset:3px}.table-wrap{overflow-x:auto;margin:24px 0}table{border-collapse:collapse;background:white;width:100%;min-width:620px}th,td{padding:14px;text-align:left;vertical-align:top;border:1px solid #d9dfdb}th{background:#e3ece6}td:first-child{min-width:95px}li{margin:12px 0}@media print{body{background:white;font-size:11pt}header{display:none}h2{break-after:avoid}.table-wrap{overflow:visible}table{min-width:0}tr{break-inside:avoid}}</style></head><body><header><a href="index.html">JEJU PROPOSAL</a><a href="ranking.html">공개자료 잠정 순위</a><a href="contractor-gallery.html">준공 사진</a><a href="templates/contractor-evaluation.csv">평가표 다운로드</a></header><main>'''+''.join(out)+'</main></body></html>'
(R/'folio-audit.html').write_text(page)
print('Built folio audit and final selection rubric.')
