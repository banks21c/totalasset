"""공통 상담 신청 폼.

연금저축 · IRP · ISA 세 페이지가 각자 다른 폼을 들고 있었고, 필드 구성도
전송 방식도 제각각이었다. 하나로 합쳐 서빙 시점에 끼워 넣는다.

페이지 HTML에 `<!-- ta:consult-form -->` 주석을 남겨두면 그 자리에 폼이 들어간다.
어느 페이지에서 신청했는지는 숨김 필드 `product`로 함께 보낸다.

라벨과 입력칸은 한 줄에 나란히 놓는다(좁은 화면에서는 위아래로 접힌다).
"""

# 마커. 페이지 HTML에 이 주석을 넣어두면 폼으로 치환된다.
MARKER = "<!-- ta:consult-form -->"

# 관심 분야 선택지. 사이트가 다루는 다섯 영역과 맞춘다.
INTERESTS = [
    "국민연금 수령 전략",
    "연금저축",
    "IRP",
    "ISA",
    "보험",
    "아직 잘 모르겠음 · 추천 필요",
]

_CSS = """
<style id="ta-consult-style">
  /* 카드 껍데기. 원래 각 페이지의 .consult가 하던 역할을 컴포넌트가 가져온다. */
  .ta-consult {
    --ta-label-w: 84px;
    max-width: 760px;
    background: var(--card, transparent);
    border: 1px solid var(--line, currentColor);
    border-radius: 10px;
    box-shadow: var(--shadow, none);
    padding: 32px 36px;
  }
  @media (max-width: 560px) { .ta-consult { padding: 24px 20px; } }
  /* 한 줄에 두 필드씩: 라벨·입력칸·라벨·입력칸 4칼럼. */
  .ta-consult .ta-row {
    display: grid;
    grid-template-columns: var(--ta-label-w) 1fr var(--ta-label-w) 1fr;
    align-items: center; gap: 12px 14px; margin-bottom: 14px;
  }
  /* 문의사항은 라벨 + 입력칸이 남은 폭을 다 쓴다. */
  .ta-consult .ta-row-wide { grid-template-columns: var(--ta-label-w) 1fr; }
  .ta-consult .ta-row-wide { align-items: start; }
  .ta-consult label {
    font-size: 14px; font-weight: 700; text-align: right; line-height: 1.4;
  }
  .ta-consult .ta-req { color: var(--accent, #a13d2e); margin-left: 2px; }
  .ta-consult input, .ta-consult select, .ta-consult textarea {
    width: 100%; padding: 10px 12px; font: inherit; font-size: 14px;
    color: inherit; background: transparent;
    border: 1px solid currentColor; border-radius: 7px;
    opacity: .95;
  }
  .ta-consult textarea { resize: vertical; min-height: 76px; }
  /* 버튼은 내용 폭만 차지하고 폼 가운데에 선다. */
  .ta-consult .ta-actions {
    display: flex; flex-direction: column; align-items: center; gap: 12px;
    margin-top: 22px;
  }
  /* 버튼 색은 페이지가 정의한 --accent / --accent-ink를 그대로 쓴다.
     폼이 들어가는 세 페이지 모두 이 두 변수를 갖고 있고, 값이 없을 때를
     대비해 폴백을 둔다. */
  .ta-consult .ta-submit {
    padding: 11px 28px; font: inherit; font-size: 14px; font-weight: 700;
    border-radius: 7px; cursor: pointer; min-width: 160px;
    background: var(--accent, #a13d2e);
    color: var(--accent-ink, #ffffff);
    border: 1px solid var(--accent, #a13d2e);
  }
  .ta-consult .ta-submit:hover { opacity: .9; }
  .ta-consult .ta-submit[disabled] { opacity: .55; cursor: default; }
  .ta-consult .ta-msg {
    display: none; width: 100%; padding: 12px 14px; text-align: center;
    border: 1px solid currentColor; border-radius: 7px; font-size: 14px;
  }
  .ta-consult .ta-msg-ok { color: var(--success, #2f7a4d); }
  .ta-consult .ta-msg-err { color: var(--accent, #a13d2e); }
  /* 두 필드를 나란히 두기 좁아지면 한 필드씩 한 줄로 내린다. */
  @media (max-width: 760px) {
    .ta-consult .ta-row { grid-template-columns: var(--ta-label-w) 1fr; }
  }
  /* 더 좁아지면 라벨도 입력칸 위로 올린다. */
  @media (max-width: 480px) {
    .ta-consult .ta-row, .ta-consult .ta-row-wide { grid-template-columns: 1fr; }
    .ta-consult label { text-align: left; }
    .ta-consult .ta-submit { width: 100%; }
  }
</style>
"""

