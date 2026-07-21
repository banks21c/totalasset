"""통합 서버의 라우팅·네비 계약 검증. `python test_app.py`로 실행한다."""
import app as application
import consult
import consult_form
import hub
import nav

PAGE_ROUTES = [
    "/",
    "/national-pension",
    "/national-pension/strategy",
    "/savings-pension",
    "/irp",
    "/isa",
    "/insurance",
    "/insurance/damage",
    "/insurance/life",
    "/insurance/whole-life",
    "/insurance/term-life",
    "/insurance/variable",
]

failures = []


def check(label, condition):
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


client = application.app.test_client()

print("모든 페이지가 200을 반환하고 네비 바를 포함한다")
for route in PAGE_ROUTES:
    response = client.get(route)
    body = response.get_data(as_text=True)
    check(f"{route} -> 200", response.status_code == 200)
    check(f"{route} 네비 바 주입됨", 'class="ta-nav"' in body)
    check(f"{route} 네비가 <body> 안에 있음", body.index("<body") < body.index('class="ta-nav"'))

print("현재 위치가 네비에서 활성 표시된다")
for route, expected in [
    ("/national-pension", "국민연금"),
    ("/national-pension/strategy", "국민연금"),
    ("/insurance/life", "보험"),
    ("/isa", "ISA"),
]:
    body = client.get(route).get_data(as_text=True)
    marker = f'aria-current="page">{expected}<'
    check(f"{route} -> {expected} 활성", marker in body)

print("허브에서 5개 영역으로 가는 링크가 모두 있다")
home = client.get("/").get_data(as_text=True)
for path, _title, _desc in hub.CARDS:
    check(f"허브 -> {path}", f'href="{path}"' in home)

print("/isa가 접두사만 겹치는 다른 메뉴를 활성화하지 않는다")
check("'/isa'는 '/is'로 시작하는 항목을 오탐하지 않음", nav._is_active("/insurance", "/isa") is False)
check("'/insurance'는 하위 경로에서 활성", nav._is_active("/insurance", "/insurance/life") is True)

print("페이지 안의 절대 링크가 통합 경로로 재작성되어 있다")
np_index = client.get("/national-pension").get_data(as_text=True)
check("국민연금 -> 전략 페이지 링크", 'href="/national-pension/strategy"' in np_index)
check("국민연금에 옛 '/strategy/' 링크가 남아있지 않음", 'href="/strategy/"' not in np_index)

damage = client.get("/insurance/damage").get_data(as_text=True)
check("손해보험 -> 생명보험 링크", 'href="/insurance/life"' in damage)

print("보험 하위 탭 4개가 보험 영역에서만 뜬다")
for route in ["/insurance", "/insurance/damage", "/insurance/life",
              "/insurance/whole-life", "/insurance/term-life", "/insurance/variable"]:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} 탭 바 있음", 'class="ta-tabs"' in body)
    for tab_path, tab_label in nav.SUB_TABS["/insurance"]:
        check(f"{route} 탭 '{tab_label}' 링크", f'href="{tab_path}"' in body)

for route in ["/", "/irp", "/isa", "/national-pension"]:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} 에는 보험 탭이 없음", 'class="ta-tabs"' not in body)

print("네비·탭이 본문 칼럼에 정렬된다")
for route in ["/", "/insurance", "/insurance/life", "/irp"]:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} 네비 링크가 .ta-inner 안에 있음",
          '<nav class="ta-nav"><div class="ta-inner">' in body)
tabs_page = client.get("/insurance/life").get_data(as_text=True)
check("탭 링크가 .ta-inner 안에 있음",
      '<div class="ta-tabs"><div class="ta-inner">' in tabs_page)
check("보험 허브 본문 폭이 다른 보험 페이지와 같음",
      "max-width:960px" in client.get("/insurance").get_data(as_text=True))

