"""Render an auditable, evidence-based selection score, not a quality guarantee."""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parent
D=json.loads((R/'ranking.json').read_text())
e=lambda x:html.escape(str(x),quote=True)
C=D['criteria']; rows=D['candidates']
assert sum(c['weight'] for c in C)==100
for p in rows:
 assert len(p['levels'])==len(C) and all(0<=v<=5 for v in p['levels'])
 assert p['total']==sum(v*c['weight']/5 for v,c in zip(p['levels'],C))
heads=['순위','업체']+[c['name']+' / '+str(c['weight']) for c in C]+['합계 / 100','현재 조건']
values=[[str(p['rank']),p['name']]+p['points']+[p['total'],p['status']] for p in rows]
def table(headers,vs):return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+e(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in vs)+'</tbody></table></div>'
def mdtable(headers,vs):return ['| '+' | '.join(map(str,headers))+' |','|'+'---|'*len(headers)]+['| '+' | '.join(map(str,row))+' |' for row in vs]
intro='하백/이아컴퍼니와 GAU는 78점으로 공동 1위를 유지한다. 새로 검증한 아틀리에건설은 60점으로 3위에 추가하되, 서울 기반이고 현재 제주 상주팀이 확인되지 않은 조건부 비교 대상이다. 제주 현지 우선 검증은 하백·GAU, 성능 비교는 JEJUPH 54점으로 유지한다. 점수는 계약 적격이나 업계 실력 순위가 아니다. 상세 추가 조사와 구조 구분은 review.html#expanded에서 확인할 수 있다.'
notes=[
'아틀리에건설의 제주 실적은 2016·2018년이다. 같은 시공사의 2025년 서울 실적이 현재 제주 수행팀을 입증하지는 않는다. 신규 관찰 후보 돌담하우스·레아하우징·포스트제주는 추가 조사 문서에서 별도 검토했다.',
'완성 사진의 아름다움, 유명 건축가, 건축명장·협회 회원 명칭, 검색 결과 수는 별도 가점을 주지 않았다. 사진은 관련 접합부·외장·외부공간의 결과물을 확인하는 보조 근거로만 썼다.',
'같은 건물의 중복 기사, 여러 동의 한 프로젝트, 상업시설을 주택 수에 합산하지 않았다. 자체 자료와 외부 크레딧은 단계에서 구분했다. 협회·매체의 크레딧도 계약서 감사나 무하자 보증을 의미하지 않는다.',
'시스홈의 확인되지 않은 제3자 행정처분 표기는 감점하지 않았다. 공식 확인은 계약 전 별도 검증 과제다. 검색에서 부정 후기가 안 나왔다는 이유로 가점을 주지 않았다.',
'하백·GAU의 성능·입주 후 항목은 모두 0점이다. 시험이나 입주 후 보수 기록을 확보하지 못했기 때문이다. 시공 품질이 나쁘다는 뜻이 아니다. GAU의 유지관리 담당 공개만으로 실제 대응 성과를 추정하지 않았다.',
'현재 공사 가격·착공 여력·재무·보증·등록 상태는 충분히 확인하지 못해 상대 점수를 만들지 않았다. 실제 계약 여부는 모든 업체에 대해 별도 확인해야 한다.',
'브라운트리+JD는 확인된 제주 협업을 검토하는 조건부 단위다. 두 회사 전체 실적과 조직을 합산한 점수가 아니며 실제 계약별로 다시 평가해야 한다.',
'저점 후보는 현재 조사자료의 부족이 크게 반영됐다. 엘비탑·오름·TCM의 구조 미확인 0점은 RC 공사 불가능 판정이 아니다. 새 자료가 나오면 근거 단계부터 수정한다.',
'연안재 면적은 기존 매체 기록과 협회 상세 표기가 다르다. 정확한 연면적은 준공 도서 확인 사항이며 이번 점수는 면적 숫자를 가산하지 않아 이 불일치로 점수를 바꾸지 않았다.'
]
h='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>제주 시공사 점수와 순위</title><link rel="stylesheet" href="style.css"><style>td,th{min-width:80px}td:nth-child(2){min-width:180px}.table-wrap{overflow-x:auto}p,li{line-height:1.9}.rubric{margin-top:24px}.score{font-size:1.15em;font-weight:700}</style></head><body><header><a class="brand" href="index.html">JEJU <b>PROPOSAL</b></a><span>공개근거 채점 · '+e(D['date'])+'</span><a href="RANKING.md">채점 문서</a></header><main><section class="intro"><p class="eyebrow">EVIDENCE-BASED SELECTION</p><h1>시공사 점수와 순위</h1><p class="score">'+e(intro)+'</p><div class="notice">'+e(D['notice'])+'</div><p>'+e(D['formula'])+'</p></section><p><a href="review.html#expanded">9월 14일 추가 조사 · 신규 후보와 구조 구분</a></p><section><h2>항목별 점수</h2>'+table(heads,values)+'</section>'
md=['# 제주 시공사 점수와 순위','','검토일 '+D['date'],'',intro,'',D['notice'],'',D['formula'],'','## 항목별 점수','']+mdtable(heads,values)
h+='<section><h2>0~5단계의 공통 채점 기준</h2><p>확보한 근거가 충족하는 가장 높은 단계를 적용한다. 외부 크레딧은 외부 설계자·매체·협회에 해당 시공사가 명시된 것을 뜻한다. 독립적인 계약·성능 감사와는 다르다.</p>'
md+=['','## 공통 채점 기준','','확보한 근거가 충족하는 가장 높은 단계를 적용한다. 외부 크레딧은 외부 설계자·매체·협회에 해당 시공사가 명시된 것을 뜻하며 계약·성능 감사는 아니다.']
for c in C:
 h+='<h3 class="rubric">'+e(c['name'])+' · '+str(c['weight'])+'점</h3><ol start="0">'+''.join('<li>'+e(t)+'</li>' for t in c['levels'])+'</ol>'
 md+=['','### '+c['name']+' · '+str(c['weight'])+'점','']+[str(i)+'. '+t for i,t in enumerate(c['levels'])]
