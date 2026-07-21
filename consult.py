"""상담신청 접수 (SQLite). 기존 pension 앱에서 옮겨 왔다.

연금저축 · IRP · ISA 세 페이지가 모두 `/api/consult/`로 폼을 전송하므로
접수 창구를 하나로 합친다.
"""
import os
import re
import sqlite3
from datetime import datetime, timezone

from flask import g, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "consultations.db")
# 관리자 목록 조회용 토큰. 운영 시 환경변수로 지정하세요.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "changeme")

PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db


def close_db(exc=None):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS consultations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT    NOT NULL,
                name       TEXT    NOT NULL,
                phone      TEXT    NOT NULL,
                email      TEXT,
                salary     TEXT,
                amount     TEXT,
                strategy   TEXT,
                message    TEXT
            )
            """
        )


def clean(value, limit=500):
    return (value or "").strip()[:limit]


def submit():
    """상담신청 폼을 받아 저장한다."""
    # 허니팟: 봇이 채우는 숨김 필드. 값이 있으면 조용히 성공 처리.
    if clean(request.form.get("website")):
        return jsonify(ok=True)

    name = clean(request.form.get("name"), 60)
    phone = clean(request.form.get("phone"), 30)
    if not name or not phone:
        return jsonify(ok=False, error="이름과 연락처는 필수입니다."), 400
    if not PHONE_RE.match(phone):
        return jsonify(ok=False, error="연락처 형식을 확인해주세요."), 400

    row = (
        datetime.now(timezone.utc).isoformat(timespec="seconds"),
        name,
        phone,
        clean(request.form.get("email"), 120),
        clean(request.form.get("salary"), 60),
        clean(request.form.get("amount"), 60),
        clean(request.form.get("strategy"), 60),
        clean(request.form.get("message"), 2000),
    )
    db = get_db()
    db.execute(
        """INSERT INTO consultations
           (created_at, name, phone, email, salary, amount, strategy, message)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        row,
    )
    db.commit()
    return jsonify(ok=True)


def rows():
    """접수된 상담신청을 최신순으로 반환한다."""
    return get_db().execute("SELECT * FROM consultations ORDER BY id DESC").fetchall()