print("국민연금 페이지가 사이트 공통 스타일을 따른다")
for route in ["/national-pension", "/national-pension/strategy"]:
    body = client.get(route).get_data(as_text=True)
    for old in ["00539f", "003c73", "00a651"]:
        check(f"{route} 옛 국민연금 블루({old}) 없음", old not in body)
    check(f"{route} Pretendard 사용", "Pretendard" in body)
    check(f"{route} 본문 폭 960px", "max-width:960px" in body)
    check(f"{route} 다크모드 지원", "prefers-color-scheme" in body)
    check(f"{route} 공통 accent 사용", "#a13d2e" in body)

print("보험 탭 순서")
check(
    "생명보험이 손해보험보다 앞",
    [label for _path, label in nav.SUB_TABS["/insurance"]]
    == ["생명보험", "손해보험", "종신보험", "정기보험", "변액보험"],
)
hub_page = client.get("/insurance").get_data(as_text=True)
check(
    "보험 허브 카드도 생명보험이 앞",
    hub_page.index('href="/insurance/life"') < hub_page.index('href="/insurance/damage"'),
)

print("보험 탭이 본문 바탕 위의 폴더 탭 모양이다")
tab_css = client.get("/insurance/life").get_data(as_text=True)
check("탭 바 바탕이 본문과 같은 --paper", "background: var(--paper, var(--bg, transparent))" in tab_css)
check("옛 어두운 바탕 제거됨", "background: #1c231a" not in tab_css)
check("탭마다 테두리", "border: 1px solid var(--line, var(--border, currentColor))" in tab_css)
check("위쪽만 둥근 탭 모양", "border-radius: 7px 7px 0 0" in tab_css)
check("이웃 탭과 테두리 공유(붙임)", "margin-right: -1px" in tab_css)
check("안 눌린 탭은 --card-stub", "background: var(--card-stub, transparent)" in tab_css)
check("눌린 탭은 아래 선이 끊김", "border-bottom-color: transparent" in tab_css)
check("탭이 올라앉는 밑줄", "border-bottom: 1px solid var(--line, var(--border, currentColor))" in tab_css)
for route in ["/insurance", "/insurance/damage", "/insurance/life",
              "/insurance/whole-life", "/insurance/term-life", "/insurance/variable"]:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} --card-stub 정의됨", "--card-stub" in body)
    check(f"{route} --paper 정의됨", "--paper" in body)

print("보험 탭에서 현재 상품이 활성 표시된다")
for route, expected in [
    ("/insurance/whole-life", "종신보험"),
    ("/insurance/damage", "손해보험"),
    ("/insurance/variable", "변액보험"),
]:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} -> {expected} 탭 활성", f'aria-current="page">{expected}<' in body)

print("종신보험 페이지 내용")
whole_life = client.get("/insurance/whole-life").get_data(as_text=True)
for phrase in ["종신보험", "정기보험", "해지환급금", "예정이율", "사업비"]:
    check(f"'{phrase}' 다룸", phrase in whole_life)

print("정기보험 페이지 내용")
term_life = client.get("/insurance/term-life").get_data(as_text=True)
for phrase in ["정기보험", "갱신형", "비갱신형", "만기", "순수보장형", "보장기간"]:
    check(f"'{phrase}' 다룸", phrase in term_life)

print("생명보험 종류 표와 종신/정기 페이지가 서로 연결된다")
life = client.get("/insurance/life").get_data(as_text=True)
check("생명보험 표 -> 종신보험", 'href="/insurance/whole-life"' in life)
check("생명보험 표 -> 정기보험", 'href="/insurance/term-life"' in life)
check("종신보험 -> 정기보험", 'href="/insurance/term-life"' in whole_life)
check("정기보험 -> 종신보험", 'href="/insurance/whole-life"' in term_life)

