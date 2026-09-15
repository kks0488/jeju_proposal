# 제주 주택 시공사 비교

**[공개 포트폴리오](https://jeju-proposal.vercel.app/)** · **[다봄 바로 보기](https://jeju-proposal.vercel.app/?company=dabom#portfolio)**

## 2026-09-15 다봄 추가 및 사진 확대

주요 비교: **하백·이아 / GAU / 다봄**. 추가 비교: **아틀리에**. 앞선 대화의 주요 세 업체와 점수순 상위 세 업체를 혼동했던 구성을 바로잡았다. 아틀리에를 삭제하거나 기존 점수를 변경하지 않았다.

| 화면 배치 | 업체 | 기존 점수순 | 프로젝트 | 페이지 내 사진 |
|---|---|---|---:|---:|
| 주요 비교 | 하백·이아 | 공동 1위 · 78점 | 6 | 11 |
| 주요 비교 | GAU | 공동 1위 · 78점 | 6 | 10 |
| 주요 비교 | 다봄 | 4위 · 57점 | 5 | 14 |
| 추가 비교 | 아틀리에 | 3위 · 60점 | 3 | 5 |

총 **20개 프로젝트·40장**. 17개 프로젝트에 사진을 표시하고, 미확보 3개(어흥·어음, 영평동, 오라동 현이네)는 임의 이미지를 넣지 않았다. 업체별 필터·검색·RC 필터·카드 썸네일·확대 사진 선택·좌우 넘김·휴대전화 스와이프·공유·비교표·인쇄를 제공한다. 사진가·출처·시공 역할과 미확인 내용을 함께 표시한다.

다봄: 저지 오름 아래 3장 / 용담 심양재 2장 / 해안동 3장 / 소원재 3장 / 제주 작은 집 3장. RC 본체는 저지·용담 2건이다. 해안동 복합구조·목조 2건을 RC 본체 실적에 합산하지 않는다. 현재 계약 법인·소장·보증 연결 및 소원재 보수 경위 확인 전 조건부라는 판단을 유지한다.

## 편집·배포 구조

- `portfolio-data.json` + `portfolio-expansion.json`: 기존 15개 기초 자료와 추가 5개·사진 보강. 공개 `/portfolio-data.json`은 병합된 20개 자료다.
- `public-portfolio.html` + `portfolio-enhancements.js`: 기존 반응형 템플릿과 새 썸네일·네 업체 비교 동작.
- `lib/portfolio-v2-core.mjs`: 원본과 추가 자료 병합, 현재 ranking.json을 읽어 점수 보존, HTML 보완.
- `api/public-site.mjs`: 공개 진입점·이미지 최적화·상태 점검. 큰 외부 사진은 비율을 유지해 최대 1600px WebP로 변환한다.
- `lib/legacy-site.mjs`: 기존 게이트웨이 동일 코드 보존. 기존 보고서·26장 내장 사진집 제공과 사적 연락처 제외.
- `scripts/prepare-deploy.mjs`: 보존 코드 SHA·20개 프로젝트·40장·다봄 RC 2건·스크립트 문법 및 결합 점검. `npm install`, `npm test`로 재현한다.

사진을 볼 때 출처 사이트를 열 필요 없이 같은 도메인의 이미지 응답을 사용한다. 기존 26장은 저장소 내장 사진집에서 가져오며 새 외부 사진은 허용 출처를 읽어 캐시한다. 외부 사이트 장애가 영향을 줄 수 있고 영구 보존이나 사진 이용허락 확보를 뜻하지 않는다.

기존 GitHub master 원본 연결은 유지한다. HTML·expansion·enhancements·채점 자료는 캐시 갱신 후 반영한다. 서버 함수·의존성·배포 설정 변경은 재배포가 필요하다. Vercel 네이티브 Git 자동 빌드 연동을 완료한 것은 아니다. `public/`만 정적 출력 폴더로 사용하고 과거 도면 폴더는 공개 경로에 포함하지 않는다.

## 기존 검토 자료

- [순위·채점 기준](RANKING.md) / [전체 채점표](https://jeju-proposal.vercel.app/ranking.html)
- [이번 변경·원문 근거](PORTFOLIO-V2.md)
- [정밀 검토](DETAIL-REVIEW.md) / [도급범위](DUE-DILIGENCE.md)
- [추가 시공사 조사](EXPANDED-REVIEW.md) / [폴리오 감사](FOLIO-AUDIT.md)
- [다른 후보 포트폴리오](PORTFOLIO-REVIEW.md) / [기초 조사](RESEARCH.md) / [검색 이력](SEARCH-LOG.md)
- [기존 메인 보존본](https://jeju-proposal.vercel.app/overview.html) / [기존 26장 사진집](https://jeju-proposal.vercel.app/contractor-gallery.html)
- [이전 README 전체 보존](history/README-before-gallery-v2.md)
- [이전 배포 점검 기록](PUBLIC-VERIFICATION.md): 15개·12장 기록은 이전 버전이며 현재 20개·40장과 구분한다.

현장방문·현재 공적 등록·재무·보증·원본 시험 및 하자 처리대장 검증은 완료되지 않았다. 업체에 연락하거나 도면을 전달하지 않았다. 이번 변경은 포트폴리오 정리와 공개 화면 보완이며 계약 추천 확정이 아니다.
