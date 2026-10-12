# 제주 주택 견적 — 에이전트 작업 지침 R1

## 사용자 지시와 현재 기준

사용자는 건축주/발주자다. 2026-10-12 직접 지시로 **실제 사용은 주택**이며, 사양은 리서치해 우리가 선택하고 시공업체가 동일기준으로 견적하도록 한다. 대외 제목과 난방/급탕/환기·생활설비는 주택 기준으로 쓴다. 원본 행정 기재를 고치거나 허가상 주택으로 승인됐다고 주장하지 않는다. 이 차이를 다시 미확정 질문으로 돌려 견적 준비를 멈추지 않는다.

현재 가격기준은 `data/owner-specifications.json`의 **JEJU-HOUSE-RFQ-20261012-R1**이다. 이전 R0의 사양 미정·용도 확인 전 견적보류를 현행조건으로 되살리지 않는다.

## 읽는 순서

`README.md` → `TENDER.md` → `data/owner-specifications.json` → `data/research-sources.json` → 필요한 도면근거 `data/evidence.json`/`data/source-manifest.json` → `data/tender-response-template.json`.

`OWNER-DECISIONS.md`는 건축주 선택 이유, `contractor/`는 업체에게 공유할 부분이다. 기존 업체조사·순위·내부 전략·과거질의를 업체용 패키지에 섞지 않는다.

## 데이터 규칙

- 기준사양 `SP-ID`, 공통비용항목 기존61개ID, 자재허용액 `ALW-ID`, 옵션 `ALT-ID`, 제조사출처 `RS-ID`를 유지한다.
- 제조사 제품사실·도면전사·발주자 제안/허용액을 구별한다. 13개 허용액은 실제 공급가/시장평균이 아니며 허위 구매가로 설명하지 않는다.
- 기기표 전사값을 R1 고정 가격비교수량으로 채택했지만 실측/적산 승인값으로 승격하지 않는다. 250급환기3대/AP3개소/제습2개소는 명시적 신규 제안이다.
- 7mm LX마루 선택과 도면T10 차이를 명시하고 마감FL 조정비를 포함한다. 50S겸용을50R전용으로 바꾸지 않는다. 큰 창의 안전유리/프레임 크기를 표준 제품에 억지로 맞추지 않는다.
- 구조·부하·풍압·안전·법정 적합성은 건축주 사양 선택과 다르다. 견적은 진행하되 검증 안 된 시공/허가 승인을 주장하지 않는다.
- 원문 근거 hash/handle을 보존한다. 신규 소스 버전은 별도 기록한다. 기존 후보 업체의 평가순위/실적을 이번 사양 선정으로 수정하지 않는다.

## 생성과 검사

`build_tender.py`가 R1 JSON에서 `TENDER.md`, `OWNER-DECISIONS.md`, `SPEC-RESEARCH.md`, 업체용 `contractor/`, ZIP을 생성한다. `build.py`는 기존6개등록부와 전체HTML/진입링크를 생성한다. 두 스크립트는 루트 빌드 명령으로 순서대로 실행되도록 연결돼 있다.

```sh
python procurement/scripts/build.py
python procurement/scripts/validate.py
python procurement/scripts/validate_tender.py
python procurement/scripts/test_validate.py
```

Python Markdown/ezdxf 요구사항은 `procurement/requirements.txt`. 브라우저 점검은 이미 설치된 Chrome/Playwright를 사용하고 로컬 서버를 띄우지 않는다. R1회신 양식은 별도 구조이며 R0의 `validate.py --bid`에 그대로 입력하지 않는다.

## 공개 범위

원본 CAD/전체 추출/작업메모/연락처와 작성된 업체별가격은 `.local/` 등 비공개 경로. 공개할 것은 검토된 원문발췌·사양·발주자의 공통 허용액·빈 회신양식이다. 업체전송/구매/계약체결은 별도 사용자 지시 없이는 하지 않는다.

R0 원본은 `history/R0/`와 Git이력에 남아 있다. 루트/갤러리의 다른 조사·사진을 보존하고 견적사양 진입영역만 변경한다. 루트 AGENTS의 명시적 stage/검토/commit/normal push/원격검증 원칙을 유지한다.
