"""보험 영역의 서브 허브(`/insurance`). 기존 insurance 앱의 허브를 옮겨 왔다."""

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>보험 안내 | NextFinUp 종합자산관리</title>
<style>
  :root { color-scheme: light dark; --ink:#1f2e28; --paper:#f1ede1; --card:#fffcf5; --line:#d8d0ba; --accent:#a13d2e; }
  @media (prefers-color-scheme: dark) {
    :root { --ink:#eef0ea; --paper:#12160f; --card:#1c231a; --line:#3a4536; --accent:#e07a5f; }
  }
  :root[data-theme="dark"] { --ink:#eef0ea; --paper:#12160f; --card:#1c231a; --line:#3a4536; --accent:#e07a5f; }
  :root[data-theme="light"] { --ink:#1f2e28; --paper:#f1ede1; --card:#fffcf5; --line:#d8d0ba; --accent:#a13d2e; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--paper); color:var(--ink); line-height:1.6;
         font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Malgun Gothic','Apple SD Gothic Neo',sans-serif; }
  .wrap { max-width:900px; margin:0 auto; padding:48px 20px; }
  h1 { font-size:28px; margin:0 0 8px; }
  p.lead { color:var(--ink); opacity:.75; margin:0 0 32px; }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }
  a.card { display:block; background:var(--card); border:1px solid var(--line); border-radius:12px;
           padding:24px; text-decoration:none; color:inherit; }
  a.card:hover { border-color:var(--accent); }
  a.card h2 { margin:0 0 8px; font-size:20px; color:var(--accent); }
  a.card p { margin:0; font-size:14px; opacity:.8; }
  .table-scroll { overflow-x:auto; margin-top:32px; }
  table { border-collapse:collapse; width:100%; min-width:520px; font-size:14px; }
  th, td { border:1px solid var(--line); padding:10px 12px; text-align:left; }
  th { background:var(--card); }
  footer { margin-top:40px; font-size:13px; opacity:.7; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>보험, 어느 쪽부터 봐야 할까</h1>
    <p class="lead">보험은 크게 손해보험과 생명보험으로 나뉩니다. 보상 방식이 근본적으로 다릅니다.</p>

    <div class="cards">
      <a class="card" href="/insurance/life">
        <h2>생명보험 &rarr;</h2>
        <p>사람의 생사에 대해 약정한 금액을 정액 지급. 종신 · 정기 · 연금</p>
      </a>
      <a class="card" href="/insurance/damage">
        <h2>손해보험 &rarr;</h2>
        <p>재산상 손해를 실제 손해액만큼 보상. 화재 · 자동차 · 배상책임 · 보증</p>
      </a>
      <a class="card" href="/insurance/whole-life">
        <h2>종신보험 &rarr;</h2>
        <p>기간 제한 없이 사망을 보장. 보험금 확정 · 해지환급금 존재</p>
      </a>
      <a class="card" href="/insurance/term-life">
        <h2>정기보험 &rarr;</h2>
        <p>정해진 기간만 사망을 보장. 같은 보장에 보험료가 가장 저렴</p>
      </a>
      <a class="card" href="/insurance/variable">
        <h2>변액보험 &rarr;</h2>
        <p>보험료 일부를 펀드로 운용해 성과에 따라 보험금이 달라지는 상품</p>
      </a>
    </div>

    <div class="table-scroll">
      <table>
        <thead><tr><th>구분</th><th>손해보험</th><th>생명보험</th></tr></thead>
        <tbody>
          <tr><td>보험사고</td><td>재산상 손해</td><td>사람의 생사</td></tr>
          <tr><td>지급방식</td><td>실손보상</td><td>정액보상</td></tr>
          <tr><td>중복가입</td><td>비례분담</td><td>각각 전액 지급</td></tr>
          <tr><td>보험기간</td><td>1년 단위 갱신이 일반적 (장기손해보험 예외)</td><td>장기</td></tr>
        </tbody>
      </table>
    </div>

    <p>실손의료보험 · 암보험 등 제3보험은 손해보험과 생명보험 사이에 있으며 두 페이지 모두에서 다룹니다.
      <a href="/insurance/damage">손해보험 페이지에서 제3보험 보기 &rarr;</a></p>

    <footer><strong>NextFinUp</strong> · 교육용 일반 정보이며 특정 상품의 가입 권유가 아닙니다.</footer>
  </div>
</body>
</html>
"""


def render():
    return HTML
