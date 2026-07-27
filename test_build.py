"""정적 빌드(`build_static.py`) 검증. `python test_build.py`로 실행한다.

임시 디렉터리에 실제로 한 벌 구운 뒤, GitHub Pages에 올렸을 때 깨질 만한 것들을
확인한다. 가장 중요한 것은 모든 내부 링크가 실제로 존재하는 파일을 가리키는지다.
"""
import re
import tempfile
from pathlib import Path
from urllib.parse import unquote

import build_static

failures = []


def check(label, condition):
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


LINK_RE = re.compile(r'\b(?:href|src)="([^"]*)"')
# 외부로 나가거나 페이지 안에 머무는 링크. 파일로 해석하지 않는다.
EXTERNAL_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#|$)", re.IGNORECASE)

out_dir = Path(tempfile.mkdtemp(prefix="totalasset-build-")) / "docs"
pages = build_static.build(out_dir)
routes = [route for route, _path in pages]

print("앱의 모든 정적 라우트가 파일로 나온다")
check("구워진 페이지가 하나 이상", len(pages) > 0)
check("허브가 index.html로 나옴", (out_dir / "index.html").is_file())
check(".nojekyll 포함", (out_dir / ".nojekyll").is_file())
for route, path in pages:
    check(f"{route} -> {path.relative_to(out_dir)}", path.is_file())

print("백엔드가 필요한 경로는 굽지 않는다")
check("/api/consult/ 제외됨", not any(r.startswith("/api/") for r in routes))
check("/admin/consults 제외됨", not any(r.startswith("/admin/") for r in routes))

print("모든 내부 링크가 실제 존재하는 파일을 가리킨다")
broken = []
checked_links = 0
for _route, path in pages:
    html = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(html):
        if EXTERNAL_RE.match(target):
            continue
        relative = unquote(target.partition("#")[0].partition("?")[0])
        if not relative:
            continue
        checked_links += 1
        if not (path.parent / relative).resolve().is_file():
            broken.append(f"{path.relative_to(out_dir)} -> {target}")
check(f"내부 링크 {checked_links}개를 검사함", checked_links > 0)
check(f"깨진 링크 없음 ({broken[:5]})" if broken else "깨진 링크 없음", not broken)

print("루트 기준 절대경로가 남아있지 않다")
for _route, path in pages:
    html = path.read_text(encoding="utf-8")
    leftovers = re.findall(r'\b(?:href|src)="/(?!/)[^"]*"', html)
    check(f"{path.relative_to(out_dir)} 절대경로 없음", not leftovers)

print("네비 바가 모든 페이지에 들어 있다")
for _route, path in pages:
    html = path.read_text(encoding="utf-8")
    check(f"{path.relative_to(out_dir)} 네비 포함", 'class="ta-nav"' in html)

print("상담 폼은 정적 결과물에 없다")
for _route, path in pages:
    html = path.read_text(encoding="utf-8")
    check(f"{path.relative_to(out_dir)} 상담 섹션 제거됨", "전문가 상담 신청" not in html)
    check(f"{path.relative_to(out_dir)} 폼 POST 없음", "/api/consult/" not in html)
    check(f"{path.relative_to(out_dir)} 마커 잔여 없음", "ta:consult-section" not in html)

print("허브에서 7개 영역으로 가는 링크가 모두 살아 있다")
home = (out_dir / "index.html").read_text(encoding="utf-8")
import hub  # noqa: E402  (빌드 후에 읽어야 할 이유는 없지만 검증 대상과 나란히 둔다)

for path_, _title, _desc in hub.CARDS:
    expected = path_.strip("/") + "/index.html"
    check(f"허브 -> {expected}", f'href="{expected}"' in home)

print("상대경로 깊이가 페이지마다 맞다")
damage = (out_dir / "insurance" / "damage" / "index.html").read_text(encoding="utf-8")
check("깊이 2에서 허브 링크는 ../../index.html", 'href="../../index.html"' in damage)
check("깊이 2에서 채권 링크는 ../../bond/index.html", 'href="../../bond/index.html"' in damage)
bond = (out_dir / "bond" / "index.html").read_text(encoding="utf-8")
check("깊이 1에서 허브 링크는 ../index.html", 'href="../index.html"' in bond)

print()
if failures:
    print(f"실패 {len(failures)}건:")
    for item in failures:
        print(f"  - {item}")
    raise SystemExit(1)
print("전부 통과")
