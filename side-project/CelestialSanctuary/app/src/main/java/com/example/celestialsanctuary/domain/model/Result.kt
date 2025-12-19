package com.example.celestialsanctuary.domain.model

/**
 * 비동기 작업의 결과를 표현하는 sealed class
 *
 * 사용 예:
 * ```
 * when (result) {
 *     is Result.Success -> showData(result.data)
 *     is Result.Error -> showError(result.message)
 *     is Result.Loading -> showLoading()
 * }
 * ```
 */
sealed class Result<out T> {

    /**
     * 성공 상태 - 데이터를 포함
     */
    data class Success<T>(val data: T) : Result<T>()

    /**
     * 에러 상태 - 에러 메시지와 원본 예외를 포함
     */
    data class Error(
        val message: String,
        val exception: Throwable? = null
    ) : Result<Nothing>()

    /**
     * 로딩 상태
     */
    data object Loading : Result<Nothing>()

    /**
     * 성공 여부 확인
     */
    val isSuccess: Boolean get() = this is Success

    /**
     * 에러 여부 확인
     */
    val isError: Boolean get() = this is Error

    /**
     * 로딩 여부 확인
     */
    val isLoading: Boolean get() = this is Loading

    /**
     * 성공 시 데이터 반환, 아니면 null
     */
    fun getOrNull(): T? = when (this) {
        is Success -> data
        else -> null
    }

    /**
     * 성공 시 데이터 반환, 아니면 기본값
     */
    fun getOrDefault(default: @UnsafeVariance T): T = when (this) {
        is Success -> data
        else -> default
    }

    /**
     * 성공 시 변환 함수 적용
     */
    fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Success -> Success(transform(data))
        is Error -> this
        is Loading -> this
    }

    /**
     * 성공 시 콜백 실행
     */
    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) action(data)
        return this
    }

    /**
     * 에러 시 콜백 실행
     */
    inline fun onError(action: (String, Throwable?) -> Unit): Result<T> {
        if (this is Error) action(message, exception)
        return this
    }

    /**
     * 로딩 시 콜백 실행
     */
    inline fun onLoading(action: () -> Unit): Result<T> {
        if (this is Loading) action()
        return this
    }

    companion object {
        /**
         * 성공 결과 생성
         */
        fun <T> success(data: T): Result<T> = Success(data)

        /**
         * 에러 결과 생성
         */
        fun error(message: String, exception: Throwable? = null): Result<Nothing> =
            Error(message, exception)

        /**
         * 로딩 결과 생성
         */
        fun loading(): Result<Nothing> = Loading

        /**
         * try-catch를 Result로 래핑
         */
        inline fun <T> runCatching(block: () -> T): Result<T> {
            return try {
                Success(block())
            } catch (e: Exception) {
                Error(e.message ?: "Unknown error", e)
            }
        }
    }
}

/**
 * suspend 함수를 Result로 래핑하는 확장 함수
 */
suspend fun <T> Result.Companion.fromSuspend(block: suspend () -> T): Result<T> {
    return try {
        Result.Success(block())
    } catch (e: Exception) {
        Result.Error(e.message ?: "Unknown error", e)
    }
}
