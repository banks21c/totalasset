# GitHub Pages 정적 사이트 빌드 — 설계

날짜: 2026-07-27
대상 저장소: https://github.com/banks21c/totalasset

## 배경

이 프로젝트는 Flask 앱이다. 지금 구조로는 저장소를 그대로 GitHub Pages에 올려도
사이트가 동작하지 않는다. 네 가지가 걸린다.

1. 허브(`/`)는 파일이 아니라 `hub.render()`가 파이썬으로 만들어 내는 HTML이다.
   저장소에 `index.html`이 존재하지 않는다.
2. 공통 네비게이션 바는 `nav.inject()`가 서빙 시점에 `<body>` 뒤로 끼워 넣는다.
   `pages/` 아래 HTML 파일 자체에는 네비가 없다.
3. 링크가 전부 루트 기준 절대경로(`href="/bond"`)다. 프로젝트 Pages는
   `banks21c.github.io/totalasset/` 아래에 놓이므로 전부 404가 된다.
4. 상담신청 폼은 `POST /api/consult/`와 SQLite를 쓴다. 정적 호스팅에서는 동작하지 않는다.

## 목표

사이트 전체(허브 + 12개 본문 페이지)를 GitHub Pages에서 동작하게 만든다.
Flask 앱은 그대로 유지한다. 로컬에서는 지금처럼 `python app.py`로 띄우고,
GitHub Pages에는 정적으로 구운 결과물을 올린다.

## 비목표

- Flask 앱 제거
- 정적 사이트에서 상담신청 접수 (백엔드가 필요하다)
- GitHub Actions 자동 배포 — 나중에 워크플로 파일 하나로 얹을 수 있으므로 지금은 하지 않는다

## 설계

### 출력 위치

빌드 결과는 `docs/`에 쓴다. GitHub Pages 설정에서 *Deploy from branch → master / docs*
하나만 고르면 되고, 별도 `gh-pages` 브랜치를 관리할 필요가 없다.
`docs/.nojekyll`을 함께 써서 Jekyll 처리를 건너뛴다.

이 설계 문서를 포함한 스펙은 `specs/`(저장소 루트)에 둔다. `docs/`가 Pages 루트가 되므로
그 아래 두면 스펙 문서까지 웹에 공개된다.

### 빌드 방식 — 라우트를 중복 선언하지 않는다

`build_static.py`가 Flask 앱의 `url_map`을 읽고 test client로 각 경로를 요청한다.

```
app.url_map → 인자 없는 GET 규칙만 추출 (/api/, /admin/, /static/ 제외)
  → client.get(route) → 네비 주입까지 끝난 완성 HTML
  → 상담 섹션 제거 → 링크 상대경로 변환
  → docs/<route>/index.html 로 저장
```

라우트 목록을 빌드 스크립트에 다시 적지 않는 것이 핵심이다. `app.py`에 라우트를
추가하면 정적 빌드에 자동으로 포함되고, `nav.py`와 `hub.py`가 계속 메뉴의 유일한
정의로 남는다. 이 중복 제거가 이 접근을 고른 이유다.

응답이 200이 아니면 빌드를 중단한다. 깨진 페이지를 조용히 배포하지 않는다.

### 경로 매핑

| 라우트 | 출력 파일 | 깊이 |
|---|---|---|
| `/` | `docs/index.html` | 0 |
| `/bond` | `docs/bond/index.html` | 1 |
| `/insurance/damage` | `docs/insurance/damage/index.html` | 2 |

깊이는 상대경로의 `../` 개수가 된다.

### 링크 변환

`href`/`src`의 루트 기준 경로를 현재 페이지 기준 상대경로로 바꾼다.
깊이 2인 페이지에서 `href="/bond"` → `href="../../bond/index.html"`.

건드리지 않는 것: `http://`, `https://`, `//cdn...`(프로토콜 상대), `#앵커`,
`mailto:`. 확장자가 있는 대상(`/static/app.css`)은 `index.html`을 붙이지 않는다.
`#` 뒤 프래그먼트는 잘라 두었다가 변환 후 다시 붙인다.

절대경로 대신 상대경로를 쓰는 이유는 저장소 이름이 바뀌거나 커스텀 도메인을
붙여도 깨지지 않고, `docs/index.html`을 브라우저로 직접 열어 확인할 수도 있기
때문이다. 같은 이유로 디렉터리 링크(`bond/`) 대신 `index.html`을 명시한다 —
`file://`로 열었을 때 디렉터리 인덱스가 동작하지 않는다.