print("상담 폼이 공통 컴포넌트로 3개 페이지에 들어간다")
FORM_PAGES = {"/savings-pension": "연금저축", "/irp": "IRP", "/isa": "ISA"}
for route, product in FORM_PAGES.items():
    body = client.get(route).get_data(as_text=True)
    check(f"{route} 공통 폼 있음", 'id="taConsultForm"' in body)
    check(f"{route} 마커가 남지 않음", consult_form.MARKER not in body)
    check(f"{route} 출처={product}", f'name="product" value="{product}"' in body)
    check(f"{route} 옛 폼 제거됨", 'class="consult"' not in body)
    check(f"{route} 옛 submitConsult 제거됨", "function submitConsult" not in body)
    for field in ["name", "phone", "email", "interest", "message"]:
        check(f"{route} 필드 {field}", f'name="{field}"' in body)
    check(f"{route} 허니팟 유지", 'name="website"' in body)

print("상담 폼이 없는 페이지에는 폼이 들어가지 않는다")
for route in ["/", "/irp", "/national-pension", "/insurance/life"]:
    body = client.get(route).get_data(as_text=True)
    if route in FORM_PAGES:
        continue
    check(f"{route} 폼 없음", 'id="taConsultForm"' not in body)

print("제출 버튼이 페이지 accent 변수를 쓴다")
for route in FORM_PAGES:
    body = client.get(route).get_data(as_text=True)
    check(f"{route} 버튼 배경 var(--accent)", "background: var(--accent, #a13d2e)" in body)
    check(f"{route} 버튼 글자 var(--accent-ink)", "color: var(--accent-ink, #ffffff)" in body)
    check(f"{route} invert 필터 제거됨", "filter: invert" not in body)
    check(f"{route} 페이지가 --accent-ink를 정의함", "--accent-ink:" in body)

print("한 줄에 두 필드씩 배치된다")
form_page = client.get("/irp").get_data(as_text=True)
check(
    "행이 4칼럼 그리드(라벨·입력·라벨·입력)",
    "grid-template-columns: var(--ta-label-w) 1fr var(--ta-label-w) 1fr" in form_page,
)
check("문의사항 행은 2칼럼", ".ta-row-wide { grid-template-columns: var(--ta-label-w) 1fr; }" in form_page)
check("좁은 화면에서 한 필드씩 내려감", "@media (max-width: 760px)" in form_page)
check("더 좁으면 라벨도 위로", "@media (max-width: 480px)" in form_page)

# 이름·연락처가 같은 .ta-row 안에, 이메일·관심분야가 같은 .ta-row 안에 있어야 한다
rows = form_page.split('<div class="ta-row')
check("이름과 연락처가 한 행", any('name="name"' in r and 'name="phone"' in r for r in rows))
check("이메일과 관심분야가 한 행", any('name="email"' in r and 'name="interest"' in r for r in rows))

print("출처·관심분야가 실제로 저장된다")
saved = client.post("/api/consult/", data={
    "name": "테스트", "phone": "010-0000-0000",
    "product": "IRP", "interest": "ISA", "message": "자동 테스트",
})
check("접수 성공", saved.get_json() == {"ok": True})
with application.app.app_context():
    latest = consult.rows()[0]
    check("product 저장됨", latest["product"] == "IRP")
    check("interest 저장됨", latest["interest"] == "ISA")
    # 테스트가 남긴 행은 지운다
    consult.get_db().execute("DELETE FROM consultations WHERE id = ?", (latest["id"],))
    consult.get_db().commit()

print("상담 API 계약")
check("이름·연락처 없으면 400", client.post("/api/consult/", data={}).status_code == 400)
check(
    "연락처 형식이 틀리면 400",
    client.post("/api/consult/", data={"name": "홍길동", "phone": "abc"}).status_code == 400,
)
check(
    "허니팟이 채워지면 저장 없이 성공",
    client.post("/api/consult/", data={"website": "bot"}).get_json() == {"ok": True},
)
check("토큰 없이 관리자 목록 조회하면 401", client.get("/admin/consults").status_code == 401)

print()
if failures:
    print(f"실패 {len(failures)}건: {failures}")
    raise SystemExit(1)
print("전부 통과")