_SCRIPT = """
<script>
  (function () {
    var form = document.getElementById('taConsultForm');
    if (!form) return;
    var btn = document.getElementById('taConsultSubmit');
    var ok = document.getElementById('taConsultOk');
    var err = document.getElementById('taConsultErr');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      ok.style.display = 'none';
      err.style.display = 'none';
      btn.disabled = true;
      var original = btn.textContent;
      btn.textContent = '전송 중...';

      fetch('/api/consult/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(new FormData(form))
      })
        .then(function (res) { return res.json().catch(function () { return { ok: false }; }); })
        .then(function (data) {
          if (data.ok) {
            ok.style.display = 'block';
            form.reset();
            ok.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } else {
            err.textContent = data.error || '신청에 실패했습니다. 잠시 후 다시 시도해주세요.';
            err.style.display = 'block';
          }
        })
        .catch(function () {
          err.textContent = '신청에 실패했습니다. 잠시 후 다시 시도해주세요.';
          err.style.display = 'block';
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = original;
        });
    });
  })();
</script>
"""


def render(product, default_interest=""):
    """`product` 페이지용 상담 폼 HTML을 만든다.

    `default_interest`가 INTERESTS 안에 있으면 그 항목을 미리 선택해 둔다.
    """
    options = ['<option value="">선택 안 함</option>']
    for item in INTERESTS:
        selected = " selected" if item == default_interest else ""
        options.append(f"<option{selected}>{item}</option>")

    return (
        _CSS
        + '<form class="ta-consult" id="taConsultForm">'
        + f'<input type="hidden" name="product" value="{product}">'
        # 1행: 이름 · 연락처
        + '<div class="ta-row">'
        '<label for="taName">이름<span class="ta-req">*</span></label>'
        '<input id="taName" name="name" type="text" required placeholder="홍길동">'
        '<label for="taPhone">연락처<span class="ta-req">*</span></label>'
        '<input id="taPhone" name="phone" type="tel" required placeholder="010-1234-5678">'
        "</div>"
        # 2행: 이메일 · 관심 분야
        '<div class="ta-row">'
        '<label for="taEmail">이메일</label>'
        '<input id="taEmail" name="email" type="email" placeholder="you@example.com">'
        '<label for="taInterest">관심 분야</label>'
        '<select id="taInterest" name="interest">' + "".join(options) + "</select>"
        "</div>"
        # 3행: 문의사항 (한 줄 전체)
        '<div class="ta-row ta-row-wide">'
        '<label for="taMessage">문의사항</label>'
        '<textarea id="taMessage" name="message" rows="3" '
        'placeholder="궁금한 점을 자유롭게 남겨주세요."></textarea>'
        "</div>"
        # 허니팟: 사람 눈에 보이지 않는 봇 차단 필드
        '<input type="text" name="website" autocomplete="off" tabindex="-1" '
        'aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0;">'
        '<div class="ta-actions">'
        '<button type="submit" class="ta-submit" id="taConsultSubmit">'
        "상담 신청하기</button>"
        '<div class="ta-msg ta-msg-ok" id="taConsultOk" role="status">'
        "신청이 접수되었습니다. 담당자가 남겨주신 연락처로 안내드립니다.</div>"
        '<div class="ta-msg ta-msg-err" id="taConsultErr" role="alert">'
        "신청에 실패했습니다. 잠시 후 다시 시도해주세요.</div>"
        "</div>"
        "</form>"
        + _SCRIPT
    )


def inject(html, product, default_interest=""):
    """`html` 안의 마커를 상담 폼으로 바꾼다. 마커가 없으면 그대로 둔다."""
    if MARKER not in html:
        return html
    return html.replace(MARKER, render(product, default_interest))
