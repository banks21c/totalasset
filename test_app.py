"""통합 서버의 라우팅·네비 계약 검증. `python test_app.py`로 실행한다."""
import app as application
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
