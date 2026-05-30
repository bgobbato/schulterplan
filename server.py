#!/usr/bin/env python3
"""
GPS Web Planner — Flask + SQLite backend.

Serves the static frontend (index.html, data/*) AND a small REST API
for storing cases, scenarios, comments, and a revision log.

Storage layout:
  storage/gps.db          SQLite database
  storage/cases/<id>/     One folder per case with binary meshes
                           - scapula.bin             (required)
                           - scapula_osteo.bin       (optional)

Run locally:
  pip install flask          # or: apt install python3-flask
  python3 server.py [port]

Sharing model:
  Two URLs per case
   - View: /?case=<id>
   - Edit: /?case=<id>&edit=<edit_token>
  Mutating endpoints require ?edit=<token> or X-Edit-Token header.
  Author of every change is taken from the X-Author header.
"""
from __future__ import annotations

import json
import os
import secrets
import sqlite3
import sys
import time
import shutil
from pathlib import Path

from flask import (
    Flask,
    abort,
    jsonify,
    request,
    send_file,
)

ROOT = Path(__file__).parent.resolve()
STORAGE = ROOT / "storage"
CASES_DIR = STORAGE / "cases"
DB_PATH = STORAGE / "gps.db"

STORAGE.mkdir(exist_ok=True)
CASES_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB upload ceiling

# ---------------------------------------------------------------------------
# Database schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
  id                       TEXT PRIMARY KEY,
  case_short_id            TEXT,
  side                     TEXT NOT NULL,
  surgeon                  TEXT,
  creator_name             TEXT,
  edit_token               TEXT NOT NULL,

  -- Pre-op measurements (parsed from landmarks.ini if available)
  preop_retroversion       REAL,
  preop_inclination        REAL,
  preop_subluxation        REAL,

  -- Original GPS planning (immutable snapshot of the imported reverse.ini)
  glenoid_plate            TEXT,
  orig_version             REAL,
  orig_inclination         REAL,
  orig_rotation            REAL,
  orig_implant_to_glenoid  TEXT,  -- JSON array of 16 floats
  patient_to_glenoid       TEXT,  -- JSON array of 16 floats

  -- Mesh files relative to STORAGE/cases/
  scapula_path             TEXT NOT NULL,
  scapula_osteo_path       TEXT,

  created_at               INTEGER NOT NULL,
  updated_at               INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS scenarios (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id           TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  slot              INTEGER,
  name              TEXT,
  author            TEXT,
  implant_type      TEXT,
  adj_retroversion  REAL DEFAULT 0,
  adj_inclination   REAL DEFAULT 0,
  adj_depth         REAL DEFAULT 0,
  adj_tx            REAL DEFAULT 0,
  adj_ty            REAL DEFAULT 0,
  adj_rotz          REAL DEFAULT 0,
  created_at        INTEGER NOT NULL,
  updated_at        INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id      TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  scenario_id  INTEGER REFERENCES scenarios(id) ON DELETE SET NULL,
  author       TEXT,
  text         TEXT NOT NULL,
  created_at   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS revisions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id      TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  author       TEXT,
  action       TEXT NOT NULL,
  payload_json TEXT,
  created_at   INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_scenarios_case ON scenarios(case_id);
CREATE INDEX IF NOT EXISTS idx_comments_case  ON comments(case_id);
CREATE INDEX IF NOT EXISTS idx_revisions_case ON revisions(case_id);
"""


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_ts() -> int:
    return int(time.time())


def random_id(n: int = 8) -> str:
    return secrets.token_urlsafe(n)[:n]


def request_author() -> str:
    return (request.headers.get("X-Author") or "Anonymous").strip()[:80] or "Anonymous"


def require_edit(case_id: str) -> dict:
    """Verify the request carries a valid edit token for this case."""
    token = request.args.get("edit") or request.headers.get("X-Edit-Token")
    if not token:
        abort(403, description="edit token required")
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM cases WHERE id = ?", (case_id,)
        ).fetchone()
    if not row:
        abort(404)
    if row["edit_token"] != token:
        abort(403, description="invalid edit token")
    return dict(row)


def safe_float(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def case_row_to_dict(row, include_planning: bool = True) -> dict:
    out = {
        "id": row["id"],
        "caseShortId": row["case_short_id"],
        "side": row["side"],
        "surgeon": row["surgeon"],
        "creatorName": row["creator_name"],
        "preOp": {
            "retroversion": row["preop_retroversion"],
            "inferiorInclination": row["preop_inclination"],
            "preOpSubluxation": row["preop_subluxation"],
        },
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }
    if include_planning:
        out["planning"] = {
            "glenoidPlate": row["glenoid_plate"],
            "version": row["orig_version"],
            "inclination": row["orig_inclination"],
            "rotation": row["orig_rotation"],
            "transfoFromImplantToLocalGlenoidRef":
                json.loads(row["orig_implant_to_glenoid"])
                if row["orig_implant_to_glenoid"] else None,
            "patientRefToGlenoidRef":
                json.loads(row["patient_to_glenoid"])
                if row["patient_to_glenoid"] else None,
        }
    out["hasOsteo"] = bool(row["scapula_osteo_path"])
    return out


def scenario_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "slot": row["slot"],
        "name": row["name"],
        "author": row["author"],
        "implantType": row["implant_type"],
        "adjust": {
            "retroversion": row["adj_retroversion"],
            "inclination": row["adj_inclination"],
            "depth": row["adj_depth"],
            "tx": row["adj_tx"],
            "ty": row["adj_ty"],
            "rotz": row["adj_rotz"],
        },
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def add_revision(conn, case_id: str, action: str, payload=None) -> None:
    conn.execute(
        "INSERT INTO revisions (case_id, author, action, payload_json, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (case_id, request_author(), action,
         json.dumps(payload) if payload else None, now_ts()),
    )


# ---------------------------------------------------------------------------
# Static frontend
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_file(ROOT / "index.html")


@app.route("/<path:path>")
def static_files(path: str):
    # Block direct access to server.py and storage/ tree
    if path == "server.py" or path.startswith("storage/") or path.startswith("deploy/"):
        abort(404)
    full = ROOT / path
    if not full.exists() or not full.is_file():
        abort(404)
    return send_file(full)


# ---------------------------------------------------------------------------
# API: cases
# ---------------------------------------------------------------------------

@app.route("/api/cases", methods=["POST"])
def create_case():
    """Multipart upload: metadata (JSON), scapula (.bin), scapula_osteo (.bin) optional."""
    try:
        metadata = json.loads(request.form.get("metadata", "{}"))
    except json.JSONDecodeError:
        abort(400, "invalid metadata JSON")

    scapula_file = request.files.get("scapula")
    if not scapula_file:
        abort(400, "scapula file is required")

    case_id = random_id(8)
    while (CASES_DIR / case_id).exists():
        case_id = random_id(8)
    edit_token = secrets.token_urlsafe(16)

    case_dir = CASES_DIR / case_id
    case_dir.mkdir(parents=True)
    scapula_file.save(case_dir / "scapula.bin")
    scapula_path = f"{case_id}/scapula.bin"

    osteo_file = request.files.get("scapula_osteo")
    osteo_path = None
    if osteo_file:
        osteo_file.save(case_dir / "scapula_osteo.bin")
        osteo_path = f"{case_id}/scapula_osteo.bin"

    p = metadata.get("planning") or {}
    preop = metadata.get("preOp") or {}
    t = now_ts()

    with get_db() as conn:
        conn.execute("""
            INSERT INTO cases (
                id, case_short_id, side, surgeon, creator_name, edit_token,
                preop_retroversion, preop_inclination, preop_subluxation,
                glenoid_plate, orig_version, orig_inclination, orig_rotation,
                orig_implant_to_glenoid, patient_to_glenoid,
                scapula_path, scapula_osteo_path,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            metadata.get("caseShortId"),
            (metadata.get("side") or "?")[:8],
            metadata.get("surgeon"),
            metadata.get("creatorName") or request_author(),
            edit_token,
            safe_float(preop.get("retroversion")),
            safe_float(preop.get("inferiorInclination")),
            safe_float(preop.get("preOpSubluxation")),
            p.get("glenoidPlate"),
            safe_float(p.get("version")),
            safe_float(p.get("inclination")),
            safe_float(p.get("rotation")),
            json.dumps(p.get("transfoFromImplantToLocalGlenoidRef"))
                if p.get("transfoFromImplantToLocalGlenoidRef") else None,
            json.dumps(p.get("patientRefToGlenoidRef"))
                if p.get("patientRefToGlenoidRef") else None,
            scapula_path,
            osteo_path,
            t, t
        ))
        add_revision(conn, case_id, "create_case",
                     {"caseShortId": metadata.get("caseShortId")})

    return jsonify({"id": case_id, "edit_token": edit_token}), 201


