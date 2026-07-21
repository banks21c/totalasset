"""모든 페이지 상단에 공통 네비게이션 바를 주입한다.

각 페이지는 저마다 완결된 HTML 파일이고 CSS도 서로 다르다. 템플릿 상속으로
묶으려면 8개 파일을 전부 뜯어야 하므로, 대신 서빙 시점에 `<body>` 바로 뒤로
네비 바를 끼워 넣는다. 원본 HTML은 그대로 두고 통합만 얹는 방식이다.

주입되는 스타일은 `ta-` 접두사를 붙여 각 페이지의 기존 CSS와 충돌하지 않게 한다.
"""
import re

BRAND = "NextFinUp 종합자산관리"

# (경로, 표시 이름). 활성 여부는 현재 경로가 이 경로로 시작하는지로 판정한다.
NAV_ITEMS = [
    ("/national-pension", "국민연금"),
    ("/savings-pension", "연금저축"),
    ("/irp", "IRP"),
    ("/isa", "ISA"),
    ("/insurance", "보험"),
]

# 영역 안에서 다시 갈라지는 하위 탭. 해당 영역에 들어왔을 때만 네비 바 아래에 붙는다.
SUB_TABS = {
    "/insurance": [
        ("/insurance/life", "생명보험"),
        ("/insurance/damage", "손해보험"),
        ("/insurance/whole-life", "종신보험"),
        ("/insurance/term-life", "정기보험"),
        ("/insurance/variable", "변액보험"),
    ],
}

_NAV_CSS = """
<style id="ta-nav-style">
  :root { --ta-nav-h: 52px; }
  /* 페이지 자체의 sticky 헤더(예: 국민연금)가 네비 바 아래로 붙도록 밀어준다.
     `top`은 positioned 요소에만 적용되므로 static 헤더에는 아무 영향이 없다. */
  body > header, body > .header { top: var(--ta-nav-h) !important; }
  .ta-nav {
    position: sticky; top: 0; z-index: 10000;
    display: flex; align-items: center; gap: 4px;
    height: var(--ta-nav-h); padding: 0 16px;
    background: #12160f; color: #eef0ea;
    font-family: 'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;
    font-size: 14px; line-height: 1;
    overflow-x: auto; -webkit-overflow-scrolling: touch;
  }
  .ta-nav::-webkit-scrollbar { display: none; }
  .ta-nav a { color: inherit; text-decoration: none; white-space: nowrap; }
  .ta-nav .ta-brand {
    font-weight: 700; margin-right: 12px; padding: 8px 4px;
    display: flex; align-items: center; gap: 8px;
  }
  .ta-nav .ta-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: linear-gradient(135deg, #e07a5f, #a8c686); flex: none;
  }
  .ta-nav .ta-link { padding: 8px 12px; border-radius: 7px; opacity: .72; }
  .ta-nav .ta-link:hover { opacity: 1; background: rgba(255,255,255,.09); }
  .ta-nav .ta-link[aria-current="page"] {
    opacity: 1; background: rgba(224,122,95,.22); color: #f2a68e; font-weight: 600;
  }

  /* 하위 탭. 페이지마다 배경색이 달라 색을 물려받지 않고 자체 색을 쓴다. */
  .ta-tabs {
    position: sticky; top: var(--ta-nav-h); z-index: 9998;
    display: flex; gap: 2px; padding: 0 12px;
    background: #1c231a; border-bottom: 1px solid #3a4536;
    font-family: 'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;
    font-size: 14px; overflow-x: auto;
  }
  .ta-tabs::-webkit-scrollbar { display: none; }
  .ta-tabs a {
    color: #b7bfae; text-decoration: none; white-space: nowrap;
    padding: 12px 16px; border-bottom: 2px solid transparent; margin-bottom: -1px;
  }
  .ta-tabs a:hover { color: #eef0ea; }
  .ta-tabs a[aria-current="page"] {
    color: #e07a5f; border-bottom-color: #e07a5f; font-weight: 700;
  }
</style>
"""

# `<body ...>` 여는 태그. 속성이 붙어 있을 수 있어 정규식으로 찾는다.
_BODY_OPEN_RE = re.compile(r"<body\b[^>]*>", re.IGNORECASE)


def _is_active(item_path, current_path):
    """현재 경로가 해당 메뉴에 속하는지 판정한다.

    `/insurance`와 `/insurance/life`는 같은 메뉴지만, `/isa`가 `/is`로 시작하는
    다른 항목까지 활성으로 만들면 안 되므로 경계(`/`)까지 확인한다.
    """
    return current_path == item_path or current_path.startswith(item_path + "/")


def render_nav(current_path):
    """현재 경로를 기준으로 네비 바 HTML을 만든다."""
    links = []
    for path, label in NAV_ITEMS:
        current = ' aria-current="page"' if _is_active(path, current_path) else ""
        links.append(f'<a class="ta-link" href="{path}"{current}>{label}</a>')
    return (
        _NAV_CSS
        + '<nav class="ta-nav">'
        + f'<a class="ta-brand" href="/"><span class="ta-dot"></span>{BRAND}</a>'
        + "".join(links)
        + "</nav>"
    )


def render_tabs(current_path):
    """현재 영역에 하위 탭이 있으면 탭 바 HTML을, 없으면 빈 문자열을 반환한다."""
    for section, tabs in SUB_TABS.items():
        if not _is_active(section, current_path):
            continue
        links = []
        for path, label in tabs:
            current = ' aria-current="page"' if _is_active(path, current_path) else ""
            links.append(f'<a href="{path}"{current}>{label}</a>')
        return '<div class="ta-tabs">' + "".join(links) + "</div>"
    return ""


def inject(html, current_path):
    """`html`의 `<body>` 직후에 네비 바(+하위 탭)를 넣어 반환한다.

    `<body>` 태그를 못 찾으면 (조각 HTML 등) 맨 앞에 붙인다.
    """
    nav = render_nav(current_path) + render_tabs(current_path)
    match = _BODY_OPEN_RE.search(html)
    if not match:
        return nav + html
    end = match.end()
    return html[:end] + nav + html[end:]
