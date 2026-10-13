from __future__ import annotations

from pathlib import Path

import pytest

from adops.diagnose import diagnose
from adops.execute import Executor
from adops.fakedata import MT_ACCOUNT, SA_ACCOUNT
from adops.models import Platform
from adops.plan import build_plan
from adops.workspace import Workspace, load_ruleset


@pytest.fixture
def ws(tmp_path: Path) -> Workspace:
    w = Workspace(tmp_path / "home")
    w.seed()
    return w


@pytest.fixture
def store(ws: Workspace):
    s = ws.store()
    yield s
    s.close()


def make_run(ws: Workspace, store, account: str):
    adapter = ws.adapter(account)
    ruleset, label = load_ruleset(adapter.platform)
    return build_plan(diagnose(adapter), ruleset, store, label).run, ruleset


@pytest.fixture
def sa_run(ws, store):
    return make_run(ws, store, SA_ACCOUNT)


@pytest.fixture
def mt_run(ws, store):
    return make_run(ws, store, MT_ACCOUNT)


def executor(ws, store, account, ruleset, failure=None, actor="tester") -> Executor:
    return Executor(ws.adapter(account, failure), store, ruleset.guardrails, actor=actor)


__all__ = ["MT_ACCOUNT", "SA_ACCOUNT", "Platform", "executor", "make_run"]
