"""작업 폴더(.adops/) 구성: 가짜 플랫폼 상태, 감사 로그, 브리핑 HTML."""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from adops import fakedata
from adops.adapters import AdPlatformAdapter, FailureMode, FakeAdServer, make_adapter
from adops.audit import AuditStore
from adops.models import Platform
from adops.rules.engine import DEFAULT_RULE_FILES, RuleSet, load_rules

DEFAULT_HOME = ".adops"


def resolve_home(home: str | Path | None = None) -> Path:
    return Path(home or os.environ.get("ADOPS_HOME") or DEFAULT_HOME)


@dataclass
class Workspace:
    home: Path

    @property
    def platform_path(self) -> Path:
        return self.home / "platform.json"

    @property
    def audit_path(self) -> Path:
        return self.home / "audit.sqlite3"

    @property
    def briefs_dir(self) -> Path:
        return self.home / "briefs"

    def seed(self, as_of: date = fakedata.DEMO_AS_OF, seed: int = fakedata.DEFAULT_SEED, reset: bool = True) -> Path:
        """가상 데이터를 새로 만든다. reset이면 감사 로그·브리핑도 지운다."""
        if reset and self.home.exists():
            shutil.rmtree(self.home)
        FakeAdServer.create(self.platform_path, fakedata.generate(as_of, seed))
        return self.platform_path

    def server(self, failure: FailureMode | None = None) -> FakeAdServer:
        return FakeAdServer(self.platform_path, failure)

    def store(self) -> AuditStore:
        return AuditStore(self.audit_path)

    def adapter(self, account_id: str, failure: FailureMode | None = None) -> AdPlatformAdapter:
        return make_adapter(self.server(failure), account_id)

    def account_ids(self) -> list[str]:
        return list(self.server().accounts())


def load_ruleset(platform: Platform, path: str | Path | None = None) -> tuple[RuleSet, str]:
    """규칙 파일을 읽는다. 경로가 없으면 플랫폼 기본 규칙."""
    file = Path(path) if path else DEFAULT_RULE_FILES[platform]
    ruleset = load_rules(file)
    if ruleset.platform != platform:
        raise ValueError(f"{file.name}은 {ruleset.platform} 규칙인데 {platform} 계정에 쓰려고 했습니다")
    label = str(path) if path else f"기본 규칙({file.name})"
    return ruleset, label
