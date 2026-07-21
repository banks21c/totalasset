"""허브(`/`) 페이지. 5개 영역으로 들어가는 입구."""

CARDS = [
    ("/national-pension", "국민연금", "국가가 운영하는 노후 소득의 1층. 가입·수령 조건과 50~60대 활용 전략."),
    ("/savings-pension", "연금저축", "세액공제를 받으며 직접 쌓는 사적연금. 상품별 비교와 상담 신청."),
    ("/irp", "IRP", "퇴직금과 추가 납입을 함께 굴리는 개인형 퇴직연금 계좌."),
    ("/isa", "ISA", "예금·펀드·주식을 한 계좌에 담고 순이익에 비과세를 받는 만능통장."),
    ("/insurance", "보험", "손해보험 · 생명보험 · 변액보험. 보상 방식이 어떻게 다른지부터."),
]

LAYERS = [
    ("3층", "개인연금", "연금저축 · IRP · ISA", "스스로 준비하는 층. 세제 혜택이 핵심입니다."),
    ("2층", "퇴직연금", "IRP · DB · DC", "직장 생활에서 쌓이는 층."),
    ("1층", "국민연금", "노령연금 · 연기연금", "가장 아래에서 받치는 층. 평생 지급됩니다."),
]

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NextFinUp 종합자산관리</title>
<style>
  :root {
    color-scheme: light dark;
    --ink:#1f2e28; --paper:#f1ede1; --card:#fffcf5; --line:#d8d0ba; --accent:#a13d2e; --muted:#536056;
  }
  @media (prefers-color-scheme: dark) {
    :root { --ink:#eef0ea; --paper:#12160f; --card:#1c231a; --line:#3a4536; --accent:#e07a5f; --muted:#a3aa9c; }
  }
  :root[data-theme="dark"] {
    --ink:#eef0ea; --paper:#12160f; --card:#1c231a; --line:#3a4536; --accent:#e07a5f; --muted:#a3aa9c;
  }
  :root[data-theme="light"] {
    --ink:#1f2e28; --paper:#f1ede1; --card:#fffcf5; --line:#d8d0ba; --accent:#a13d2e; --muted:#536056;
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--paper); color:var(--ink); line-height:1.65;
         font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Malgun Gothic','Apple SD Gothic Neo',sans-serif; }
  .wrap { max-width:960px; margin:0 auto; padding:56px 20px 64px; }
  h1 { font-size:32px; margin:0 0 10px; letter-spacing:-.02em; }
  p.lead { color:var(--muted); margin:0 0 40px; font-size:16px; }
  h2.sec { font-size:15px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);
           margin:48px 0 16px; font-weight:600; }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
  a.card { display:block; background:var(--card); border:1px solid var(--line); border-radius:14px;
           padding:24px; text-decoration:none; color:inherit; transition:border-color .15s, transform .15s; }
  a.card:hover { border-color:var(--accent); transform:translateY(-2px); }
  a.card h3 { margin:0 0 8px; font-size:19px; color:var(--accent); }
  a.card p { margin:0; font-size:14px; color:var(--muted); }
  .layers { display:flex; flex-direction:column; gap:10px; }
  .layer { display:flex; align-items:baseline; gap:16px; flex-wrap:wrap;
           background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 20px; }
  .layer .n { font-weight:800; color:var(--accent); font-size:14px; flex:none; width:32px; }
  .layer .name { font-weight:700; font-size:16px; flex:none; }
  .layer .items { font-size:13px; color:var(--muted); flex:none; }
  .layer .desc { font-size:13px; color:var(--muted); margin-left:auto; }
  footer { margin-top:56px; padding-top:20px; border-top:1px solid var(--line);
           font-size:13px; color:var(--muted); }
</style>
</head>
<body>
  <div class="wrap">
    <h1>종합자산관리</h1>
    <p class="lead">국민연금부터 개인연금 · 보험까지, 노후 자산을 이루는 제도를 한자리에서 봅니다.</p>

    <h2 class="sec">노후소득 3층 구조</h2>
    <div class="layers">
      {layers}
    </div>

    <h2 class="sec">영역별 안내</h2>
    <div class="cards">
      {cards}
    </div>

    <footer>
      <strong>NextFinUp</strong> · 교육용 일반 정보이며 특정 상품의 가입 권유가 아닙니다.
      제도는 개정될 수 있으므로 실제 결정 전 최신 규정을 확인하세요.
    </footer>
  </div>
</body>
</html>
"""


def render():
    cards = "".join(
        f'<a class="card" href="{path}"><h3>{title} &rarr;</h3><p>{desc}</p></a>'
        for path, title, desc in CARDS
    )
    layers = "".join(
        f'<div class="layer"><span class="n">{n}</span>'
        f'<span class="name">{name}</span>'
        f'<span class="items">{items}</span>'
        f'<span class="desc">{desc}</span></div>'
        for n, name, items, desc in LAYERS
    )
    # CSS에 중괄호가 많아 str.format은 쓸 수 없다. 자리표시자만 직접 치환한다.
    return HTML.replace("{cards}", cards).replace("{layers}", layers)
