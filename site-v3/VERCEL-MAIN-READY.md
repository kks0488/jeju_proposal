# 제주집 시공사 선정 — Vercel 메인 반영 완료

공개 메인: https://jeju-proposal.vercel.app/

제목은 `제주집 시공사 선정`으로 유지했다. `하백·이아 / GAU / 다봄 중에서 선정합니다`와 `우리 집을 지을 세 업체`라는 확정적인 표현을 제거하고, **현재 평가 순위에 따라 시공사를 비교합니다.**로 바꿨다. 소개 문장은 `평가 순위와 실제 시공 사례를 바탕으로 제주집에 맞는 시공사를 비교합니다.`이다. 기존 점수·순위는 변경하지 않았다.

루트 `index.html`에 갤러리의 실제 내용을 넣고 이미지·스타일·스크립트 경로를 맞췄다. GitHub Pages로 이동시키는 리디렉션이나 iframe이 아니다. Vercel 메인 주소 `/`에서 바로 열린다. 17개 프로젝트·178개 이미지와 필터·검색·확대 기능을 유지했다. 정적 파일만 배포하므로 이미지 표시를 위한 방문 시점의 외부 원본 요청이나 서버 이미지 변환이 없다.

## 배포

- Vercel 프로젝트: jeju-proposal / prj_ADMxQWvg3gvb9HsBFxOYvcOcdF6n
- 프로덕션 배포: dpl_BvbozoLegWMjPCdJv4dY8c2ypPbg
- 상태: READY / aliasError null
- 연결 주소: jeju-proposal.vercel.app
- 배포 소스: ab020b5a5624719e6c44426a02b9f5446da83da4의 저장 이미지와 인덱스 생성기
- 배포 출력: dist / index.html / site-v3/published/assets

## 실제 메인 브라우저 확인

검사 시각: 2026-09-15T10:44:22.273Z.
GitHub Actions run 34959475094 / job 104349367131 성공.
결과 artifact: vercel-main-live-check / 10392428405.

로그인 쿠키가 없는 별도 Chromium 세션으로 **https://jeju-proposal.vercel.app/**에 직접 접속했다. 1440px·390px 모두 HTTP 200, 제목 일치, 주소 경로 `/` 유지, 확정적인 선정 문구 없음, 필터·검색·사진 확대와 다음 사진 동작 정상. 각 화면에서 이미지 178개가 모두 실제 디코딩됐고, 깨진 이미지 0개·JavaScript 오류 0개였다. 모든 이미지가 같은 Vercel 도메인의 정적 파일이다. 두 화면 스크린샷도 확인했다.

별도 하위 GitHub 갤러리 주소는 호환용으로 남겨두되, 사용자에게 안내할 메인은 위 Vercel 주소다. 이번 성공은 프로덕션 메인 배포와 공개 접속 확인을 의미하며 네이티브 Git 자동 배포 연동을 새로 설정했다는 뜻은 아니다.
