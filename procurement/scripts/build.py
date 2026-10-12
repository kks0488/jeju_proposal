#!/usr/bin/env python3
"""Build public, static procurement pages from reviewed Markdown/JSON only.
No raw CAD import, no network, no publication, no private bid processing.
"""
import collections
import html
import json
import re
from pathlib import Path
import markdown
from markdown.extensions.toc import slugify

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
PAGES = [
 ('README','시작·핵심 결론'), ('DRAWING-REVIEW','도면 검토 결과'),
 ('PREPARATION','우리가 준비할 것'), ('RFI','설계 질의 25건'),
 ('RFQ','시공사 견적요청서'), ('BID-RETURN','견적 회신·비교 규칙'),
 ('SCOPE','공통 견적항목'), ('RESPONSIBILITY','공종 책임표'),
 ('DRAWING-REGISTER','도면번호 목록'), ('EQUIPMENT','장비 표기 수량'),
 ('REQUIREMENTS','기존 요청 대조'), ('ADDENDUM','공통 추가통보'),
 ('QUANTITY-PROTOCOL','물량산출 검증 규칙'), ('AGENTS','에이전트 작업 지침'),
 ('EVIDENCE','원문 근거 발췌')]

def read(name):
 return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

def cell(s):
 return str(s if s is not None else '미확정').replace('|','&#124;').replace('\n','<br>')

def eid(s):
 return s.lower().replace(':','-')

def refs(values):
 return ' · '.join('[{}](EVIDENCE.md#{})'.format(x,eid(x)) for x in values) or '별도 근거/결정 필요'

def write(name,lines):
 (ROOT/name).write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip()+'\n',encoding='utf-8')