@app.route("/api/cases", methods=["GET"])
def list_cases():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT c.*,
                (SELECT COUNT(*) FROM scenarios WHERE case_id = c.id) AS sc,
                (SELECT COUNT(*) FROM comments  WHERE case_id = c.id) AS cc
            FROM cases c
            ORDER BY updated_at DESC
        """).fetchall()
    out = []
    for r in rows:
        d = case_row_to_dict(r, include_planning=False)
        d["scenariosCount"] = r["sc"]
        d["commentsCount"] = r["cc"]
        out.append(d)
    return jsonify({"cases": out})


@app.route("/api/cases/<case_id>", methods=["GET"])
def get_case(case_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
        if not row:
            abort(404)
        scenarios = conn.execute(
            "SELECT * FROM scenarios WHERE case_id = ? ORDER BY id ASC", (case_id,)
        ).fetchall()
        comments = conn.execute(
            "SELECT * FROM comments WHERE case_id = ? ORDER BY id ASC", (case_id,)
        ).fetchall()
    data = case_row_to_dict(row)
    data["scenarios"] = [scenario_row_to_dict(s) for s in scenarios]
    data["comments"] = [
        {
            "id": c["id"], "author": c["author"], "text": c["text"],
            "scenarioId": c["scenario_id"], "createdAt": c["created_at"],
        } for c in comments
    ]
    return jsonify(data)


@app.route("/api/cases/<case_id>/mesh/<mesh_name>")
def get_mesh(case_id, mesh_name):
    if mesh_name not in ("scapula", "scapula_osteo"):
        abort(404)
    fp = CASES_DIR / case_id / f"{mesh_name}.bin"
    if not fp.is_file():
        abort(404)
    return send_file(fp, mimetype="application/octet-stream")


@app.route("/api/cases/<case_id>", methods=["DELETE"])
def delete_case(case_id):
    require_edit(case_id)
    with get_db() as conn:
        conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    case_dir = CASES_DIR / case_id
    if case_dir.exists():
        shutil.rmtree(case_dir)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API: scenarios
# ---------------------------------------------------------------------------

@app.route("/api/cases/<case_id>/scenarios", methods=["POST"])
def create_scenario(case_id):
    require_edit(case_id)
    body = request.get_json(force=True, silent=True) or {}
    adj = body.get("adjust") or {}
    t = now_ts()
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO scenarios (
                case_id, slot, name, author, implant_type,
                adj_retroversion, adj_inclination, adj_depth,
                adj_tx, adj_ty, adj_rotz,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id, body.get("slot"), body.get("name"),
            request_author(), body.get("implantType"),
            safe_float(adj.get("retroversion")) or 0,
            safe_float(adj.get("inclination")) or 0,
            safe_float(adj.get("depth")) or 0,
            safe_float(adj.get("tx")) or 0,
            safe_float(adj.get("ty")) or 0,
            safe_float(adj.get("rotz")) or 0,
            t, t,
        ))
        sid = cur.lastrowid
        conn.execute("UPDATE cases SET updated_at = ? WHERE id = ?", (t, case_id))
        add_revision(conn, case_id, "add_scenario",
                     {"id": sid, "name": body.get("name")})
    return jsonify({"id": sid}), 201


@app.route("/api/cases/<case_id>/scenarios/<int:sid>", methods=["PUT"])
def update_scenario(case_id, sid):
    require_edit(case_id)
    body = request.get_json(force=True, silent=True) or {}
    adj = body.get("adjust") or {}
    t = now_ts()
    with get_db() as conn:
        conn.execute("""
            UPDATE scenarios SET
                slot = ?, name = ?, author = ?, implant_type = ?,
                adj_retroversion = ?, adj_inclination = ?, adj_depth = ?,
                adj_tx = ?, adj_ty = ?, adj_rotz = ?, updated_at = ?
            WHERE id = ? AND case_id = ?
        """, (
            body.get("slot"), body.get("name"),
            request_author(), body.get("implantType"),
            safe_float(adj.get("retroversion")) or 0,
            safe_float(adj.get("inclination")) or 0,
            safe_float(adj.get("depth")) or 0,
            safe_float(adj.get("tx")) or 0,
            safe_float(adj.get("ty")) or 0,
            safe_float(adj.get("rotz")) or 0,
            t, sid, case_id,
        ))
        conn.execute("UPDATE cases SET updated_at = ? WHERE id = ?", (t, case_id))
        add_revision(conn, case_id, "edit_scenario", {"id": sid})
    return jsonify({"ok": True})


@app.route("/api/cases/<case_id>/scenarios/<int:sid>", methods=["DELETE"])
def delete_scenario(case_id, sid):
    require_edit(case_id)
    with get_db() as conn:
        conn.execute("DELETE FROM scenarios WHERE id = ? AND case_id = ?",
                     (sid, case_id))
        conn.execute("UPDATE cases SET updated_at = ? WHERE id = ?",
                     (now_ts(), case_id))
        add_revision(conn, case_id, "delete_scenario", {"id": sid})
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API: comments
# ---------------------------------------------------------------------------

@app.route("/api/cases/<case_id>/comments", methods=["POST"])
def add_comment(case_id):
    body = request.get_json(force=True, silent=True) or {}
    text = (body.get("text") or "").strip()
    if not text:
        abort(400, "text required")
    text = text[:2000]
    with get_db() as conn:
        if not conn.execute("SELECT 1 FROM cases WHERE id = ?", (case_id,)).fetchone():
            abort(404)
        cur = conn.execute("""
            INSERT INTO comments (case_id, scenario_id, author, text, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (case_id, body.get("scenarioId"), request_author(), text, now_ts()))
        cid = cur.lastrowid
        add_revision(conn, case_id, "add_comment", {"id": cid})
    return jsonify({
        "id": cid, "author": request_author(), "text": text,
        "scenarioId": body.get("scenarioId"), "createdAt": now_ts(),
    }), 201


# ---------------------------------------------------------------------------
# Error handler — return JSON for API errors
# ---------------------------------------------------------------------------

@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(400)
@app.errorhandler(413)
def json_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": str(e.description if hasattr(e, "description") else e),
                        "code": e.code}), e.code
    return e.get_response()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

init_db()


if __name__ == "__main__":
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    print(f"GPS Web Planner serving on http://127.0.0.1:{port}")
    print(f"Storage: {STORAGE}")
    # Bind to 127.0.0.1 only — Nginx proxies in production
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
