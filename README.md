# Jeju Proposal — 제주 주택 시공사 검토

현재 목적은 **기존 설계를 유지한 제주 주택 시공사 선정 준비**입니다. 과거 HTML의 도면·공간 구성은 현재 설계가 아닙니다.

- `ranking.html` / `RANKING.md`: 13개 후보의 공통 채점·항목별 근거·가중치 민감도
- `ranking.json` / `build_ranking.py`: 채점 단계·배점·생성기
- `DUE-DILIGENCE.md` / `review.html#responsibility`: 11개 현장의 도급범위·반복 협력사·변경된 판단
- `responsibility-review.json` / `build_responsibility.py`: 상세 원문 검증 데이터·기존 검토 페이지 통합 생성기
- `portfolio.html` / `PORTFOLIO-REVIEW.md`: 다른 9개 후보의 실제 시공 포트폴리오·근거 수준·혼동 방지
- `portfolio-review.json` / `build_portfolio.py`: 포트폴리오 검증 데이터·생성기
- `index.html`: 13개 업체·협업팀, 설계 조건, 검증 질문, 견적 준비
- `review.html` / `DETAIL-REVIEW.md`: 업체의 가치·조직·결과물 사진·성능 기록을 연결한 3차 판단 (호미·솔비나무집·인증번호·공정 사진 추가)
- `detail-review.json` / `build_review.py`: 정밀 검토 데이터와 생성기
- `research.json`: 출처와 연결된 실적·판단·미확인 항목
- `RESEARCH.md`: 조사 기록 및 출처
- `SEARCH-LOG.md`: 조사 경로·접근 한계·6곳의 자료 요청 우선순위
- `templates/`: 공종별 견적 비교표, 평가표, 발송 전 문의 문안
- `history/archive.html`: 이전 HTML 기록의 진입점
- `history/index.html`, `history/2nd.html`, `history/stone.html`: 기존 문서 보존본
- `images/`: 과거 자료 이미지. 현재 도면으로 사용하지 않음

- `EXPANDED-REVIEW.md` / `review.html#expanded`: 2026-09-14 신규 4곳의 추가 검증·조직·구조·표기 충돌
- `expanded-review.json` / `build_expanded.py`: 추가 조사 데이터와 기존 검토 페이지 통합 생성기

## 2026-09-15 폴리오 재검토와 공정 평가

[FOLIO-AUDIT.md](FOLIO-AUDIT.md) / [folio-audit.html](folio-audit.html): 기존 13개 후보와 대오의 폴리오 확인 범위, 상세 현장 검증, 미확인 자료 및 계약 평가 기준. 검증된 사전 기여는 100점 안에서 최대 3점이며 자동 가점이 아닙니다. 기존 공개자료 순위와 최종 계약 평가는 별도입니다. 생성기는 `build_folio_audit.py`입니다.

## 조사 상태

2026-09-09 기본 조사에 2026-09-14 추가 조사를 반영했습니다. 아틀리에건설을 13번째 채점 후보로 추가하고, 돌담하우스·레아하우징·포스트제주는 관찰 후보로 별도 기록했습니다. 기존 12개 업체의 점수는 유지하며 모든 업체의 현재 상태를 새로 실사한 것은 아닙니다. 최신 설계 근거는 2026-09-08 수정도면 송부와 후속 메일입니다. DWG 내부는 직접 검증하지 않았습니다. 정확한 면적·치수·구조는 최신 PDF 도서로 재확인해야 합니다.
‘우선 검토’는 자료 확인 우선순위이며 계약 적격·품질 보증이 아닙니다. 견적, 현장방문, 고객 확인, 공적 등록·행정처분·재무·보증 확인은 미완료입니다. 업체에 문의하거나 도면을 전달하지 않았습니다.

## 수정·열기

`research.json`과 `build.py`를 수정한 뒤 `python build.py`를 실행합니다. 정적 HTML이라 `index.html`을 열면 됩니다. 설치는 필요 없습니다. 외부 이미지는 인터넷 연결이 필요합니다.

기존 원본은 Git 커밋 `0f29504a5fcdbecdaae698844af4e05e9438fe2d`에 그대로 남아 있습니다. 보존본에는 현재 미사용 안내와 이미지 경로용 base 요소만 추가했습니다. 루트 `2nd.html`, `stone.html`은 기존 링크 호환을 위해 보존본으로 연결합니다.

메일 원문·첨부·사적 연락처·가족 배경은 공개 저장소에 복사하지 않았습니다. 상세 근거는 페이지의 출처·한계에서 확인하십시오.

## 2026-09-15 추가 검증

[심층 조사](EXPANDED-REVIEW.md): 다봄 RC 2건·반복 협업과 소원재 6년차 거주자의 공정 불만을 함께 반영했습니다. GAU 항심당·월정리 RC 실적과 A/S 약속의 구체성도 대조했습니다. [채점표](RANKING.md)의 다봄은 32→57점으로 수정하되 현재 법인 연결과 보수 경위 확인 전 조건부입니다.

## 세 업체 준공 사진집

[contractor-gallery.html](contractor-gallery.html) — 하백·이아컴퍼니 2개, GAU 3개, 다봄 5개 대표 프로젝트 / 사진 26장. 원문 출처와 설계자·사진가를 표시하고 구조를 구분했습니다. 사진은 파일에 포함되어 별도 다운로드 없이 열리며, 원문 링크에는 인터넷 연결이 필요합니다. 다봄 전화번호는 사용자가 제공한 연락처입니다.
