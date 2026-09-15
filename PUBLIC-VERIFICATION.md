# 공개 배포 검증 — 2026-09-15

공개 주소: https://jeju-proposal.vercel.app/
프로젝트: `jeju-proposal` / `prj_ADMxQWvg3gvb9HsBFxOYvcOcdF6n`
최종 확인한 배포: `dpl_6baEFoZa7rGwgtv1Dz2Tsr2FtVnM` — production / READY / aliasError null.

## 실제 HTTP 점검

2026-09-15 07:37:23 UTC(한국시간 16:37) 응답 기준 `/health?links=1&images=1`에서 아래를 확인했다.

- `ok: true`, `mode: github-origin`, repository `kks0488/jeju_proposal`, branch `master`.
- 15개 프로젝트·12개 대표 사진. 12개 사진 모두 정상 이미지 MIME 및 응답 확인(`assetsOk: true`).
- 쿠키, Authorization, Vercel 보호 우회 헤더 없이 별도로 요청한 11개 경로가 모두 HTTP 200(`anonymousAccessOk: true`). 일반 공개 주소를 Node fetch로 요청했으며 로그인 세션을 전달하지 않았다.

확인한 경로: `/`, `/portfolio-data.json`, `/ranking.html`, `/review.html`, `/portfolio.html`, `/folio-audit.html`, `/contractor-gallery.html`, `/overview.html`, `/style.css`, `/app.js`, `/gallery-photo?index=0`.

큰 기존 사진집은 HTML 약 27KB와 이미지별 응답으로 분리해 제공된다. 원본 파일과 26장 사진은 보존한다. 임의 경로 및 사적 휴대전화 연결은 공개 전달본에서 제외했다.

## 화면·기능 점검

1440×1000, 768×1024, 390×844, 320×700의 격리 Chromium 문서 검사에서 가로 넘침 및 JavaScript 예외 없음. 업체 필터(6/6/3), RC 필터에서 눈뫼가름 제외, 검색·빈 결과·초기화, 상세 모달, 사진 다음/이전, Escape·닫기 동작을 확인했다.

격리 환경에서는 네트워크와 history를 모의한 문서 검사를 수행했다. 따라서 실제 iPhone Safari 또는 실배포 전체 화면의 브라우저 종단간 테스트를 했다는 뜻은 아니다. 외부 사진의 접근성과 로그인 없는 HTTP 응답은 위 실제 배포 점검으로 별도 확인했다.

실행: `node tests/check.mjs`. 선택적 브라우저 검사에는 Python Playwright 및 Chromium이 필요하며 `python tests/browser-check.py`로 실행한다. 결과는 `test-results/`에 저장한다. 기본 검사에는 외부 패키지가 필요 없다.

## 연결 방식

현재는 Vercel이 GitHub master의 허용된 공개 파일을 읽는 구성이다. 페이지·포트폴리오 데이터 수정은 master 커밋 후 캐시 갱신에 따라 반영된다. 함수 코드와 vercel.json은 재배포해야 한다. Vercel 네이티브 Git Integration/커밋별 자동 빌드 연결을 완료했다고 주장하지 않는다. 자세한 구성 및 한계는 DEPLOYMENT.md를 참조한다.
