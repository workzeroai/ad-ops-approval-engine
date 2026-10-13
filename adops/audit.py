"""감사 로그(SQLite).

- runs: 실행(조정안 묶음) 1건 = 계정 1개의 하루치 조정안
- changes: 변경 1건의 현재 상태
- events: 모든 단계의 기록(추가만 하고 고치거나 지우지 않는다)

상태 변경은 반드시 transition()을 거친다. 허용되지 않는 전이는 여기서 막히고,
상태 변경과 이벤트 기록이 한 트랜잭션으로 함께 저장된다.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from adops.models import Change, ChangeStatus, Platform, Run, RunStatus, check_transition

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    account_id  TEXT NOT NULL,
    platform    TEXT NOT NULL,
    ops_date    TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    status      TEXT NOT NULL,
    rules_file  TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS changes (
    change_id   TEXT PRIMARY KEY,
    run_id      TEXT NOT NULL REFERENCES runs(run_id),
    seq         INTEGER NOT NULL,
    payload     TEXT NOT NULL,
    status      TEXT NOT NULL,
    note        TEXT NOT NULL DEFAULT '',
    updated_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    run_id      TEXT NOT NULL,
    change_id   TEXT,
    actor       TEXT NOT NULL,
    action      TEXT NOT NULL,
    from_status TEXT,
    to_status   TEXT,
    detail      TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_events_run ON events(run_id);
CREATE INDEX IF NOT EXISTS idx_changes_run ON changes(run_id);
"""


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class AuditStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------ 실행
    def next_run_id(self, ops_date: date, platform: Platform) -> str:
        prefix = f"R{ops_date:%Y%m%d}-{'SA' if platform == Platform.SEARCHAD_LIKE else 'MT'}-"
        row = self.conn.execute("SELECT COUNT(*) FROM runs WHERE run_id LIKE ?", (prefix + "%",)).fetchone()
        return f"{prefix}{row[0] + 1:02d}"

    def save_run(self, run: Run, actor: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO runs VALUES (?,?,?,?,?,?,?)",
                (run.run_id, run.account_id, run.platform.value, run.ops_date.isoformat(), run.created_at,
                 run.status.value, run.rules_file),
            )
            self._event(run.run_id, None, actor, "run_created", None, run.status.value,
                        f"조정안 {len(run.changes)}건")
            for c in run.changes:
                self.conn.execute(
                    "INSERT INTO changes VALUES (?,?,?,?,?,?,?)",
                    (c.change_id, c.run_id, c.seq, c.model_dump_json(), c.status.value, c.note, _now()),
                )
                self._event(run.run_id, c.change_id, actor, "transition", None, c.status.value, c.reason)

    def get_run(self, run_id: str) -> Run:
        row = self.conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if row is None:
            raise KeyError(f"실행을 찾을 수 없습니다: {run_id}")
        changes = []
        for r in self.conn.execute("SELECT * FROM changes WHERE run_id = ? ORDER BY seq", (run_id,)):
            c = Change.model_validate_json(r["payload"])
            c.status = ChangeStatus(r["status"])
            c.note = r["note"]
            changes.append(c)
        return Run(run_id=row["run_id"], account_id=row["account_id"], platform=Platform(row["platform"]),
                   ops_date=date.fromisoformat(row["ops_date"]), created_at=row["created_at"],
                   status=RunStatus(row["status"]), rules_file=row["rules_file"], changes=changes)

    def list_runs(self, limit: int = 20) -> list[Run]:
        ids = [r[0] for r in self.conn.execute(
            "SELECT run_id FROM runs ORDER BY created_at DESC, run_id DESC LIMIT ?", (limit,))]
        return [self.get_run(i) for i in ids]

    def latest_run_id(self) -> str | None:
        row = self.conn.execute("SELECT run_id FROM runs ORDER BY created_at DESC, run_id DESC LIMIT 1").fetchone()
        return row[0] if row else None

    def set_run_status(self, run_id: str, status: RunStatus, actor: str, detail: str = "") -> None:
        with self.conn:
            old = self.conn.execute("SELECT status FROM runs WHERE run_id = ?", (run_id,)).fetchone()[0]
            self.conn.execute("UPDATE runs SET status = ? WHERE run_id = ?", (status.value, run_id))
            self._event(run_id, None, actor, "run_status", old, status.value, detail)

    # ------------------------------------------------------------ 변경
    def transition(self, change: Change, target: ChangeStatus, actor: str, note: str = "",
                   detail: str = "") -> None:
        """허용된 전이만 저장한다. 상태·사유·이벤트가 한 트랜잭션으로 기록된다."""
        row = self.conn.execute("SELECT status FROM changes WHERE change_id = ?", (change.change_id,)).fetchone()
        current = ChangeStatus(row[0])
        check_transition(current, target)
        with self.conn:
            self.conn.execute(
                "UPDATE changes SET status = ?, note = ?, updated_at = ? WHERE change_id = ?",
                (target.value, note or change.note, _now(), change.change_id),
            )
            self._event(change.run_id, change.change_id, actor, "transition", current.value, target.value,
                        detail or note)
        change.status = target
        if note:
            change.note = note

    def log(self, run_id: str, change_id: str | None, actor: str, action: str, detail: Any = "") -> None:
        with self.conn:
            self._event(run_id, change_id, actor, action, None, None, detail)

    def _event(self, run_id: str, change_id: str | None, actor: str, action: str, from_status: str | None,
               to_status: str | None, detail: Any) -> None:
        text = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
        self.conn.execute(
            "INSERT INTO events (ts, run_id, change_id, actor, action, from_status, to_status, detail) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (_now(), run_id, change_id, actor, action, from_status, to_status, text),
        )

    # ------------------------------------------------------------ 조회
    def events(self, run_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        sql = "SELECT * FROM events"
        args: tuple = ()
        if run_id:
            sql += " WHERE run_id = ?"
            args = (run_id,)
        sql += " ORDER BY id DESC LIMIT ?"
        rows = [dict(r) for r in self.conn.execute(sql, (*args, limit))]
        rows.reverse()
        return rows

    def count_applied(self, account_id: str, ops_date: date) -> int:
        """그 계정에 그날 실제로 반영(applied)된 변경 건수. 일일 상한 계산에 쓴다."""
        row = self.conn.execute(
            "SELECT COUNT(DISTINCT e.change_id) FROM events e JOIN runs r ON r.run_id = e.run_id "
            "WHERE r.account_id = ? AND r.ops_date = ? AND e.action = 'transition' AND e.to_status = 'applied'",
            (account_id, ops_date.isoformat()),
        ).fetchone()
        return int(row[0])