### 상담 폼 제거

상담 폼이 들어가는 세 페이지(`savings_pension`, `irp`, `isa`)에서 마커 하나만
건너뛰면 "전문가 상담 신청" 제목이 붙은 빈 `<section>`이 남는다
(`pages/irp/index.html:394-402`). 그래서 섹션 전체를 마커 쌍으로 감싼다.

```html
<!-- ta:consult-section:start -->
<section> … 전문가 상담 신청 … </section>
<!-- ta:consult-section:end -->
```

Flask로 서빙할 때는 HTML 주석이라 아무 영향이 없다. 정적 빌드에서는 두 마커
사이를 통째로 걷어낸다. 이 방식이라 `app.py`에 빌드 전용 분기를 넣지 않아도 된다.

### 테스트 (`test_build.py` 신규)

임시 디렉터리에 빌드한 뒤 검증한다.

- 앱의 모든 정적 대상 라우트가 파일로 나왔는가
- **모든 페이지의 모든 내부 링크가 실제 존재하는 파일을 가리키는가** (가장 중요)
- 절대경로 `href="/…"`가 하나도 남지 않았는가
- 네비 바가 모든 페이지에 들어 있는가
- 상담 폼과 "전문가 상담 신청" 문구가 정적 결과물에 없는가
- 허브의 7개 카드 링크가 모두 살아 있는가

기존 `test_app.py`도 계속 통과해야 한다. Flask 서빙 동작은 바뀌지 않는다.

## 구현 중 발견한 것

링크 검증 테스트가 **원래부터 깨져 있던 링크 두 종류**를 잡아냈다. 둘 다 Flask에서도
404였다. 정적 빌드가 만든 문제가 아니라 드러낸 문제다.

1. **파비콘 4개** (`/static/articles/favicon.ico` 등) — `bond`, `irp`, `isa` 페이지의
   `<head>`에 있었으나 `static/` 디렉터리 자체가 존재하지 않는다. 다른 프로젝트에서
   복사해 온 흔적으로 보인다. 죽은 `<link>` 태그를 제거했다.
2. **`/privacy-policy/`** — `irp`, `isa` 하단 쿠키 동의 배너의 "자세히 보기" 링크가
   없는 페이지를 가리켰다. 상담 폼으로 이름·연락처를 받고 쿠키 배너까지 있는 사이트라
   방침 페이지를 만드는 쪽으로 정했다. `pages/privacy_policy/index.html`과
   `GET /privacy-policy` 라우트를 추가하고, 두 링크의 후행 슬래시를 떼어
   라우트와 맞췄다(Flask는 `/privacy-policy/`를 `/privacy-policy` 규칙으로 받지 않는다).

방침 문서의 내용은 초안이다. 보유 기간(1년) 등 실제 운영 정책과 다른 부분은
사용자가 검토해 고쳐야 한다.

## 변경되는 파일

| 파일 | 변경 |
|---|---|
| `build_static.py` | 신규 — 빌드 스크립트 |
| `test_build.py` | 신규 — 빌드 검증 |
| `pages/savings_pension/index.html` | 상담 섹션에 마커 쌍 추가 |
| `pages/irp/index.html` | 상담 섹션에 마커 쌍 추가 |
| `pages/isa/index.html` | 상담 섹션에 마커 쌍 추가 |
| `pages/privacy_policy/index.html` | 신규 — 개인정보처리방침 |
| `pages/bond/index.html` | 죽은 파비콘 `<link>` 제거 |
| `app.py` | `GET /privacy-policy` 라우트 추가 |
| `test_app.py` | `/privacy-policy`를 페이지 목록에 추가 |
| `docs/` | 신규 — 빌드 산출물 (커밋한다) |
| `specs/` | 신규 — 이 문서 |
| `nav.py`, `hub.py`, `consult*.py` | 변경 없음 |

## 배포 절차

```bash
python build_static.py     # docs/ 재생성
git add docs && git commit && git push
```

GitHub 저장소 Settings → Pages → Source: *Deploy from a branch* →
Branch: `master`, 폴더: `/docs`.

공개 주소: https://banks21c.github.io/totalasset/