h+='</section><section><h2>업체별 점수 근거</h2>'
for p in rows:
 h+='<article id="'+p['id']+'"><h3>'+str(p['rank'])+'위 · '+e(p['name'])+' · '+str(p['total'])+'점</h3><p>'+e(p['reason'])+'</p><p>'+e(p['limit'])+'</p><details><summary>원문 근거</summary><ul>'+''.join('<li><a target="_blank" rel="noopener noreferrer" href="'+e(u)+'">'+e(t)+'</a></li>' for t,u in p['sources'])+'</ul></details></article>'
 md+=['','## '+str(p['rank'])+'위 · '+p['name']+' · '+str(p['total'])+'점','',p['reason'],'',p['limit'],'','근거 단계: '+', '.join(c['name']+' '+str(v)+'/5' for c,v in zip(C,p['levels'])),'']+['- ['+t+']('+u+')' for t,u in p['sources']]
h+='</section><section><h2>가중치를 바꿔도 순위가 유지되는가</h2>'
sh=['업체']+[s['name'] for s in D['sensitivity']]
sv=[[p['name']]+[int(s['scores'][p['id']]) for s in D['sensitivity']] for p in rows]
h+=table(sh,sv)
sens='하백·GAU 공동 선두는 세 배점안 모두 유지된다. 아틀리에는 기본 60점, 포트폴리오 확대 62점, 제주·RC 강화 62점이다. 제주 현지팀 미확인 조건은 가중치를 바꿔도 남는다. 반면 포트폴리오를 40점으로 높이면 시스홈 61점이 JEJUPH 54점을 앞선다. 제주·RC를 강화하면 이음과 JEJUPH가 54점으로 같아진다. 따라서 중간 순위를 실력의 확정 서열로 읽으면 안 된다. 기본안은 현재 설계 유지와 제주 수행을 함께 반영했다.'
h+='<p>'+e(sens)+'</p><ul>'+''.join('<li>'+e(s['name'])+': '+', '.join(c['name']+' '+str(w) for c,w in zip(C,s['weights']))+'</li>' for s in D['sensitivity'])+'</ul></section>'
md+=['','## 가중치 민감도','']+mdtable(sh,sv)+['',sens,'']+['- '+s['name']+': '+', '.join(c['name']+' '+str(w) for c,w in zip(C,s['weights'])) for s in D['sensitivity']]
h+='<section><h2>점수 해석과 계약 전 조건</h2><ul>'+''.join('<li>'+e(t)+'</li>' for t in notes)+'</ul><p><a href="review.html#responsibility">도급범위·반복 팀 상세</a> · <a href="portfolio.html">다른 업체 포트폴리오</a> · <a href="index.html">전체 조사</a></p></section></main><footer>JEJU PROPOSAL · 점수는 확인된 근거와 가중치에 따라 변경됩니다.</footer></body></html>'
md+=['','## 점수 해석과 계약 전 조건','']+['- '+t for t in notes]
(R/'ranking.html').write_text(h);(R/'RANKING.md').write_text('\n'.join(md)+'\n')
print('Built ranking for',len(rows),'candidates, totals and scenarios checked.')
