"""Render the dated supplemental research into the existing review and Markdown."""
from pathlib import Path
import json, html, re
R = Path(__file__).resolve().parent
D = json.loads((R / 'expanded-review.json').read_text())
e = lambda value: html.escape(str(value), quote=True)
def link(title, url):
    return '<a href="' + e(url) + '">' + e(title) + '</a>'
def table(heads, rows):
    return '<div class="table-wrap"><table><thead><tr>' + ''.join('<th scope="col">'+e(x)+'</th>' for x in heads) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rows) + '</tbody></table></div>'
def mdtable(heads, rows):
    return ['| '+' | '.join(heads)+' |', '|'+'---|'*len(heads)] + ['| '+' | '.join(row)+' |' for row in rows]
heads = ['업체', '현재 판단', '확인한 근거', '남은 차이']
h = '<!-- EXPANDED-START --><section id="expanded"><p class="eyebrow">ADDITIONAL RESEARCH · '+e(D['checked'])+'</p><h2>'+e(D['title'])+'</h2><p>'+e(D['summary'])+'</p><p>'+e(D['method'])+'</p><p>'+link('추가 조사 문서', 'EXPANDED-REVIEW.md')+' · '+link('갱신한 13개 후보 채점표', 'ranking.html')+'</p>'+table(heads, D['overview'])
md = ['# '+D['title'], '', '검토일: '+D['checked'], '', D['summary'], '', D['method'], '', '## 판단 비교', ''] + mdtable(heads, D['overview'])
for s in D['sections']:
    h += '<article id="expanded-'+s['id']+'"><h3>'+e(s['title'])+'</h3>' + ''.join('<p>'+e(p)+'</p>' for p in s['paragraphs']) + '<p><b>판단을 바꿀 자료:</b> '+e(s['request'])+'</p><ul>' + ''.join('<li>'+link(t,u)+'</li>' for t,u in s['sources'])+'</ul></article>'
    md += ['', '## '+s['title'], '']
    for p in s['paragraphs']: md += [p, '']
    md += ['판단을 바꿀 자료: '+s['request'], ''] + ['- ['+t+']('+u+')' for t,u in s['sources']]
heads = ['대상', '출처의 표기', '처리']
h += '<h3>숫자·구조 불일치 기록</h3>'+table(heads, D['conflicts'])
md += ['', '## 숫자·구조 불일치 기록', ''] + mdtable(heads, D['conflicts'])
h += '<h3>조사 범위와 한계</h3><ul>'+''.join('<li>'+e(p)+'</li>' for p in D['limits'])+'</ul><ul>'+''.join('<li>'+link(t,u)+'</li>' for t,u in D['extra_sources'])+'</ul></section><!-- EXPANDED-END -->'
md += ['', '## 조사 범위와 한계', ''] + ['- '+p for p in D['limits']] + ['', '추가 출처:'] + ['- ['+t+']('+u+')' for t,u in D['extra_sources']]
(R / 'EXPANDED-REVIEW.md').write_text('\n'.join(md)+'\n')
p = R / 'review.html'
body = re.sub(r'<!-- EXPANDED-START -->.*?<!-- EXPANDED-END -->', '', p.read_text(), flags=re.S)
assert '</main>' in body
p.write_text(body.replace('</main>', h+'</main>', 1))
print('Built expanded research: 4 new companies, 1 scored addition, existing review retained.')
