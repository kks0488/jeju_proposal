#!/usr/bin/env python3
"""Generate R1 owner/pricing documents and a contractor-only share pack.
Canonical input: owner-specifications.json and research-sources.json.
Never includes raw CAD, previous RFI analysis, contractor rankings or filled bids.
"""
from pathlib import Path
import html,json,re,zipfile
import markdown
from markdown.extensions.toc import slugify
P=Path(__file__).resolve().parents[1]

def get(n):return json.loads((P/'data'/n).read_text(encoding='utf-8'))
def write(n,s):
 f=P/n;f.parent.mkdir(parents=True,exist_ok=True)
 f.write_text('\n'.join(x.rstrip() for x in s.splitlines()).strip()+'\n',encoding='utf-8')
def tab(head,rows):
 def c(v):return str(v if v is not None else '업체 도면산출').replace('|','&#124;').replace('\n','<br>')
 return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(c(v) for v in row)+' |' for row in rows])
def anchor(i):return '<a id="'+i.lower()+'"></a>'
def main():
 j=get('owner-specifications.json');sr=get('research-sources.json');scope=get('scope-items.json')['items'];byid={s['id']:s for s in j['specifications']}
 source_map={r['id']:r for r in sr['sources']}
 lines=['# '+j['document_title'], '', '**시공사 전달용 견적 기준 R1 · '+j['package_id']+' · 2026-10-12**', '',
 '**본 공사는 상시 거주하는 주택입니다.** 난방·급탕·환기·냉방·전기 및 마감은 이 문서의 주거용 사양으로 견적해 주십시오. 도면과 아래 사양을 함께 제공하며, 지정이 없는 부분을 업체별 최저등급 자재나 별도공사로 임의 처리하지 않습니다.', '',
 '이 문서는 **가격 산정을 위한 건축주 사양서**입니다. 도면의 수량·형상은 시공사가 산출하고, 명시된 기기/신규 준비 개소와 자재 기준단가는 공통으로 사용합니다. 제작도·부하계산·구조/법정 검토는 수행 책임자가 확인하되, 이를 이유로 사양을 모두 미정으로 되돌리지 않습니다.', '',
 '## 1. 회신 조건', '',
 tab(['구분','공통 기준'],[
 ('견적 범위','도면상의 건축·구조·토목/외부·실내·창호·냉난방/급배수·전기/통신/소방·검사·가설·관리비. 본체/실내 공종소계와 전체총액 모두 제시.'),
 ('수량 방식','업체 도면 적산. 도면번호/개정·위치·산출식 제출. 아래 고정 비교수량은 별도 이견 없이 바꾸지 않음.'),
 ('사양 방식','기준모델/성능을 먼저 견적. 단종·치수불가·공학적 충돌은 해당 ID와 적합한 대체/증감 명시.'),
 ('일정 제안','수신 후5일 이내 질의,14일 이내 견적회신. 견적일로부터60일 유효. 불가능하면 회신 시 가능한 일정과 이유 제시. 실제 발송일은 발주자가 별도 기재.'),
 ('가격 구분','세전 본공사·그 안에 포함된 공통 자재 허용액·별도 옵션·기관 실비·부가세·세후총액을 구분.'),
 ('제외/이견','누락은0원으로 처리하지 않음. 제외 위치/내용, 타행포함ID, 조건부 비용을 별도 표로 명시.'),
 ('업체 자료','실제 계약법인·공종 수행범위·배정소장/동시현장·공기/공정표·보증/보험·검사/보수체계 제출.')]), '',
 '도면상 표기 연면적345.60㎡·건축면적405.06㎡는 서로 다른 값입니다. 어느 한 면적에 평당단가를 곱한 금액만 제출하지 말고, 다락·보일러실·테라스·외부공사를 포함한 공종별 내역을 제시하십시오. 도면의 실명은 위치 식별용으로 보존하고 설비 사용조건은 주택으로 적용합니다.', '',
 '## 2. 기본 사양 한눈에 보기','',
 tab(['공종','기준 사양','상세'],[
 ('난방/급탕','귀뚜라미 기름50S 겸용1대 +600L탱크1대 +도면순환펌프2대. 실별 온수온돌, 샤워2곳 동시사용 목표.','[SP-20~22](#sp-20)'),
 ('냉방','LG 도면 실내기11대/실외기2대. 설치·배관·전원·드레인·시운전 포함. 주거 부하 최적화는 별도안.','[SP-26](#sp-26)'),
 ('환기','힘펠250CMH급3대 + H13/바이패스 + 덕트/점검구/TAB. 욕실배기4대는 별도 유지.','[SP-24~25](#sp-24)'),
 ('창호','이건 AL시스템, 도면43T 삼중유리 출발. 창호별 전체창 성능/풍압/안전유리 확인.','[SP-07](#sp-07)'),
 ('외피','도면0.7mm AL지붕 +T30사비석 +부위별 외단열 유지. 접합 방수·고정·배수 포함.','[SP-04~06](#sp-04)'),
 ('마루/도장','LX강그린 프로맥스 루트오크7mm +KCC숲으로웰빙 무광. 마루 두께변경 바탕조정 포함.','[SP-11](#sp-11), [SP-16](#sp-16)'),
 ('타일/방수','표준규격 타일·C2TES1접착, 샤워 바닥 에폭시줄눈, Mapelastic Smart2mm이상 방수·양생 후 담수.','[SP-12~15](#sp-12)'),
 ('위생기구/가구','대림CC-280양변기3대. 세면기/수전 등 공통 허용액. 도면 고정가구+Blum댐핑경첩.','[SP-18](#sp-18), [SP-28~31](#sp-28)'),
 ('조명/통신','CRI90·주거3000K/작업4000K·주거주조명디밍. CAT6·AP배선3개소·제습준비2개소.','[SP-32~34](#sp-32)')]), '',
 '## 3. 도면에서 유지·변경·추가한 내용','',
 tab(['구분','이번 공통 선택','처리 원칙'],[
 ('유지','RC골조/기초,외관,창호분할,공용부CH3200,사비석/AL지붕,LG기기표 수량','도면의 더 엄격한 안전/부위별 사양은 유지.'),
 ('명시 변경','도면T10강마루 → LX선정제품7mm','원문을 덮어쓰지 않음. 단차 없이 완성FL을 맞추는 바탕조정비 포함.'),
 ('신규 포함','전열교환기250급3대, AP배선3곳, 제습전원/배수2곳, 주거실 차음벽·급탕/조명조건','도면에서 이미 확인한 수량처럼 기록하지 말고 R1추가로 분리.'),
 ('수량 해석','Ø15수전 합계7개를 부동5+일반2로 통일, 주방싱크볼3개 가격 가정','현장/도면 이견은 해당항목을 지정해 공통회신.'),
 ('선택 견적','히트펌프,200L급탕탱크,창호/마감 변경,중앙제습,기기최적화','기준안 총액에 섞지 말고 증감액과 변경범위 제출.')]), '',
 '## 4. 공종별 상세 사양','']
 prev=None
 for s in j['specifications']:
  if s['category']!=prev:lines+=['### '+s['category'],''];prev=s['category']
  lines += [anchor(s['id']),'#### '+s['id']+' · '+s['title'],'',
   '**견적 기준:** '+s['pricing_basis'],'',
   '**기본 포함:** '+s['included_work'],'',
   '**제작·시공 확인:** '+s['shop_drawing_and_acceptance'],'',
   '**견적항목:** '+', '.join(s['scope_ids'])]
  if s['research_refs']:lines+=['','**제품 근거:** '+' · '.join('[{}](#{}): {}'.format(k,k.lower(),source_map[k]['title']) for k in s['research_refs'])]
  lines+=['']
 lines+=['## 5. 공통 자재 기준단가','',
 '**아래 금액은 모든 업체가 같은 자재수준으로 계산하기 위한 발주자 허용액입니다. 실제 시장판매가를 조사해 확정한 값이나 공급업체 견적이 아닙니다.** 지정 모델이 있는 창호·보일러·마루·양변기·냉방기 등은 해당 모델의 실제 공급가격으로 견적합니다. 허용액은 아래 품목에만 적용합니다.', '',
 '허용액은 세전 자재 공급비이며 표준 포장과 제주 현장 반입까지 포함합니다. 설치 노무·접착제/줄눈 등 시공부자재·타공/바탕/배관·특수 양중은 해당 공종에서 따로 견적하되 전체 본공사에는 포함하십시오. 도면 재료 두께와 다른 타일을 제안하면 동일 완성FL/벽면을 유지하는 조정비를 포함합니다.', '',
 tab(['ID','자재','기준단가(원,세전)','단위','공통 비교수량','가격행'],[(a['id'],a['name'],format(a['material_allowance_ex_vat_krw'],','),a['unit'],a['common_pricing_quantity'],a['scope_id']) for a in j['material_allowances']]), '',
 '타일 자재비 = **공통 기준단가 × 순시공면적 × 1.10**. 10%는 모든 업체에 같은 비교용 손실가정이며 실물 발주량 확정치가 아닙니다. 설치비는 순시공면적으로 계산하고 손실을 다시 곱하지 않습니다. 포장단위 반올림·실제 재단·남는 자재는 주문 전 승인명세로 정리합니다. 다른 품목에는 손실10%를 자동 적용하지 않습니다.', '',
 '허용액은 **본공사 안에 한 번만 합산**합니다. 선택 확정 후 승인된 실제 구매/납품/반품명세를 기준으로 자재차액을 정산하는 조건을 계약에 별도 명시합니다. 허용액 안에 적합제품 공급이 어려우면 그 차액과 제품 근거를 회신하되 기본계산을 업체 임의로 바꾸지 않습니다.', '',
 '## 6. 공통 장비·준비수량','',
 tab(['기기ID','도면 모델','공통 비교수량','도면 냉방능력(kW/대)'],[(x['id'],x['model_reported'],x['common_pricing_quantity'],x['cooling_kw_reported']) for x in j['cooling_schedule']]), '',
 '실내기 합계11대, 실외기 합계2대. 위 수량/출력은 도면 기기표·모델문자에서 가져와 **가격비교 기준으로 채택**한 값이며, 실제 설치 위치/용량 적정성을 검증한 결과가 아닙니다. 제조사 선정서와 주거부하 계산으로 대조하고 최적화 가격은 ALT-07에 제출하십시오.', '',
 tab(['기기/준비','공통 비교수량','근거 구분'],[
 ('기름50S보일러/600L유류탱크/순환펌프','1대/1대/2대','도면수량 유지, 보일러모델 R1선정'),
 ('화장실 환기팬','4대','도면표기 수량 유지'),
 ('양변기/세면기/레인샤워/욕조','3/3/2/2','도면표기 수량 유지'),
 ('싱크수전/일반·부동수전','3/합계7','도면표기,7개 구성은부동5+일반2 R1해석')]+[(x['name'],str(x['quantity'])+' '+x['unit'],'R1 신규 건축주 비교수량') for x in j['new_owner_pricing_quantities']]), '',
 '## 7. 기본공사·지급품·공종 경계','',
 tab(['구분','공통 처리'],[
 ('시공사 구매/설치 기본','일반조명,창호/문,도면 고정가구,일반 위생기구,보일러/유류탱크/펌프,냉방기,환기기 및 배관배선/시운전'),
 ('건축주 지급 본체','냉장고·인덕션·오븐·식기세척기·세탁/건조기,주방후드 본체·장식펜던트,AP/공유기·제습기·이동가구/커튼'),
 ('지급품이어도 시공사 포함','도면/R1 기준 타공·전용회로·급배수/덕트·반입협의·최종 연결·보양. 제조사전문설치 필수 본체는 경계표시.'),
 ('옥외 굴착·되메우기·장비기초','건축/토목 가격행. 설비에서 다시 계상하지 않음.'),
 ('오수 배관','오수받이까지설비,이후관/기존관접속/복구는건축. 관저고와 연결점확인.'),
 ('온도조절기/실내기 점검구','조절기 배관·전원/통신선은전기,점검구/천장복구는건축. 제어기본체는설비범위와대조.'),
 ('세면카운터/거울','건축/가구 가격행. 세면기/수전/트랩은설비. 타공/실링 한 담당 명시.')]), '',
 '같은 작업이 여러 공종에 표시되어도 비용을 두 번 합산하지 않습니다. 각 업체는 타행 포함이면 정확한 ID를 적고, 모두 제외된 작업이 없도록 책임표를 회신하십시오.', '',
 '## 8. 별도 증감 견적','']
 for o in j['options']:
  lines += [anchor(o['id']),'### '+o['id']+' · '+o['title'],'',o['scope'],'','**회신:** '+o['return_requirement'],'']
 lines+=['## 9. 회신 내역과 비교 방법','',
 '각 행에 **항목ID·위치·규격/모델·단위·수량·도면/산출근거·자재비·노무비·장비비·금액·포함/제외/이견**을 적어 주십시오. 아래61개 원항목을 유지하고, 창호ID/관경/실별로 하위행을 추가하십시오. 원항목을 조용히 삭제하지 말고 해당없음/타행포함도 표시합니다.', '',
 tab(['항목ID','공종/작업','기본단위','적용 사양'],[(s['id'],s['name'],s['unit'],', '.join('[{}](#{})'.format(k,k.lower()) for k in j['scope_spec_mapping'][s['id']])) for s in scope]), '',
 '기본총액에는 공통 허용액을 포함하고 옵션은 제외합니다. 비교할 때는 먼저 도면 버전·범위·제품·수량·허용액을 맞춥니다. 미확인 암반/추가 지반개량·미상 관로는 발생조건/단가를 별도 기재하고, 도면 밖 물량을 업체마다 다르게 넣은 총액으로 순위를 매기지 않습니다. 이 조건부 비용이 남으면 발주자가 부담할 최종 총사업비도 아직 고정된 것이 아닙니다.', '',
 '## 10. 제출·변경 규칙','',
 '업체별 질의는 발주자에게 모아 회신받고, 가격·독자제안을 제외한 설계/범위 관련 공통 답변은 모든 업체에 동일하게 전달합니다. 회신에는 반영한 추가통보ID를 기재하십시오. 구두협의로 기준안 사양을 바꾸지 않습니다.', '',
 '사양 우선순위는 **공통 추가회신 → R1의 명시적 선택/추가/변경 → 첨부도면 → 제조사 시방**입니다. 다만 구조·법정 성능·안전과 충돌하면 이 순위로 강행하지 않고 담당 설계자에게 적합해법을 확인합니다. 계약/제작 승인 전에 도면·실측·제품별 제약을 대조합니다.', '',
 '행정 용도와 허가사항은 원본도서로 별도 관리하며, 본 문서의 주택 명칭은 실제 이용과 견적 성능 기준입니다. 이 문서가 행정서류를 변경하거나 주택 허가 취득을 의미하지는 않습니다.', '',
 '## 11. 제품 근거','',
 '제조사 공개 자료 확인일:2026-10-12. 모델/특성 확인과 현장 공급견적·재고·실제 시험성능은 구분합니다. 상세 성능목표와 비교 허용액은 발주 제안값입니다.']
 for r in sr['sources']:
  lines += ['',anchor(r['id']),'**'+r['id']+' · ['+r['title']+']('+r['url']+')**',r['verified_facts']+' '+r['limits']]
 tender='\n'.join(lines);write('TENDER.md',tender)
 owner=['# 건축주 사양 선정 이유와 비용 선택','',
 '**R0의 ‘사양을 결정해 달라’는 목록을 R1의 실제 비교견적 사양으로 바꿨습니다.** 구조/외관은 도면을 지키고, 교체가 어려운 방수·창접합·온돌·환기는 기본에 넣고, 장식·고가 수입품·열원 변경은 옵션으로 분리했습니다. 정답인 최저가 조합이나 현장 설계검증 완료를 뜻하지 않습니다.', '',
 '시공사에는 [통합 사양서](TENDER.md) 또는 `contractor/` 패키지를 도면3개와 함께 전달합니다. 이 페이지는 건축주와 분석 에이전트의 선택 이유 기록입니다.', '',
 tab(['유지/선정','이번 판단'],[
 ('주택 사용','건축주 직접 지시에 따라 명칭·부하·생활설비 기준은 주택. 행정 표기를 견적 보류 사유로 앞세우지 않음.'),
 ('기름50S 기본','기존 설계의 기름/50000급을 실제 겸용모델로 구체화. 히트펌프가 항상 싸다고 추정하지 않고 전환비·성능조건을 별도 비교.'),
 ('급탕200L탱크는 옵션','겸용보일러의 일상2샤워 요구조건부터 확인. 욕조 동시사용 때문에 필요한지 보고 추가.'),
 ('전열교환기 기본','주거용 기밀창과 함께 환기/점검구/덕트/소음까지 기본에 넣음. 단순 기기값만 견적받지 않음.'),
 ('국내AL창 기본','이건을 기준으로 동일자료로 비교. 모든 창에 특정계열을 억지로 맞추지 않으며 외관 분할변경은 별도.'),
 ('타일/도기 디자인','내구성 시스템은 지정하고 디자인은 표준규격·색과 동일 자재 허용액으로 통제.'),
 ('가구','도면 고정가구는 포함, 국산 표면재·단순 모듈·댐핑철물. 고급수입 주방·대형슬랩은 옵션.'),
 ('사업비','본공사/지급품/옵션/기관실비/지반조건부 비용을 나눔. 아직 모르는 물량을0원으로 감추지 않음.')]), '',
 '## 사양별 선택 근거','']
 for s in j['specifications']:
  owner += ['### '+s['id']+' · '+s['title'],'',s['selection_reason'],'','**구분:** '+s['decision_type'],'','[시공사 사양으로 이동](TENDER.md#'+s['id'].lower()+')','']
 owner += ['## 지금 건축주가 할 일','',
 '이번 사양서와 도면3개를 같은 업체들에 전달하고 견적을 받으면 됩니다. 색상/실측/최종제작도는 발주 시 승인하고, 원본에 없는 상세를 임의로 만들지 않는 대신 담당업체의 적합 선정서와 변경표를 받습니다. RFI자료를25건 모두 닫을 때까지 예산견적을 못 받도록 만들지 않았습니다.', '',
 '총예산, 착공일, 수신업체 확정 또는 실제 발송은 수행하지 않았습니다. 업체 단가와 공급재고도 아직 받지 않았으므로 자재 허용액을 ‘시장조사로 확인한 구매가’라고 사용하지 않습니다.']
 write('OWNER-DECISIONS.md','\n'.join(owner))
 research=['# 사양 리서치 — 제조사 근거와 발주 판단','',
 '**제품 사실·도면 표기·발주자 제안을 구분합니다.** 연구 대상은 합리적인 사양과 현행 확인 가능한 제품군입니다. 실제 제주 납품견적, 모든 제품의 재고/인증 최신본과 현장 시험은 별개입니다. 숫자가 들어 있다고 모두 법정 기준 또는 제조사 보장값인 것은 아닙니다.', '',
 tab(['구분','자료에서 의미하는 것'],[
 ('제조사 사실','13개 공식 제품/기술 출처에 있는 모델·규격·시스템 설명'),
 ('원본 사실','변환 DWG의 기기표·두께·실명 등. 원본/실측과 추가 대조 필요'),
 ('발주자 제안','22/26℃ 실내조건,2샤워,환기250급3대,실풍량/소음 목표,타일허용액 등 공통 비교 기준'),
 ('현장 확정','부하/풍압/유리/도막/부속/개소와 실제 도면 적합성 확인 후 제작 승인')]),'']
 for r in sr['sources']:
  research += [anchor(r['id']),'## '+r['id']+' · '+r['title'],'','[공식 원문]('+r['url']+') · 확인2026-10-12 · '+r['kind'],'',
   '**확인한 사실:** '+r['verified_facts'],'','**이번 적용/한계:** '+r['limits'],'']
 research+=['## 자재 허용액의 성격','',
 '타일/일부위생기구/일반등기구의 공통 자재 허용액은 디자인 미선정 때문에 업체별 자재등급이 달라지는 일을 막는 비교예산입니다. 시장 평균·제조사정가·최저가를 입증한 조사값이 아닙니다. 지정 제품군/크기/규격 안에서 제품을 제시하게 한 뒤, 실제 견적에 따라 구매와 계약금액을 조정합니다.']
 write('SPEC-RESEARCH.md','\n'.join(research))
 # Contractor-only static page has no link to our contractor scores, old RFIs, or internal reasoning.
 body=markdown.markdown(tender,extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'toc_depth':'2-2','slugify':lambda value,sep:'section-'+slugify(value,sep)}})
 body=body.replace('<table>','<div class="table-wrap" tabindex="0" aria-label="견적표 가로 스크롤"><table>').replace('</table>','</table></div>')
 package_html='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>제주 주택 신축공사 — 시공사 견적사양 R1</title><link rel="stylesheet" href="style.css"></head><body><main style="max-width:1120px;margin:24px auto"><div class="meta"><b>시공사 전달용 / R1</b><span><a href="SPECIFICATIONS.md">문서 원본</a> · <a href="specifications.json">사양 JSON</a> · <a href="quote-return.json">견적 회신 양식</a> · <a href="DRAWING-MANIFEST.json">도면 목록</a></span></div><article>'''+body+'''</article></main></body></html>'''
 write('contractor/index.html',package_html);write('contractor/SPECIFICATIONS.md',tender)
 write('contractor/specifications.json',json.dumps(j,ensure_ascii=False,indent=2))
 write('contractor/quote-return.json',json.dumps(get('tender-response-template.json'),ensure_ascii=False,indent=2))
 manifest=get('source-manifest.json')
 write('contractor/DRAWING-MANIFEST.json',json.dumps({'package_id':j['package_id'],'note':'발주자가 별도 전달할 DWG3개. 이 패키지에는 원본 CAD가 들어 있지 않다. 수신일은 도면의 정식 발행일이 아님.','files':[{k:s[k] for k in ['source_id','filename','bytes','sha256','received_date']} for s in manifest['sources']]},ensure_ascii=False,indent=2))
 write('contractor/README.md','''# 제주 주택 견적 요청 자료 R1

`index.html`을 브라우저에서 열거나 `SPECIFICATIONS.md`를 읽고 견적을 작성해 주십시오. `quote-return.json`은 기계판독 회신 양식이며 동일 항목ID/내용을 유지하는 다른 표 형식도 가능합니다.

본 묶음은 건축주 지정사양·견적조건·회신양식입니다. **원본 DWG3개는 발주자가 별도로 전달합니다.** `DRAWING-MANIFEST.json`의 파일명과 해시로 같은 도서인지 확인하십시오.

사양서의 기준안으로 먼저 가격을 제출하고, 대체/옵션·조건부 작업은 별도 증감과 근거를 기재하십시오. 실제 시공/제작은 도면·부하/안전 검토와 승인 후 진행합니다. 작성된 업체 견적과 담당자 정보는 공개 저장소에 올리지 말고 발주자에게 비공개로 회신해 주십시오.
''')
 (P/'contractor/style.css').write_bytes((P/'style.css').read_bytes())
 archive=P/'jeju-house-contractor-R1.zip'
 allowed=['README.md','SPECIFICATIONS.md','index.html','style.css','specifications.json','quote-return.json','DRAWING-MANIFEST.json']
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in allowed:
   zi=zipfile.ZipInfo('jeju-house-R1/'+name,date_time=(2026,10,12,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(zi,(P/'contractor'/name).read_bytes())
 print(json.dumps({'owner_specifications':len(j['specifications']),'sources':len(sr['sources']),'contractor_files':len(allowed),'zip':archive.name},ensure_ascii=False))
if __name__=='__main__':main()
