# Jeju Proposal — 제주 주택 시공사 검토

현재 목적은 **기존 설계를 유지한 제주 주택 시공사 선정 준비**입니다. 과거 HTML의 도면·공간 구성은 현재 설계가 아닙니다.

- `portfolio.html` / `PORTFOLIO-REVIEW.md`: 다른 9개 후보의 실제 시공 포트폴리오·근거 수준·혼동 방지
- `portfolio-review.json` / `build_portfolio.py`: 포트폴리오 검증 데이터·생성기
- `index.html`: 12개 업체·협업팀, 설계 조건, 검증 질문, 견적 준비
- `review.html` / `DETAIL-REVIEW.md`: 업체의 가치·조직·결과물 사진·성능 기록을 연결한 3차 판단 (호미·솔비나무집·인증번호·공정 사진 추가)
- `detail-review.json` / `build_review.py`: 정밀 검토 데이터와 생성기
- `research.json`: 출처와 연결된 실적·판단·미확인 항목
- `RESEARCH.md`: 조사 기록 및 출처
- `SEARCH-LOG.md`: 조사 경로·접근 한계·6곳의 자료 요청 우선순위
- `templates/`: 공종별 견적 비교표, 평가표, 발송 전 문의 문안
- `history/archive.html`: 이전 HTML 기록의 진입점
- `history/index.html`, `history/2nd.html`, `history/stone.html`: 기존 문서 보존본
- `images/`: 과거 자료 이미지. 현재 도면으로 사용하지 않음

## 조사 상태

2026-09-09 공개자료 조사. 최신 설계 근거는 2026-09-08 수정도면 송부와 후속 메일입니다. DWG 내부는 직접 검증하지 않았습니다. 정확한 면적·치수·구조는 최신 PDF 도서로 재확인해야 합니다.
‘우선 검토’는 자료 확인 우선순위이며 계약 적격·품질 보증이 아닙니다. 견적, 현장방문, 고객 확인, 공적 등록·행정처분·재무·보증 확인은 미완료입니다. 업체에 문의하거나 도면을 전달하지 않았습니다.

## 수정·열기

`research.json`과 `build.py`를 수정한 뒤 `python build.py`를 실행합니다. 정적 HTML이라 `index.html`을 열면 됩니다. 설치는 필요 없습니다. 외부 이미지는 인터넷 연결이 필요합니다.

기존 원본은 Git 커밋 `0f29504a5fcdbecdaae698844af4e05e9438fe2d`에 그대로 남아 있습니다. 보존본에는 현재 미사용 안내와 이미지 경로용 base 요소만 추가했습니다. 루트 `2nd.html`, `stone.html`은 기존 링크 호환을 위해 보존본으로 연결합니다.

메일 원문·첨부·사적 연락처·가족 배경은 공개 저장소에 복사하지 않았습니다. 상세 근거는 페이지의 출처·한계에서 확인하십시오.