def table(headers,rows):
 return ['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(cell(v) for v in row)+' |' for row in rows]

def generated_markdown():
 d=read('drawings.json')['drawings']
 lines=['# 도면번호 목록: 발행본 확인 전 후보 등록부','',
  '**{}개 고유 번호 후보입니다. 공식 PDF 시트 수 또는 설계 완결성을 확인한 목록이 아닙니다.** 원본 발행일·개정번호는 모두 미확정입니다.'.format(len(d)),
  '', 'S-004·S-007은 각각 두 위치에서 같은 번호가 검출됐습니다. S-305·S-306은 본문 번호만 확인했습니다. A-406은 목록 행의 존재와 실제 본문 발행 여부를 구분합니다.',
  '', '[정본 JSON](data/drawings.json) · [원본 정보](data/source-manifest.json)', '']
 for group in ['A','S','E','T','M','MA']:
  subset=[x for x in d if x['discipline']==group]
  lines+=['## {} · {}개'.format(group,len(subset)),'']
  labels={'index_row_detected':'목록 행 검출','body_number_detected':'본문 번호 검출','duplicate_number_locations':'동일 번호 다중 위치'}
  lines+=table(['번호','제목','검토 상태','축척 표기','근거'],[(x['id'],x['title'],labels[x['status']],', '.join(x['scale_text']) or '별도 확인',refs(x['evidence_refs'])) for x in subset])+['']
 write('DRAWING-REGISTER.md',lines)
 r=read('rfi.json'); rows=r['items']; p0=[x for x in rows if x['priority']=='P0']
 lines=['# 설계 질의·준비 확인사항','',
  '**총 {}건 · 발행 전 기준 확인 P0 {}건 · 현재 모두 미종결.** 질의가 있다는 것만으로 도면 오류가 확정된 것은 아닙니다.'.format(len(rows),len(p0)),
  '', 'P0: '+r['priority_definition']['P0'], '', 'P1: '+r['priority_definition']['P1'],
  '', '[정본 JSON](data/rfi.json) · [설계사 요청 문안](PREPARATION.md) · [회신 발행 양식](ADDENDUM.md)','']
 lines+=table(['ID','우선','제목','회신 담당'],[(f'[{x["id"]}](#{x["id"].lower()})',x['priority'],x['title'],x['assignee_role']) for x in rows])+['']
 for x in rows:
  lines+=['<a id="{}"></a>'.format(x['id'].lower()),'## {} · {}'.format(x['id'],x['title']),'',
   '**{} · 담당: {} · 상태: 미종결**'.format(x['priority'],x['assignee_role']),'',
   '**관찰:** '+x['observation'],'','**요청:** '+x['request'],'','**견적 영향:** '+x['bid_impact'],'',
   '**근거:** '+refs(x['evidence_refs'])]
  if x['prior_source']:lines+=['','**이전 기록:** '+x['prior_source']]
  lines+=['','**회신·승인·추가통보:** 미입력. 답변자/일자·승인자·도면/개정·ADD-ID 확인 후 종결.','']
 write('RFI.md',lines)
 eq=read('equipment.json')['items']
 lines=['# 장비·위생기구 표기 수량','',
  '**기기 일람표에서 전사한 수량입니다. 실제 평면 기호·설치 위치를 대조한 적산 수량이나 발주 승인 수량이 아닙니다.** 모든 `verified_quantity`는 null, 주문 승인은 false입니다.',
  '', 'MA-01 표기 합계는 실내기11대·실외기2대입니다. Ø15수전의 합계7과 비고 부동수전5EA는 구성 확인사항이며 합산하지 않습니다. 모델/성능·각 공간 적용 범위는 설계자 확인이 필요합니다.',
  '', '[정본 JSON](data/equipment.json) · [RFI-012](RFI.md#rfi-012) · [RFI-014](RFI.md#rfi-014)','']
 lines+=table(['ID','기기','표기 수량(EA)','표기 사양/한계','도면','근거'],[(x['id'],x['name'],x['reported_quantity'],x['spec_observed'],x['source_sheet'],refs(x['evidence_refs'])) for x in eq])
 write('EQUIPMENT.md',lines)
 s=read('scope-items.json')['items']
 lines=['# 공통 견적항목: {}개 발주 범위 초안'.format(len(s)), '',
  '**완성 물량내역서가 아닙니다. 모든 발주자 수량은 미산출(null), 공통 사양은 미승인입니다.** 도면ID·위치·재질·관경·창호별 하위행을 나눈 뒤 공통 발행본을 고정합니다.',
  '', '이 공종 분류는 검토자가 제안한 견적 관리 기준이며, 개별 항목의 존재·수량·필요성이 모두 도면에서 확정됐다는 뜻은 아닙니다. 해당없음/옵션/타행포함도 답변하고 원항목을 조용히 삭제하지 않습니다. 식 단위는 세부내역 생략 허용이 아닙니다.',
  '', '[빈 회신 JSON](data/bid-template.json) · [회신 규칙](BID-RETURN.md) · [정본 JSON](data/scope-items.json)','']
 for g in dict.fromkeys(x['group'] for x in s):
  subset=[x for x in s if x['group']==g]; lines+=['## '+subset[0]['group_title'],'']
  lines+=table(['ID','항목','기본단위','수량','세분화·산출 기준'],[(x['id'],x['name'],x['unit'],'미산출',x['measurement_basis']) for x in subset])+['']
 write('SCOPE.md',lines)
 req=read('requirements.json')
 lines=['# 기존 설계 요청과 이번 도면의 대조','',req['basis'],'',
  '**기존 요청을 이번 도면의 확정 사실로 합치지 않았습니다.** 부분 근거·검토 필요·미검증으로 구분하며 승인 처리한 항목은 없습니다.',
  '', '[정본 JSON](data/requirements.json) · [기존 기록](../RESEARCH.md)','']
 status={'partial':'부분 근거 / 승인 전','review_required':'기술 검토 필요','not_verified':'이번 검토에서 미검증'}
 lines+=table(['요구ID·주제','이전 요청','현재 근거/한계','상태','관련 질의'],[(x['id']+' '+x['title'],x['prior_request'],x['current_evidence_summary'],status[x['status']], ' · '.join('[{}](RFI.md#{})'.format(r,r.lower()) for r in x['rfi_refs'])) for x in req['items']])
 write('REQUIREMENTS.md',lines)
 e=read('evidence.json'); records=e['records']; manifest=read('source-manifest.json')
 lines=['# 도면 원문 근거 발췌','',
  '**{}개 선별 레코드. 모두 변환 DXF 문자이며 원본 CAD/PDF 시각대조·설계승인은 미완료입니다.** 내부 작업 메모와 전체 도면 원문은 공개하지 않습니다.'.format(len(records)),
  '', e['coordinate_note'],'', '표시용 문서에서는 줄 끝 공백만 정리했습니다. 추출된 원문 문자열은 JSON에 보존합니다.','', '[정본 JSON](data/evidence.json) · [원본 해시/변환 제한](data/source-manifest.json)','']
 lines+=table(['소스ID','파일','SHA-256'],[(s['source_id'],s['filename'],s['sha256']) for s in manifest['sources']])+['']
 for x in records:
  lines+=['<a id="{}"></a>'.format(eid(x['id'])),'### '+x['id'],'',
   '`{}` · 레이어 `{}` · 컨테이너 `{}` · xy `{}`'.format(x['type'],x['layer'],x['container'],x['xy']),
   '', '```text', x['text'], '```', '']
 write('EVIDENCE.md',lines)

def url_for(stem):
 return 'index.html' if stem=='README' else stem+'.html'

def build_html():
 available={s for s,_ in PAGES}
 for stem,label in PAGES:
  source=ROOT/(stem+'.md'); text=source.read_text(encoding='utf-8')
  md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'toc_depth':'2-3','slugify':lambda value,sep: 'section-'+slugify(value,sep)}})
  content=md.convert(text)
  # Rewrite only this package's generated pages, not unrelated root documentation.
  def rewrite(m):
   target,anchor=m.group(1),m.group(2) or ''
   return 'href="'+url_for(target)+anchor+'"' if target in available else m.group(0)
  content=re.sub(r'href="([A-Z][A-Z-]*)(?:\.md)(#[^"]*)?"',rewrite,content)
  content=content.replace('<table>','<div class="table-wrap" tabindex="0" aria-label="표 가로 스크롤"><table>').replace('</table>','</table></div>')
  title=re.sub(r'^#\s*','',text.splitlines()[0]); nav=''.join('<a {} href="{}">{}</a>'.format('aria-current="page"' if name==stem else '',url_for(name),html.escape(lab)) for name,lab in PAGES)
  toc='' if stem in ('README','EVIDENCE','DRAWING-REGISTER') else '<details class="toc"><summary>이 문서 목차</summary>'+md.toc+'</details>'
  jumps=''
  if stem=='README':
   jumps='<div class="quick"><a href="PREPARATION.html"><small>건축주·설계자</small>먼저 준비할 것 →</a><a href="RFQ.html"><small>시공업체 전달</small>견적요청서 →</a><a href="AGENTS.html"><small>Codex · Claude Code</small>자료와 근거 읽기 →</a></div>'
  page='''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="제주 건축 도면 검토와 공통 비교견적 준비. 도면 근거·준비사항·질의·견적 양식."><title>'''+html.escape(title)+''' | 제주 견적 준비</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#content">본문으로 이동</a><header class="top"><a class="brand" href="index.html">JEJU <span>도면·견적 준비</span></a><div><span class="status">검토 초안 · 미발행</span><a href="../index.html">시공사 비교 ↗</a></div></header>
<div class="layout"><aside><p class="section-label">PROCUREMENT / 2026.10.12</p><nav aria-label="자료 메뉴">'''+nav+'''</nav><div class="aside-note">원본 DWG·업체 가격은 비공개.<br>도면 표기 ≠ 검증 수량 ≠ 승인.</div></aside><main id="content"><div class="meta"><span>JEJU-RFQ-PREP-20261012-R0</span><a href="'''+source.name+'''">Markdown 원문</a></div>'''+jumps+toc+'<article>'+content+'''</article><footer>문자·목록 1차 검토 자료입니다. 공식 발행본 대조·물량산출·설계승인을 대체하지 않습니다.<br><a href="data/project.json">현재 상태 JSON</a> · <a href="data/source-manifest.json">원본 식별·검토 범위</a></footer></main></div></body></html>'''
  (ROOT/url_for(stem)).write_text(page,encoding='utf-8')

