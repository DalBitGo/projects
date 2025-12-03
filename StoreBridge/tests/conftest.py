"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock


@pytest_asyncio.fixture
async def redis_mock():
    """Redis mock with eval support."""
    redis = AsyncMock()
    redis.script_load = AsyncMock(return_value="mock_sha")
    redis.evalsha = AsyncMock()
    redis.get = AsyncMock()
    redis.delete = AsyncMock()
    redis.close = AsyncMock()
    return redis


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setattr("app.config.settings.naver_max_tps", 2)
    monkeypatch.setattr("app.config.settings.naver_burst_max", 3)
    monkeypatch.setattr("app.config.settings.redis_url", "redis://localhost:6379/1")
