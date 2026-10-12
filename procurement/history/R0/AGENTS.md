# 견적 준비 자료 작업 지침

## 읽는 순서

`README.md` → `data/project.json` → `DRAWING-REVIEW.md` → `data/source-manifest.json` → `data/drawings.json` → `data/rfi.json` → `data/requirements.json` → 필요한 `data/evidence.json` 레코드 → `RFQ.md` / `BID-RETURN.md` / `QUANTITY-PROTOCOL.md`.

## 단일 기준과 증거

- 구조화 데이터의 정본은 `data/*.json`이다. `DRAWING-REGISTER.md`, `RFI.md`, `EQUIPMENT.md`, `SCOPE.md`, `REQUIREMENTS.md`, `EVIDENCE.md` 및 HTML은 `scripts/build.py`로 생성한다. 생성물을 직접 고쳐 정본과 어긋나게 하지 않는다.
- 89개는 도면번호 후보이고 19행은 기기표 전사다. 정식 발행 시트/발주 수량으로 승격하지 않는다. 확인되지 않은 값은 null이며 0과 다르다.
- 기존 주택 계획과 새 도면의 사무소 표기를 분리한다. 임의로 ‘실제로는 주택이므로’ 덮어쓰거나 위법으로 단정하지 않는다.
- 출처 파일 해시·객체handle·위치·원문 발췌를 유지한다. 신규 파일을 받으면 신규 소스/버전을 만들고 이전 근거를 조용히 덮어쓰지 않는다.
- 질문은 `RFI-ID`, 과거 요구는 `REQ-ID`, 견적행은 공통항목ID, 추가통보는 `ADD-ID`로 연결한다. 승인 없는 답변은 종결 처리하지 않는다.
- 기타 저장소의 오래된 면적/지붕/구조/가격 가정을 최신 근거로 가져오지 않는다. 현재 메인 업체와 순위·과거 실사 기록은 이 업데이트로 변경하지 않는다.

## 공개/비공개 경계

원본 DWG/DXF/PDF 전체, 전체 텍스트, 연락처·서명·인증정보, 내부 협의 메모, 작성된 업체별 견적·가격·조건은 기본적으로 공개 금지다. `.local/` 같은 gitignored 경로에 두고 공개 문서에는 검토된 발췌/빈 양식만 둔다. 원본에 외부 공유 제한이 표시된 작업 내용을 공개 발췌로 전사하지 않는다.

비공개 파일을 보내 달라는 이유로 비공개 저장소 새로 만들기/업체 전송/권한 변경을 자동으로 하지 않는다. 사용자 승인과 도서 배포 권한을 확인한다.

## 변경과 검증

`python scripts/build.py`로 생성하고 `python scripts/validate.py`를 통과시킨다. 공식 도면을 검증한 것과 데이터/링크 검사 통과를 구별한다. 렌더링과 브라우저 검사를 수행하지 않았으면 해당 상태를 그대로 남긴다.

루트 `index.html`과 `site-v3/published/index.html`은 원래 갤러리를 보존하고 견적 준비 링크만 추가한다. 갤러리를 재생성한 경우 `scripts/build.py`를 다시 실행해 링크를 복구한다. 기존 루트 AGENTS의 검토 후 명시적 stage/commit/push 원칙을 따른다. 기존 분석/갤러리 전체를 대체하거나 무관한 자동화·서버를 실행하지 않는다.
