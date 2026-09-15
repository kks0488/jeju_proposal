from pathlib import Path
import json, html, csv
R=Path(__file__).resolve().parent
D=json.loads((R/'research.json').read_text())
def e(x):return html.escape(str(x),quote=True)
def a(u,t):return f'<a href="{e(u)}" target="_blank" rel="noopener noreferrer">{e(t)} ↗</a>' if u else ''
def table(h,rs):return '<div class="table-wrap"><table><thead><tr>'+''.join('<th scope="col">'+e(x)+'</th>' for x in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(x)+'</td>' for x in row)+'</tr>' for row in rs)+'</tbody></table></div>'
cards=[]
for i,c in enumerate(D['candidates']):
 ps=''.join('<li><b>'+e(p['name'])+'</b><span class="small">'+e(p['type'])+'</span><p>'+e(p['spec'])+'</p><p class="muted">'+e(p['match'])+'</p>'+a(p['source'],p['sourceLabel'])+'</li>' for p in c['projects'])
 cards.append(f'<article class="candidate" id="{c["id"]}" data-group="{e(c["group"])}"><div class="candidate-head"><div><span class="badge">{e(c["group"])}</span><h3>{e(c["name"])}</h3><p class="muted">{e(c["local"])}</p></div><span class="number">{i+1:02}</span></div><p>{e(c["reason"])}</p><div class="contact">{e(c["contact"])} · {a(c["website"],"공개 근거")}</div><details><summary>사례·근거 {len(c["projects"])}건과 검증 질문</summary><ul class="projects">{ps}</ul><dl><dt>확인한 근거</dt><dd>{e(c["evidence"])}</dd><dt>아직 확인하지 못한 것</dt><dd>{e(c["unknown"])}</dd><dt>먼저 물을 질문</dt><dd>{e(c["question"])}</dd></dl></details></article>')
