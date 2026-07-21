"""NextFinUp 종합자산관리 — 통합 서버 (Flask).

흩어져 있던 국민연금 · 연금저축 · IRP · ISA · 보험 페이지를 한 서버에서 서빙하고,
모든 페이지 상단에 공통 네비게이션을 얹는다.

    GET  /                          허브
    GET  /national-pension          국민연금 안내
    GET  /national-pension/strategy 50~60대 활용 전략
    GET  /savings-pension           연금저축 안내 + 상담신청
    GET  /irp                       IRP 비교
    GET  /isa                       ISA 비교
    GET  /insurance                 보험 서브 허브
    GET  /insurance/damage          손해보험
    GET  /insurance/life            생명보험
    GET  /insurance/whole-life      종신보험
    GET  /insurance/variable        변액보험
    POST /api/consult/              상담신청 접수
    GET  /admin/consults            상담신청 목록 (ADMIN_TOKEN 필요)

각 페이지는 저마다 완결된 HTML 파일이라 템플릿 렌더링 없이 그대로 읽어 반환하고,
네비 바만 주입한다(nav.inject).
"""
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import consult
import hub
import insurance_hub
import nav

BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"

app = Flask(__name__)
app.teardown_appcontext(consult.close_db)


def _serve(relative_path):
    """`pages/` 아래 HTML을 읽어 네비 바를 주입해 반환한다."""
    html = (PAGES_DIR / relative_path).read_text(encoding="utf-8")
    return nav.inject(html, request.path)


def _serve_html(html):
    """직접 만든 HTML 문자열에 네비 바를 주입해 반환한다."""
    return nav.inject(html, request.path)


# ------------------------------------------------------------------ 허브
@app.get("/")
def index():
    return _serve_html(hub.render())


# ------------------------------------------------------------ 1층 국민연금
@app.get("/national-pension")
def national_pension():
    return _serve("national_pension/index.html")


@app.get("/national-pension/strategy")
def national_pension_strategy():
    return _serve("national_pension/strategy.html")


# ------------------------------------------------------- 3층 개인연금·절세
@app.get("/savings-pension")
def savings_pension():
    return _serve("savings_pension/index.html")


@app.get("/irp")
def irp():
    return _serve("irp/index.html")


@app.get("/isa")
def isa():
    return _serve("isa/index.html")


# ------------------------------------------------------------------ 보험
@app.get("/insurance")
def insurance():
    return _serve_html(insurance_hub.render())


@app.get("/insurance/damage")
def insurance_damage():
    return _serve("insurance/damage.html")


@app.get("/insurance/life")
def insurance_life():
    return _serve("insurance/life.html")


@app.get("/insurance/whole-life")
def insurance_whole_life():
    return _serve("insurance/whole_life.html")


@app.get("/insurance/variable")
def insurance_variable():
    return _serve("insurance/variable.html")


# ------------------------------------------------------------------ 상담
@app.post("/api/consult/")
def api_consult():
    return consult.submit()


@app.get("/admin/consults")
def admin_consults():
    if request.args.get("token") != consult.ADMIN_TOKEN:
        return jsonify(ok=False, error="인증이 필요합니다."), 401
    return render_template("admin.html", rows=consult.rows())


if __name__ == "__main__":
    consult.init_db()
    app.run(host="0.0.0.0", port=5000, debug=bool(os.environ.get("FLASK_DEBUG")))