def link_gallery():
 for rel,url in [('index.html','./procurement/'),('site-v3/published/index.html','../../procurement/')]:
  p=REPO/rel
  if not p.exists():continue
  text=p.read_text(encoding='utf-8')
  # Idempotent, narrowly scoped insertions. Existing content is otherwise preserved.
  text=re.sub(r'<!--procurement-nav-start-->.*?<!--procurement-nav-end-->','',text,flags=re.S)
  text=re.sub(r'<!--procurement-start-->.*?<!--procurement-end-->','',text,flags=re.S)
  nav='<!--procurement-nav-start--><a class="research-nav" href="'+url+'">도면·견적 준비</a><!--procurement-nav-end-->'
  text=text.replace('</nav>',nav+'</nav>',1)
  strip='<!--procurement-start--><section aria-label="도면·견적 준비" style="margin:24px 0;padding:24px;border:1px solid #bbc8b8;border-radius:14px;background:#f0f4ec;color:#23332b"><p style="font-size:12px;letter-spacing:.08em;margin:0 0 8px">2026.10.12 · 도면 3개 검토 · 미발행 초안</p><h2 style="margin:0 0 10px;font-size:25px">같은 기준으로 견적 받기</h2><p style="margin:0 0 14px;line-height:1.7">도면 검토 결과, 준비사항, 설계 질의, 시공사 공통 견적요청서와 회신 양식을 한곳에 모았습니다. 도면상 용도·발행본 확인이 먼저입니다.</p><a style="color:#194f3d;font-weight:700" href="'+url+'">도면·견적 준비 자료 보기 →</a></section><!--procurement-end-->'
  if '<!--research-start-->' in text:text=text.replace('<!--research-start-->',strip+'<!--research-start-->',1)
  else:
   marker='<section class="company-grid"'
   if marker not in text:raise RuntimeError('Cannot locate safe insertion point in '+rel)
   text=text.replace(marker,strip+marker,1)
  p.write_text(text,encoding='utf-8')

def main():
 generated_markdown(); build_html(); link_gallery()
 print(json.dumps({'generated_md':6,'html_pages':len(PAGES),'gallery_entry_links':2,'network_used':False},ensure_ascii=False))
if __name__=='__main__':main()
