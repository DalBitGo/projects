"""Rate limiter unit tests."""

import asyncio

import pytest

from app.services.rate_limiter import NaverRateLimiter


@pytest.mark.unit
class TestNaverRateLimiter:
    """Test Naver API Rate Limiter (2 TPS constraint)."""

    @pytest.mark.asyncio
    async def test_acquire_success_within_limit(self, redis_mock):
        """2 TPS 이내 요청은 성공."""
        redis_mock.evalsha.return_value = 1  # Lua script returns 1 (success)

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2)
        result = await limiter.acquire()

        assert result is True
        redis_mock.evalsha.assert_called_once()

    @pytest.mark.asyncio
    async def test_acquire_blocked_over_limit(self, redis_mock):
        """2 TPS 초과 요청은 차단."""
        redis_mock.evalsha.return_value = 0  # Lua script returns 0 (blocked)

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2)
        result = await limiter.acquire()

        assert result is False
        redis_mock.evalsha.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_acquire_no_race_condition(self, redis_mock):
        """동시 요청 시 Race Condition 없음 (Lua atomic)."""
        call_count = 0

        async def mock_evalsha(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return 1  # First 2 succeed
            else:
                return 0  # Rest blocked

        redis_mock.evalsha.side_effect = mock_evalsha

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2)

        # 10개 동시 요청 (max_tps=2이므로 2개만 성공해야 함)
        tasks = [limiter.acquire() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        assert success_count == 2, "Only 2 requests should succeed"
        assert redis_mock.evalsha.call_count == 10

    @pytest.mark.asyncio
    async def test_burst_max_allows_temporary_spike(self, redis_mock):
        """Burst Max는 일시적 스파이크 허용 (3 TPS)."""
        call_count = 0

        async def mock_evalsha(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:  # Burst allows 3
                return 2 if call_count == 3 else 1  # 3rd returns 2 (burst mode)
            else:
                return 0

        redis_mock.evalsha.side_effect = mock_evalsha

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2, burst_max=3)

        tasks = [limiter.acquire() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        assert sum(results) == 3, "Burst allows 3 requests temporarily"

    @pytest.mark.asyncio
    async def test_lua_script_loaded_once(self, redis_mock):
        """Lua 스크립트는 한 번만 로드."""
        redis_mock.evalsha.return_value = 1

        limiter = NaverRateLimiter(redis_client=redis_mock)

        # 3번 호출
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()

        # script_load는 한 번만 호출되어야 함
        assert redis_mock.script_load.call_count == 1

    @pytest.mark.asyncio
    async def test_acquire_with_wait_retries_on_failure(self, redis_mock):
        """acquire_with_wait는 실패 시 재시도."""
        call_count = 0

        async def mock_evalsha(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return 0  # First 2 calls fail
            else:
                return 1  # 3rd call succeeds

        redis_mock.evalsha.side_effect = mock_evalsha

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2)

        result = await limiter.acquire_with_wait(max_retries=3, backoff=0.01)

        assert result is True
        assert redis_mock.evalsha.call_count == 3

    @pytest.mark.asyncio
    async def test_acquire_with_wait_fails_after_max_retries(self, redis_mock):
        """acquire_with_wait는 max_retries 초과 시 실패."""
        redis_mock.evalsha.return_value = 0  # Always blocked

        limiter = NaverRateLimiter(redis_client=redis_mock, max_tps=2)

        result = await limiter.acquire_with_wait(max_retries=3, backoff=0.01)

        assert result is False
        assert redis_mock.evalsha.call_count == 3

    @pytest.mark.asyncio
    async def test_get_current_count_returns_count(self, redis_mock):
        """get_current_count는 현재 카운트 반환."""
        redis_mock.get.return_value = "5"

        limiter = NaverRateLimiter(redis_client=redis_mock)

        count = await limiter.get_current_count()

        assert count == 5
        redis_mock.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_count_returns_zero_when_empty(self, redis_mock):
        """get_current_count는 키가 없으면 0 반환."""
        redis_mock.get.return_value = None

        limiter = NaverRateLimiter(redis_client=redis_mock)

        count = await limiter.get_current_count()

        assert count == 0

    @pytest.mark.asyncio
    async def test_reset_deletes_key(self, redis_mock):
        """reset은 Redis 키 삭제."""
        limiter = NaverRateLimiter(redis_client=redis_mock)

        await limiter.reset()

        redis_mock.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_connection_error_raises_exception(self, redis_mock):
        """Redis 연결 오류 시 예외 발생."""
        redis_mock.evalsha.side_effect = ConnectionError("Redis unavailable")

        limiter = NaverRateLimiter(redis_client=redis_mock)

        with pytest.raises(ConnectionError, match="Redis unavailable"):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_lua_script_error_raises_exception(self, redis_mock):
        """Lua 스크립트 오류 시 예외 발생."""
        redis_mock.evalsha.side_effect = Exception("Lua script error")

        limiter = NaverRateLimiter(redis_client=redis_mock)

        with pytest.raises(Exception, match="Rate limiter error"):
            await limiter.acquire()

    @pytest.mark.asyncio
    async def test_close_closes_redis_connection(self, redis_mock):
        """close는 Redis 연결 종료."""
        limiter = NaverRateLimiter(redis_client=redis_mock)

        await limiter.close()

        redis_mock.close.assert_called_once()
