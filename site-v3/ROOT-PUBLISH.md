# 제주집 시공사 선정 — 인덱스 배포

이번 문구는 특정 세 업체 중 계약하겠다는 뜻이 아니라 평가 순위에 따른 비교를 설명한다.

본문: **현재 평가 순위에 따라 시공사를 비교합니다.**
제목: **제주집 시공사 선정**

기존 평가 점수와 순위·프로젝트 수는 바꾸지 않는다. 반복적인 면책 문구를 다시 넣지 않는다. 기존 사진·도면 이미지 178개를 그대로 사용한다.

`site-v3/ranking-root.cjs`는 기존 갤러리와 문구 생성기를 수정하고, 실제 내용을 담은 루트 `index.html` 및 `public-portfolio.html`을 생성한다. 외부 사이트로 리디렉션하거나 iframe으로 감싸지 않는다. 이미지 경로는 `site-v3/published/assets/`로 명시한다.

`node site-v3/stage-root.cjs`는 루트 인덱스와 검증된 갤러리 파일만 `dist/`에 복사한다. Vercel의 빌드·출력 경로를 이에 맞췄다. 기존 원격 이미지 프록시 함수나 과거 도면 폴더를 배포 출력에 포함하지 않는다.

GitHub Actions `Ranking view and static main page`에서 실제 Chromium의 루트 페이지 제목·문구·필터·사진 확대와 이미지 178개를 검사한 후 결과를 커밋한다. `BASE_URL`로 Vercel 공개 루트도 같은 방식으로 확인할 수 있다. 테스트 결과는 `site-v3/qa/root-report.json`에 남긴다. 실제 Vercel 배포 성공 여부는 배포 결과와 공개 응답으로 별도 확인해야 한다.
