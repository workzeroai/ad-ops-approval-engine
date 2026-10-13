"""가짜 광고 API 서버.

실제 광고 플랫폼 대신 로컬 JSON 파일 하나에 계정·캠페인·키워드·소재·일별 실적을 저장한다.
검색광고형과 메타형은 응답 모양(필드 이름, 숫자 표기)을 일부러 다르게 두었고,
어댑터(searchad_like.py, meta_like.py)가 이를 공통 모델로 바꾼다.

실패 시뮬레이션(FailureMode)을 켜면 변경 요청이 일정 확률로 실패한다. seed를 고정하면 매번 같은 순서로 실패한다.
- transient: 일시 오류(HTTP 503)로 예외 발생 → 실행기가 재시도
- silent: 응답은 성공인데 값이 바뀌지 않음 → 재조회 검증에서만 잡힌다
"""
from __future__ import annotations

import copy
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

# 플랫폼별로 "마지막 수정 시각" 필드 이름이 다르다.
_UPDATED_KEY = {"searchad_like": "editTm", "meta_like": "updated_time"}


class ApiError(RuntimeError):
    """광고 API 오류. transient=True면 재시도할 수 있다."""

    transient = False


class TransientApiError(ApiError):
    transient = True


class PermanentApiError(ApiError):
    transient = False


@dataclass(frozen=True)
class FailureMode:
    rate: float = 0.0  # 변경 요청 1건이 실패할 확률
    seed: int = 0
    transient_share: float = 0.5  # 실패 중 일시 오류 비율(나머지는 '응답 성공·값 미반영')

    @property
    def enabled(self) -> bool:
        return self.rate > 0


class FakeAdServer:
    """상태를 JSON 파일에 저장하는 가짜 광고 API."""

    def __init__(self, path: Path, failure: FailureMode | None = None):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"가짜 플랫폼 데이터가 없습니다: {self.path} (먼저 `adops seed` 실행)")
        self._state: dict[str, Any] = {}
        self._stamp: tuple[int, int] | None = None
        self._sync()
        self.failure = failure or FailureMode()
        self._rng = random.Random(self.failure.seed)
        self.request_log: list[dict[str, Any]] = []

    # ------------------------------------------------------------ 생성·저장
    @classmethod
    def create(cls, path: Path, state: dict[str, Any], failure: FailureMode | None = None) -> FakeAdServer:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        return cls(path, failure)

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._state, ensure_ascii=False, indent=1), encoding="utf-8")
        self._stamp = self._file_stamp()

    def _file_stamp(self) -> tuple[int, int]:
        st = self.path.stat()
        return st.st_mtime_ns, st.st_size

    def _sync(self) -> None:
        """다른 프로세스·인스턴스가 바꾼 값도 보이도록, 파일이 바뀌었으면 다시 읽는다(실제 API처럼)."""
        stamp = self._file_stamp()
        if stamp != self._stamp:
            self._state = json.loads(self.path.read_text(encoding="utf-8"))
            self._stamp = stamp

    # ------------------------------------------------------------ 조회
    @property
    def as_of(self) -> date:
        """실적이 마감된 마지막 날(어제)."""
        return date.fromisoformat(self._state["meta"]["as_of"])

    @property
    def ops_date(self) -> date:
        """운영일(오늘). 실적 마감일 다음 날."""
        return self.as_of + timedelta(days=1)

    def accounts(self) -> dict[str, dict[str, Any]]:
        return copy.deepcopy(self._state["accounts"])

    def account(self, account_id: str) -> dict[str, Any]:
        try:
            return copy.deepcopy(self._state["accounts"][account_id])
        except KeyError as exc:
            raise KeyError(f"알 수 없는 계정: {account_id}") from exc

    def object_counts(self, account_id: str) -> dict[str, int]:
        return {k: len(v) for k, v in self._state["objects"][account_id].items()}

    def list_objects(self, account_id: str, collection: str) -> list[dict[str, Any]]:
        self._sync()
        self._log("GET", account_id, collection)
        return copy.deepcopy(self._state["objects"][account_id][collection])

    def get_object(self, account_id: str, collection: str, object_id: str, id_key: str) -> dict[str, Any]:
        self._sync()
        self._log("GET", account_id, f"{collection}/{object_id}")
        for obj in self._state["objects"][account_id][collection]:
            if obj[id_key] == object_id:
                return copy.deepcopy(obj)
        raise PermanentApiError(f"HTTP 404: {collection}/{object_id} 없음")

    def list_stats(self, account_id: str, start: date, end: date, level: str | None = None) -> list[dict]:
        self._sync()
        self._log("GET", account_id, f"stats?level={level}&since={start}&until={end}")
        rows = []
        for row in self._state["stats"][account_id]:
            d = date.fromisoformat(row.get("statDt") or row.get("date_start"))
            if start <= d <= end and (level is None or row.get("level", "ad") == level):
                rows.append(copy.deepcopy(row))
        return rows

    # ------------------------------------------------------------ 변경
    def update_object(self, account_id: str, collection: str, object_id: str, id_key: str,
                      patch: dict[str, Any]) -> dict[str, Any]:
        """객체 일부 필드를 바꾼다. 실패 시뮬레이션이 켜져 있으면 일정 확률로 실패한다."""
        self._sync()
        self._log("PUT", account_id, f"{collection}/{object_id}", patch)
        target = None
        for obj in self._state["objects"][account_id][collection]:
            if obj[id_key] == object_id:
                target = obj
                break
        if target is None:
            raise PermanentApiError(f"HTTP 404: {collection}/{object_id} 없음")
        unknown = set(patch) - set(target)
        if unknown:
            raise PermanentApiError(f"HTTP 400: 알 수 없는 필드 {sorted(unknown)}")

        if self.failure.enabled and self._rng.random() < self.failure.rate:
            if self._rng.random() < self.failure.transient_share:
                self.request_log[-1]["result"] = "503"
                raise TransientApiError("HTTP 503: 일시적으로 요청을 처리할 수 없습니다")
            # 응답은 성공처럼 돌려주지만 저장하지 않는다(재조회 검증에서만 드러나는 실패).
            self.request_log[-1]["result"] = "200 (값 미반영)"
            return {"ok": True, **copy.deepcopy(target)}

        target.update(patch)
        platform = self._state["accounts"][account_id]["platform"]
        key = _UPDATED_KEY[platform]
        if key in target:
            target[key] = self.ops_date.isoformat()
        self._save()
        self.request_log[-1]["result"] = "200"
        return {"ok": True, **copy.deepcopy(target)}

    def _log(self, method: str, account_id: str, path: str, body: dict | None = None) -> None:
        self.request_log.append({"method": method, "account": account_id, "path": path, "body": body})
