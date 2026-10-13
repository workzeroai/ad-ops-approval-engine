"""광고 플랫폼 어댑터."""
from __future__ import annotations

from adops.adapters.base import AdPlatformAdapter
from adops.adapters.fake_platform import (
    ApiError,
    FailureMode,
    FakeAdServer,
    PermanentApiError,
    TransientApiError,
)
from adops.adapters.meta_like import MetaLikeAdapter
from adops.adapters.searchad_like import SearchAdLikeAdapter
from adops.models import Platform

__all__ = [
    "AdPlatformAdapter",
    "ApiError",
    "FailureMode",
    "FakeAdServer",
    "MetaLikeAdapter",
    "PermanentApiError",
    "SearchAdLikeAdapter",
    "TransientApiError",
    "make_adapter",
]


def make_adapter(server: FakeAdServer, account_id: str) -> AdPlatformAdapter:
    platform = Platform(server.account(account_id)["platform"])
    if platform == Platform.SEARCHAD_LIKE:
        return SearchAdLikeAdapter(server, account_id)
    return MetaLikeAdapter(server, account_id)
