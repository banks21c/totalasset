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
  .ta-consult { --ta-label-w: 132px; max-width: 720px; }
  .ta-consult .ta-row {
    display: grid; grid-template-columns: var(--ta-label-w) 1fr;
    align-items: center; gap: 12px 16px; margin-bottom: 14px;
  }
  /* 문의사항은 여러 줄이라 라벨을 위쪽에 맞춘다. */
  .ta-consult .ta-row.ta-row-top { align-items: start; }
  .ta-consult label {
    font-size: 14px; font-weight: 700; text-align: right; line-height: 1.4;
  }
  .ta-consult .ta-req { color: #c2410c; margin-left: 2px; }
  .ta-consult input, .ta-consult select, .ta-consult textarea {
    width: 100%; padding: 10px 12px; font: inherit; font-size: 14px;
    color: inherit; background: transparent;
    border: 1px solid currentColor; border-radius: 7px;
    opacity: .95;
  }
  .ta-consult textarea { resize: vertical; min-height: 76px; }
  .ta-consult .ta-actions {
    display: grid; grid-template-columns: var(--ta-label-w) 1fr; gap: 16px;
  }
  .ta-consult .ta-submit {
    grid-column: 2; padding: 12px 24px; font: inherit; font-weight: 700;
    border: none; border-radius: 7px; cursor: pointer;
    background: currentColor; border: 1px solid currentColor;
  }
  .ta-consult .ta-submit span { filter: invert(1) grayscale(1) contrast(9); }
  .ta-consult .ta-submit[disabled] { opacity: .55; cursor: default; }
  .ta-consult .ta-msg {
    display: none; grid-column: 2; margin-top: 12px; padding: 12px 14px;
    border: 1px solid currentColor; border-radius: 7px; font-size: 14px;
  }
  @media (max-width: 620px) {
    .ta-consult .ta-row, .ta-consult .ta-actions { grid-template-columns: 1fr; }
    .ta-consult label { text-align: left; }
    .ta-consult .ta-submit, .ta-consult .ta-msg { grid-column: 1; }
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
      var label = btn.querySelector('span');
      var original = label.textContent;
      label.textContent = '전송 중...';

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
          label.textContent = original;
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
        + '<div class="ta-row">'
        '<label for="taName">이름<span class="ta-req">*</span></label>'
        '<input id="taName" name="name" type="text" required placeholder="홍길동">'
        "</div>"
        '<div class="ta-row">'
        '<label for="taPhone">연락처<span class="ta-req">*</span></label>'
        '<input id="taPhone" name="phone" type="tel" required placeholder="010-1234-5678">'
        "</div>"
        '<div class="ta-row">'
        '<label for="taEmail">이메일</label>'
        '<input id="taEmail" name="email" type="email" placeholder="you@example.com">'
        "</div>"
        '<div class="ta-row">'
        '<label for="taInterest">관심 분야</label>'
        '<select id="taInterest" name="interest">' + "".join(options) + "</select>"
        "</div>"
        '<div class="ta-row ta-row-top">'
        '<label for="taMessage">문의사항</label>'
        '<textarea id="taMessage" name="message" rows="3" '
        'placeholder="궁금한 점을 자유롭게 남겨주세요."></textarea>'
        "</div>"
        # 허니팟: 사람 눈에 보이지 않는 봇 차단 필드
        '<input type="text" name="website" autocomplete="off" tabindex="-1" '
        'aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0;">'
        '<div class="ta-actions">'
        '<button type="submit" class="ta-submit" id="taConsultSubmit">'
        "<span>상담 신청하기</span></button>"
        '<div class="ta-msg" id="taConsultOk">'
        "신청이 접수되었습니다. 담당자가 남겨주신 연락처로 안내드립니다.</div>"
        '<div class="ta-msg" id="taConsultErr">'
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
