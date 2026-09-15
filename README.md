# 제주 주택 시공사 비교 — 하백 · GAU · 다봄

## 최신 공개 갤러리

**[새 정적 갤러리](https://kks0488.github.io/jeju_proposal/site-v3/published/)**

사용자 요청에 따라 아틀리에는 메인 비교에서 제외했다. 현재 확보한 아틀리에의 제주 협동조합·서울 공동체 주택 사례는 이번 개별 단독주택과 조건이 달라 비교 우선순위에서 뺀 것이다. 업체가 단독주택을 시공할 능력이 없다는 판정이 아니다. 기존 ranking.json과 과거 검토는 그대로 보존했다.

| 메인 비교 | 프로젝트 | 저장 이미지 |
|---|---:|---:|
| 하백·이아컴퍼니 | 6 | 74 |
| GAU | 6 | 48 |
| 다봄·다봄주택 | 5 | 56 |
| 합계 | 17 | 178 |

이미지는 사진·원문 도면을 포함한 수다. 16개 프로젝트의 갤러리를 제공한다. 오라동 현이네 한 건은 원문 접근 제한(HTTP 403) 때문에 사진을 확보하지 못해 출처만 남겼다. 동일 여부가 확인되지 않은 다른 오라동 주택 사진을 가져다 붙이지 않았다.

## 사진 표시 문제 해결 방식

기존 v2는 방문 시마다 외부 사이트에서 사진을 가져와 서버에서 변환했다. 새 v3는 최적화한 **실제 이미지 파일을 저장소 `site-v3/published/assets/`에 저장**하고 페이지와 함께 제공한다. 새 페이지에는 외부 이미지 요청·런타임 이미지 프록시·요청 시 sharp 변환이 없다. 작은 썸네일과 1600px 이내 원본 비율 확대 이미지를 별도로 제공한다.

공식 갤러리의 초기 노출 사진뿐 아니라 공개된 나머지 갤러리 항목도 읽었다. 새로 확보한 어흥어음 14개, 영평동 8개 이미지를 포함한다. 영평동은 공식 개요에 단독주택과 근린생활시설이 함께 기재되어 복합 용도로 구분했다. 다봄의 목조·복합구조를 RC 본체 실적으로 합산하지 않았으며 기존 소원재 공정·보수 확인 사항도 유지했다.

## 실제 검사

GitHub Actions run 34947818047 성공, 이미지·페이지 저장 커밋 `36487a1373140e6a357f4300f9656142cafc58fc`.

실제 Chromium에서 1440×1000, 768×1024, 390×844, 320×700 화면을 열어 업체 필터·RC 필터·검색·빈 결과·사진 확대·다음 사진·Escape·프로젝트 직접 링크를 검사했다. 요청을 모의하지 않은 정적 서버 검사다. 저장된 확대 이미지 **178개 모두 Image.decode() 성공**, 깨진 이미지 0개, JavaScript 예외 0개, 가로 넘침 0개였다. 실제 iPhone Safari 검사로 확대 해석하지 않는다.

[브라우저 검사 원본](site-v3/qa/browser-report.json) · [사진별 출처와 실패 기록](site-v3/published/image-manifest.json) · [정적 데이터](site-v3/published/catalog.json)

## 공개 배포 상태

새 갤러리 파일과 이미지는 GitHub에 커밋했다. 기존 GitHub Pages 공개 배포 경로로 연결한다. 이번 Vercel 재배포 요청은 연결 도구의 보안 확인 단계에서 차단되어 **Vercel 새 버전 배포를 완료했다고 기록하지 않는다**. 기존 `jeju-proposal.vercel.app`는 이전 버전일 수 있다. 그 주소의 최근 이미지 HTTP 검사가 새 정적 버전의 배포 성공을 뜻하지 않는다.

Vercel로 재배포할 때에는 `site-v3/published` 폴더만 정적 출력으로 사용하면 된다. 파일과 사진은 모두 준비되어 있으며 원본 사이트를 재수집할 필요가 없다. 네이티브 Git Integration의 연결을 완료한 것은 아니다.

## 파일 구조

- `site-v3/template.html`, `style.css`, `app.js`: 새 반응형 화면·갤러리
- `site-v3/build.mjs`: 원문 이미지 수집·크기 최적화·정적 파일 생성
- `site-v3/browser-test.mjs`: 실제 Chromium 검사
- `site-v3/published/`: 검증된 HTML·CSS·JS·데이터·이미지 파일
- `site-v3/qa/browser-report.json`: 재현 가능한 검사 결과
- `.github/workflows/portfolio-refresh.yml`: 생성 후 검사 성공 시에만 생성 파일을 커밋

`site-v3`의 소스 파일 변경 시 이미지 재수집·브라우저 검사가 실행된다. 3개 업체의 모든 보유 실적이나 모든 비공개 포트폴리오를 확보했다는 뜻이 아니며, 현재 확인한 프로젝트별 공개 이미지 범위다. 사진 권리·설계·조경·가구 제작 기여를 구분한다. 업체 현장 실사·견적·계약·보증 검증은 별도다.

## 기존 자료 보존

[RANKING.md](RANKING.md) · [DUE-DILIGENCE.md](DUE-DILIGENCE.md) · [EXPANDED-REVIEW.md](EXPANDED-REVIEW.md) · [FOLIO-AUDIT.md](FOLIO-AUDIT.md) · [이전 README](history/README-before-static-v3.md)