q=[('공통','도서 버전·견적 유효기간','동일 도서와 공통 질의회신'),('공통','부가세·간접비·현장관리비','포함 여부·산출 기준'),('공통','계약 법인·등록·보증','수급인·통장·보증 명의'),('토공','철거·굴착·암반·반출','물량·단가·정산 조건'),('토공','성토·다짐·시험','종류·횟수·재시험 비용'),('외부','옹벽·배면배수·자연석','구조체와 마감 물량 분리'),('외부','트렌치·집수정·최종 우수처리','승인도서 기준 관경·길이·레벨'),('골조','기초·RC·다락·지붕 구조','구조도·물량·콘크리트 시험·양생'),('골조','슬리브·관통부·매립철물','타설 전 통합 검토'),('외피','지붕 바탕·금속 마감·철물','제품·강풍·결로·부식 대응'),('외피','자연낙수 받이·물끊기·배수','지붕과 외부공사 사이 누락 방지'),('외피','외단열·석재·앵커·기단','줄눈·방수·열교 상세'),('창호','프레임·유리·앵커·설치 방수','일람표별 규격·성능·보증·검사'),('방수','테라스·욕실·창호 하부','층 구성·물량·시험·책임'),('마감','비내력벽·천장·차음·보강','공용부 최종 CH 3,200 요청 반영'),('마감','바닥·도장·문·타일·몰딩','제품명 또는 잠정금액·견본'),('가구','주방·붙박이·상판·욕실가구','건축주 별도 발주와 구분'),('설비','냉난방·환기·급배수·제습','설비검토 후 모델 확정·시운전'),('전기','조명·전력·통신·외부전기','기구 공급·배선·설치 범위'),('외부','난간·포장·계단·대문·조경','염해·고정·마감·토목 경계'),('기타','인입·검사·사용승인 지원','부담금·대관 비용 포함 여부'),('기타','보양·청소·준공도서','시운전·사용법·시험 결과 인계'),('관리','소장·공정표·보고·변경관리','상주·동시 현장·주간보고'),('관리','하자보증·긴급출동·점검','금액·기간·면책·응답기한 합의'),('총괄','제외공사·잠정금액·변경단가','누락과 별도공사 합산 비교')]
(R/'templates').mkdir(exist_ok=True)
with (R/'templates/quote-comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['공종','항목','확인 범위','업체A 금액','업체A 포함/제외/잠정','업체B 금액','업체B 포함/제외/잠정','업체C 금액','업체C 포함/제외/잠정','지인소개 금액','지인소개 포함/제외/잠정','근거·회신']);w.writerows([*r,*['']*9] for r in q)
with (R/'templates/contractor-evaluation.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['업체','항목','배점','획득점수(미검증 빈칸)','증빙·날짜','검토자'])
 for c in [*D['candidates'],{'name':'지인 소개 업체'}]:
  for t,n,b in D['weights']:w.writerow([c['name'],t,n,'','',''])
  for g in ['계약 법인·등록·보증','배정 소장·동시 현장','유사 실적·건축주 확인','설계자 승인·변경관리']:w.writerow([c['name'],'필수 통과: '+g,'점수와 별도','미확인','',''])
inquiry='''안녕하세요. 제주 서귀포권 단층 중심 주택의 시공사를 검토하고 있습니다.
설계는 상당 부분 진행되어 있으며, 기존 설계를 유지한 시공 수주 가능 여부를 먼저 확인하고 싶습니다.
RC 본체, 박공지붕, 석재 외장, 대형 창호, 외부 레벨·옹벽·배수의 정밀한 시공이 중요한 프로젝트입니다. 정확한 면적과 공사 범위는 최신 도서 확인 후 공통 자료로 제공할 예정입니다.

1. 최근 5년 이내 직접 시공한 주택 3건의 준공연도·연면적·직접 수행 범위·당시 소장·설계자를 알려주십시오. 형태나 구조가 똑같을 필요는 없습니다. 규모·방수·단열·창호 등에서 역량을 보여주는 실거주 주택과 현재 설계의 수주 가능 범위를 알려주십시오.
2. 공사 중 현장 1곳과 준공 후 2년 이상 지난 주택 1곳을 설계자와 함께 볼 수 있는지, 건축주 동의를 전제로 확인 부탁드립니다.
3. 배정 가능한 현장소장, 상주 방식, 동시 진행 현장 수, 착공 가능 시기를 알려주십시오.
4. 계약 법인명·건설업 등록·보증 발급 가능 여부와 하자 담당 조직을 알려주십시오.
5. 기존 설계자의 상세 검토 및 변경 전 서면 승인 절차에 동의하는지 확인 부탁드립니다.

첫 회신은 참여 가능 여부와 위 실적자료 중심이면 됩니다. 정식 견적은 공통 도서·공통 범위로 요청할 예정입니다. 감사합니다.'''
(R/'templates/inquiry.txt').write_text(inquiry)
sources=[]
for c in D['candidates']:
 sources.append((c['name']+' — 업체·연락 경로',c['website']))
 sources.extend((c['name']+' — '+p['name'],p['source']) for p in c['projects'])
sources.extend((x[0],x[2]) for x in D['extras'] if x[2])
seen=set();sources=[x for x in sources if not (x[1] in seen or seen.add(x[1]))]
page='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>제주 주택 시공사 검토 | Jeju Proposal</title><meta name="description" content="제주 주택 시공사 실적 비교와 현장 검증·견적 준비"><link rel="stylesheet" href="style.css"></head><body>
<header><a class="brand" href="index.html">JEJU <b>PROPOSAL</b></a><span>시공사 선정 준비 · 2026.09.09</span><button id="print" type="button">인쇄 / PDF</button></header>
<nav aria-label="목차"><a href="ranking.html">점수·순위</a><a href="portfolio.html">다른 업체 포트폴리오</a><a href="review.html">결과물 정밀 검토</a><a href="#shortlist">후보 비교</a><a href="#basis">현재 설계</a><a href="#verify">검증 기준</a><a href="#quote">견적 준비</a><a href="#sources">근거·한계</a><a href="history/archive.html">이전 논의</a></nav><main>
<section class="intro"><p class="eyebrow">CONTRACTOR REVIEW</p><h1>설계를 끝까지 구현할<br>제주 시공사 찾기</h1><p>제주에 실제 팀이 있고, 오래 살 집을 제대로 완성하며 하자에 책임지는 업체를 찾습니다. 형태가 같은 집을 지었는지는 필수 조건이 아닙니다.</p><div class="notice">현재는 <b>공개자료 기반 후보 검토</b> 단계입니다. 견적·현장방문·등록 및 보증·하자 이력 검증을 마친 업체는 아직 없습니다.</div></section>
<section class="panel"><h2>세 시공사의 준공 사진집</h2><p>하백·이아컴퍼니, GAU, 다봄의 10개 프로젝트·26장. 사진이 포함된 HTML 파일로 업체별 보기와 확대가 가능합니다.</p><a class="button" href="contractor-gallery.html">준공 사진 비교하기</a></section><section class="panel"><h2>9월 15일 심층 보완: RC 반복 실적과 입주 후 문제</h2><p>다봄의 RC 주택 2건과 소원재 6년차 거주자의 공정 불만을 추가 확인했습니다. GAU의 항심당·월정리 실적과 A/S 약속도 대조했습니다. 이전 신규 후보 4곳 조사도 함께 볼 수 있습니다.</p><a class="button" href="review.html#expanded">새 후보와 추가 검증 결과 보기</a></section><section class="panel"><h2>같은 기준으로 매긴 점수와 순위</h2><p>하백·GAU 공동 1위. 13개 후보의 항목별 점수·원문 근거·가중치에 따른 순위 변화를 공개합니다. 미확인 항목을 시공 불량으로 해석하지 않습니다.</p><a class="button" href="ranking.html">100점 기준 채점표 보기</a></section><section class="panel"><h2>현재 판단을 바꾼 심층 검증</h2><p>11개 현장의 공사 책임과 반복 팀을 대조했습니다. 포엠의 기존 보류 판단을 수정했고, 하백·GAU를 우선 현장검증 대상으로 봅니다.</p><a class="button" href="review.html#responsibility">도급범위·반복 협력사·판단 근거</a></section><section class="panel"><h2>다른 업체도 포트폴리오로 비교</h2><p>하백·GAU의 실제 도급범위와 반복 협력사, 포엠 필하우스 RC 상세, 시스홈 산방풍경의 제주 실적을 추가 확인했습니다.</p><a class="button" href="portfolio.html">9개 추가 후보 정밀 비교</a></section><section class="panel"><h2>업체가 중시하는 것과 실제 결과물</h2><p>호미·솔비나무집·애월 공방주택의 시공 역할, 협회 인증번호, 신창리 공정 기록까지 추가 대조했습니다. 기존 갤러리 16장과 이번 필하우스 외관 1장을 직접 검토했습니다.</p><a class="button" href="review.html">업체별 판단과 심층 검증 보기</a></section><section id="shortlist"><h2>먼저 검토할 업체</h2><div class="decision"><div><p class="eyebrow">첫 번째 비교</p><h3>이아컴퍼니 / 하백 · GAU · JEJUPH</h3><p>건축가 주택의 완성도는 이아컴퍼니·GAU, 외피 성능 기록은 제주패시브하우스를 먼저 비교합니다. 오름건설·이음건설·포엠에도 자료를 요청할 가치가 있습니다. 목조 주력 업체도 시공 역량과 제주 상주팀을 기준으로 검토합니다.</p></div><div class="decision-note"><strong>아는 업체도 같은 기준으로</strong><p>소개 경로와 관계없이 실적·소장·하자 대응·동일 범위 견적을 확인합니다. 사진이나 친분만으로 계약을 앞당기지 않습니다.</p></div></div>
<div class="filters" role="group" aria-label="후보 필터"><button class="active" data-filter="전체" aria-pressed="true">전체 12</button><button data-filter="우선 검토" aria-pressed="false">우선 검토 3</button><button data-filter="추가 검증" aria-pressed="false">추가 검증 6</button><button data-filter="보류·참고" aria-pressed="false">보류·참고 3</button><span id="result-count" aria-live="polite">12개 업체·협업팀</span></div><p class="small">목록 번호는 품질 순위가 아닙니다. 우선 검토는 자료·면담을 먼저 진행할 후보이며 계약 추천 확정이 아닙니다.</p><div class="candidate-grid">'''+''.join(cards)+'''</div>
<figure class="reference"><img src="https://iacompany.co.kr/image/project/hwabun/hwabunmain.jpg" alt="이아컴퍼니가 공개한 제주 함덕리 단층 주택 화분의 완공 전경" loading="lazy" width="1440" height="800"><figcaption>비교 사례: 화분 · 우리 집의 현재 설계가 아닙니다. <a href="https://iacompany.co.kr/projects/hwabun/" target="_blank" rel="noopener noreferrer">사진 출처: 이아컴퍼니 ↗</a>이미지 권리는 원권리자에게 있습니다.</figcaption></figure></section>
<section id="basis"><p class="eyebrow">DESIGN BASIS</p><h2>현재 설계에서 가져올 선정 조건</h2><p>9월 8일 수정도면 송부와 후속 메일을 기준으로 정리했습니다. 건축주 요청과 도면 반영 완료를 구분합니다.</p><div class="notice">'''+e(D['basis'])+''' 정확한 면적·구조·규격은 최신 PDF 도서와 대조한 후 발주 기준으로 확정합니다.</div>'''+table(['항목','현재 방향','근거·상태','견적 전 확인'],D['requirements'])+'''<details><summary>이전 요청과 달라진 부분</summary><p>9월 4일 매립 수평홈통 우선 검토에서, 9월 8일에는 박공지붕 자연낙수 방향에 동의했습니다. 매립 홈통을 필수 조건으로 채점하지 않고, 낙수선·외부배수·물튀김 대책을 확인합니다.</p><p>기존 HTML의 2층 구성·면적·계단·이미지는 과거 논의로, 현재 배포할 도면이 아닙니다.</p></details></section>
<section id="verify"><p class="eyebrow">EVIDENCE BEFORE CONTRACT</p><h2>실력을 확인하는 순서</h2><div class="steps"><article><b>01</b><h3>자료로 선별</h3><p>최근 5년 유사 실적 3건, 계약 법인, 수행 범위, 담당 소장, 현재 공사 수. 공동 시공은 역할을 구분합니다.</p></article><article><b>02</b><h3>두 종류 현장</h3><p>공사 중 현장 1곳과 입주 2년 이상 주택 1곳. 건축사 동행과 건축주 동의하에 실제 상태를 확인합니다.</p></article><article><b>03</b><h3>같은 조건 견적</h3><p>같은 도서·질의회신을 제공합니다. 포함·제외·잠정금액을 맞춘 뒤 총액을 비교합니다.</p></article><article><b>04</b><h3>사람·책임 확정</h3><p>소장·전문업체·공정·변경 절차·기성·보증·하자 대응을 계약에 반영한 뒤 결정합니다.</p></article></div>
<h3>점수보다 먼저 통과할 4가지</h3><ul class="gate-list"><li><b>계약 법인·등록·보증</b> — 수급인과 등록 업종, 보증 발급 주체 확인</li><li><b>실제 현장소장</b> — 이름·재직·상주 방식·동시 현장 수 공개</li><li><b>유사 실적·레퍼런스</b> — 수행 범위, 건축주·설계자 확인 동의</li><li><b>설계 준수·변경관리</b> — 상세 검토와 변경 전 비용·기간 서면 승인 수용</li></ul><p class="muted">미확인은 탈락 판정과 다릅니다. 확인 전 계약 후보 확정을 보류하고, 거절·불일치가 확인되면 사유와 증빙을 기록합니다.</p>
<h3>우리 집을 기준으로 묻는 기술 질문</h3>'''+table(['항목','질문','확인할 증거','주의할 답변'],D['technical'])+'''
<div class="two-col"><article class="panel"><h3>공사 중 현장에서</h3><ul><li>철근·매립물·슬리브의 타설 전 확인 기록</li><li>석재·창호·단열·방수의 덮기 전 상태</li><li>자재 보관·양생·정리·안전 관리</li><li>도면과 다른 부분의 질의·승인 기록</li><li>소장이 도면으로 답하는지, 공종 책임자가 있는지</li></ul></article><article class="panel"><h3>입주 후 건축주에게</h3><ul><li>태풍·장마 후 누수·역류·물튀김이 있었는가</li><li>결로·곰팡이·환기 불편은 있었는가</li><li>금액·기간이 늘어난 이유와 승인 방식은</li><li>하자 신고부터 응답·완료까지 걸린 시간은</li><li>같은 소장·업체에 다시 맡기겠는가, 이유는</li></ul></article></div>
<h3>계약 전 현장 평가표 · 공개자료 채점과 별도</h3>'''+table(['항목','배점','증거'],D['weights'])+'''<p>아래는 향후 현장·견적 검증용 평가표입니다. 현재 공개자료의 근거 점수는 <a href="ranking.html">별도 채점표</a>에 있습니다. 현장 평가 등급 0–5를 정하고 <b>배점 × 등급 ÷ 5</b>로 환산합니다. 0은 미충족 확인, 3은 요구 충족, 5는 반복 실적과 현장 검증까지 우수한 경우입니다. <b>미검증은 빈칸</b>으로 두고 총점 순위를 매기지 않습니다.</p><a class="button" href="templates/contractor-evaluation.csv" download>평가표 CSV 받기</a></section>
<section id="quote"><p class="eyebrow">BID PREPARATION</p><h2>바로 사용할 견적·문의 준비</h2><div class="notice"><b>업체 발굴은 지금 시작할 수 있습니다.</b> 정식 견적은 도서와 미확정 사항을 통일한 뒤 요청합니다. 도면 공백을 각 업체의 임의 사양으로 채우면 총액을 비교하기 어렵습니다.</div><div class="two-col"><article class="panel"><h3>공통 배포 자료</h3><ol><li>도면 목록·발행일·수정 이력</li><li>건축개요·배치·평면·입면·단면</li><li>구조·성토·기초·옹벽 자료</li><li>지붕·창호·석재·방수 핵심 상세</li><li>기계·전기·환기·천장 통합 조건</li><li>배수·조경·인입·별도공사 범위</li><li>미확정 항목과 공통 잠정금액</li><li>현장조건·목표 일정·별도 발주품</li></ol></article><article class="panel"><h3>견적을 비교하는 방식</h3><p>총액에 제외공사·별도구매·동일 사양 보정액을 더해 비교합니다. 잠정금액은 확정 공사비와 나눠 봅니다.</p><p>암반·반출·성토·외부배수·창호·석재·가구·조경은 별도 행으로 확인합니다.</p><p><b>견적·예산 적합성·착공 가능일은 모두 미확인</b>입니다. 평당 가격을 추정해 순위를 만들지 않았습니다.</p><a class="button" href="templates/quote-comparison.csv" download>공종별 견적 비교표 CSV 받기</a></article></div><details><summary>견적 항목 25개 보기</summary>'''+table(['공종','항목','확인 범위'],q)+'''</details><h3>첫 문의 문안</h3><p class="muted">발송 전 검토용입니다. 문의·예약·도면 전송은 이루어지지 않았습니다.</p><textarea id="inquiry" rows="14" aria-label="시공사 문의 문안">'''+e(inquiry)+'''</textarea><div class="actions"><button id="copy" type="button">문안 복사</button><a href="templates/inquiry.txt" download>텍스트 파일 받기</a><span id="copy-status" role="status"></span></div>
<details><summary>계약 협의에 남길 항목</summary><ul><li>계약 법인·등록·통장·보증의 명의와 책임 범위</li><li>계약 도서 목록, 상충 시 처리·설계자 확인 절차</li><li>소장 지정·교체 승인·공정·주간 보고</li><li>타설·방수·매립·마감 전 검측과 기준</li><li>변경 전 금액·기간 승인·미확정 항목 정산</li><li>기성 확인 후 지급·선급금과 보증 조건</li><li>준공도서·시험·시운전·교육·하자 항목 인계</li><li>하자 기간·금액·면책·긴급 대응·정기점검</li><li>지연·중단·타절·인계·분쟁 처리</li></ul><p>협의용 목록입니다. 구체적인 기간·금액·특약과 법적 적용은 계약 전 담당 전문가 검토로 확정합니다.</p></details><div class="family-note"><h3>건축주께 드릴 짧은 설명</h3><p>“설계는 많이 정리됐으니, 이제 이 도면을 제대로 구현할 팀을 고르면 됩니다. 아시는 업체도 포함해서 유사 주택 실적, 실제 맡을 소장, 입주 후 하자 대응, 같은 범위 견적 네 가지만 비교해 보겠습니다. 시공사 선정 때문에 설계를 다시 시작하자는 취지는 아닙니다.”</p></div></section>
<section id="sources"><p class="eyebrow">SOURCE REGISTER</p><h2>근거와 남은 확인</h2><p><a href="SEARCH-LOG.md">조사 경로·접근 제한·추가 검증 계획 보기</a></p><p>조사일 2026.09.09 · 명시된 시공 크레딧을 중심으로 확인했습니다. 완공 소개는 시공 참여 증거이며 숨은 하자·재무·이번 현장 품질을 보증하지 않습니다.</p>'''+''.join('<details><summary>'+e(x[0])+'</summary><p>'+e(x[1])+'</p>'+a(x[2],'관련 출처')+'</details>' for x in D['extras'])+'''<div class="notice">주요 후보의 하자·소송 관련 공적 확정 자료는 확보하지 못했습니다. 시스홈의 제3자 기업정보에는 행정처분 표기가 발견돼 공식 원문·대상 법인·현재 효력을 별도 확인해야 합니다. 이를 무하자·무분쟁으로 해석하지 않습니다. 개별 공적 등록·행정처분·재무·보증·고객 확인은 남아 있습니다.</div><details><summary>전체 출처 '''+str(len(sources))+'''개</summary><ol class="sources">'''+''.join('<li>'+a(u,t)+'</li>' for t,u in sources)+'''</ol></details><p>메일에서 선정에 필요한 조건만 요약했습니다. 원문·첨부·사적 연락처·가족 관련 배경은 포함하지 않았습니다.</p></section><section class="history-link"><h2>이전 설계 논의 기록</h2><p>기존 요청·2차 요청·석재 가이드는 이력으로 보존했습니다. 현재 설계 또는 발주 지시로 사용하지 않습니다.</p><a class="button" href="history/archive.html">기존 HTML 기록 보기</a></section></main><footer>JEJU PROPOSAL · 공개자료 검토본 · 2026.09.09</footer><script src="app.js"></script></body></html>'''
for group in ['전체','우선 검토','추가 검증','보류·참고']:
 import re
 count=len(D['candidates']) if group=='전체' else sum(c['group']==group for c in D['candidates'])
 page=re.sub('>'+group+r' \d+</button>', '>'+group+' '+str(count)+'</button>', page)
page=re.sub(r'>\d+개 업체·협업팀', '>'+str(len(D['candidates']))+'개 업체·협업팀', page)
(R/'index.html').write_text(page)
(R/'history/archive.html').write_text('''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>이전 설계 논의 기록</title><link rel="stylesheet" href="../style.css"></head><body><header><a class="brand" href="../index.html">JEJU PROPOSAL</a></header><main><h1>이전 설계 논의 기록</h1><div class="notice">아래 도면과 이미지는 현재 사용하지 않습니다. 과거 논의를 확인하기 위한 이력입니다.</div><ul class="gate-list"><li><a href="index.html">이전 주택 설계 상세 요청사항</a></li><li><a href="2nd.html">건축 설계 2차 요청사항</a></li><li><a href="stone.html">제주 주택 외장 석재 가이드</a></li></ul><a href="../index.html">현재 시공사 검토로 돌아가기</a><p class="small">원본은 Git 이력의 0f29504 커밋에 보존되어 있습니다. 기록 페이지에는 이력 안내와 이미지 경로용 base 요소만 추가했습니다.</p></main></body></html>''')
notes=['# 제주 주택 시공사 검토','','조사일 '+D['checked'],'',D['basis'],'','## 현재 설계','']
notes+=['- **'+r[0]+'**: '+' / '.join(r[1:]) for r in D['requirements']]
for c in D['candidates']:
 notes+=['','## '+c['name']+' — '+c['group'],'',c['reason'],'',c['evidence'],'','미확인: '+c['unknown'],'','질문: '+c['question']]
 notes+=['- ['+p['name']+']('+p['source']+') · '+p['spec']+' · '+p['match'] for p in c['projects']]
notes+=['','## 검증 한계','','DWG 내용 미검증. 공식 개별 등록·행정처분 조회, 재무·보증, 현장방문, 고객 확인, 견적·일정은 미완료. 무분쟁·무하자를 주장하지 않는다. 외부 문의 발송 없음.','','## 출처','']
notes+=['- ['+t+']('+u+')' for t,u in sources]
(R/'RESEARCH.md').write_text('\n'.join(notes)+'\n')
print('Built '+str(len(D['candidates']))+' candidates, '+str(len(sources))+' sources, 3 templates.')

import runpy
runpy.run_path(str(R/"build_review.py"))

runpy.run_path(str(R/"build_portfolio.py"))

runpy.run_path(str(R / "build_responsibility.py"))

runpy.run_path(str(R / "build_ranking.py"))

runpy.run_path(str(R / "build_expanded.py"))
