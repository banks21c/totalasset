"""Flask 앱을 GitHub Pages용 정적 사이트로 굽는다. `python build_static.py`로 실행한다.

라우트 목록을 여기에 다시 적지 않는다. 앱의 `url_map`을 읽어 test client로 각 경로를
요청하므로, `app.py`에 라우트를 추가하면 정적 빌드에도 자동으로 따라 들어온다.
네비 바와 허브 카드 역시 `nav.py`·`hub.py`가 계속 유일한 정의로 남는다.

정적 호스팅에서 못 하는 두 가지는 굽는 과정에서 덜어낸다.
  - 백엔드가 필요한 경로(`/api/`, `/admin/`)는 아예 대상에서 뺀다.
  - 상담신청 섹션은 마커 쌍 사이를 통째로 걷어낸다.

링크는 루트 기준(`/bond`)에서 현재 페이지 기준 상대경로로 바꾼다. 프로젝트 Pages가
`banks21c.github.io/totalasset/` 아래에 놓이기 때문이고, 상대경로라 저장소 이름이
바뀌거나 커스텀 도메인을 붙여도 깨지지 않는다.
"""
import re
import shutil
from pathlib import Path

import app as application

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "docs"

# 백엔드가 있어야 동작하는 경로. 정적 사이트에는 담지 않는다.
EXCLUDED_PREFIXES = ("/api/", "/admin/", "/static/")

CONSULT_SECTION_RE = re.compile(
    r"[ \t]*<!--\s*ta:consult-section:start\s*-->.*?"
    r"<!--\s*ta:consult-section:end\s*-->[ \t]*\n?",
    re.DOTALL,
)

# href="/..." · src="/..." 처럼 루트 기준 경로.
# `//cdn.example.com` 같은 프로토콜 상대 URL은 두 번째 `/`로 걸러 낸다.
ROOT_LINK_RE = re.compile(r'\b(href|src)="/(?!/)([^"]*)"')


def routes():
    """정적으로 구울 수 있는 GET 라우트를 앱에서 그대로 뽑는다."""
    found = []
    for rule in application.app.url_map.iter_rules():
        if rule.arguments:  # `<id>` 같은 동적 구간이 있으면 구울 수 없다
            continue
        if "GET" not in rule.methods:
            continue
        if rule.rule.startswith(EXCLUDED_PREFIXES):
            continue
        found.append(rule.rule)
    return sorted(found)


def depth(route):
    """루트에서 몇 단계 내려간 페이지인지. 상대경로 `../` 개수가 된다."""
    return 0 if route == "/" else len(route.strip("/").split("/"))


def output_path(route, out_dir=OUT_DIR):
    """`/insurance/damage` → `<out_dir>/insurance/damage/index.html`"""
    if route == "/":
        return out_dir / "index.html"
    return out_dir / route.strip("/") / "index.html"


def _target_file(target):
    """링크가 가리킬 파일 경로. 디렉터리를 가리키면 `index.html`을 붙인다.

    `file://`로 열었을 때는 디렉터리 인덱스가 동작하지 않아 명시해야 한다.
    """
    path, sep, fragment = target.partition("#")
    if not path:
        # `/`(허브) 또는 `/#anchor`
        return "index.html" + sep + fragment
    last = path.rsplit("/", 1)[-1]
    if "." in last:
        # 이미 파일을 가리킨다 (예: `/static/app.css`)
        return path + sep + fragment
    return path.rstrip("/") + "/index.html" + sep + fragment


def relativize(html, route):
    """루트 기준 링크를 현재 페이지에서 출발하는 상대 링크로 바꾼다."""
    up = "../" * depth(route)
    return ROOT_LINK_RE.sub(
        lambda m: f'{m.group(1)}="{up}{_target_file(m.group(2))}"', html
    )


def render(route, client):
    """한 경로를 정적 HTML 문자열로 만든다."""
    response = client.get(route)
    if response.status_code != 200:
        raise RuntimeError(f"{route} 가 {response.status_code} 를 반환했다.")
    html = response.get_data(as_text=True)
    html = CONSULT_SECTION_RE.sub("", html)
    return relativize(html, route)


def build(out_dir=OUT_DIR):
    """정적 사이트를 통째로 다시 굽고, 쓴 경로 목록을 돌려준다."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    # Jekyll 처리를 건너뛴다. 이 사이트는 이미 완성된 HTML이다.
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    client = application.app.test_client()
    written = []
    for route in routes():
        path = output_path(route, out_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(route, client), encoding="utf-8")
        written.append((route, path))
    return written


if __name__ == "__main__":
    pages = build()
    print(f"{len(pages)}개 페이지를 {OUT_DIR.relative_to(BASE_DIR)}/ 에 썼다.\n")
    for route, path in pages:
        print(f"  {route:<28} → {path.relative_to(BASE_DIR)}")
