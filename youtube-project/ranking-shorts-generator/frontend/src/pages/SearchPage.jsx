import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FaSearch, FaHashtag } from 'react-icons/fa'
import Button from '../components/Button'
import LoadingSpinner from '../components/LoadingSpinner'
import { searchAPI } from '../services/api'
import useStore from '../store/useStore'

function SearchPage() {
  const navigate = useNavigate()
  const { addSearch, setSearchLoading, searchLoading } = useStore()

  const [keyword, setKeyword] = useState('')
  const [limit, setLimit] = useState(30)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    setError('')

    if (!keyword.trim()) {
      setError('키워드를 입력해주세요')
      return
    }

    try {
      setSearchLoading(true)

      const result = await searchAPI.create(keyword.trim(), limit)
      addSearch(result)

      // 검색 결과 페이지로 이동
      navigate(`/select/${result.id}`)
    } catch (err) {
      setError(err.message || '검색 중 오류가 발생했습니다')
    } finally {
      setSearchLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl mb-4">
          <FaSearch className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          TikTok 영상 검색
        </h1>
        <p className="text-lg text-gray-600">
          인기 TikTok 영상을 검색하고 랭킹 쇼츠를 만들어보세요
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <form onSubmit={handleSearch} className="space-y-6">
          {/* Keyword Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              검색 키워드
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaHashtag className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="예: football, skills, goals"
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={searchLoading}
              />
            </div>
            <p className="mt-2 text-sm text-gray-500">
              TikTok 해시태그를 입력하세요 (# 없이 입력)
            </p>
          </div>

          {/* Limit Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              검색 결과 수
            </label>
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={searchLoading}
            >
              <option value={20}>20개</option>
              <option value={30}>30개 (권장)</option>
              <option value={50}>50개</option>
              <option value={100}>100개</option>
            </select>
            <p className="mt-2 text-sm text-gray-500">
              더 많은 결과를 검색할수록 시간이 오래 걸립니다
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={searchLoading}
            disabled={searchLoading}
            icon={FaSearch}
            className="w-full"
          >
            {searchLoading ? '검색 중...' : '검색 시작'}
          </Button>
        </form>

        {/* Loading State */}
        {searchLoading && (
          <div className="mt-8 p-6 bg-gray-50 rounded-lg">
            <LoadingSpinner size="md" message="TikTok 영상을 검색하고 있습니다..." />
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">
                검색 결과가 많을수록 시간이 오래 걸릴 수 있습니다
              </p>
              <p className="text-xs text-gray-500 mt-1">
                평균 30초 ~ 2분 소요
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-2">🔍</div>
          <h3 className="font-semibold text-gray-900 mb-2">1. 검색</h3>
          <p className="text-sm text-gray-600">
            키워드로 인기 TikTok 영상을 자동으로 검색합니다
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-2">✅</div>
          <h3 className="font-semibold text-gray-900 mb-2">2. 선택</h3>
          <p className="text-sm text-gray-600">
            검색 결과에서 원하는 영상을 5~7개 선택합니다
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-3xl mb-2">🎬</div>
          <h3 className="font-semibold text-gray-900 mb-2">3. 생성</h3>
          <p className="text-sm text-gray-600">
            랭킹 오버레이가 포함된 쇼츠 영상을 자동으로 생성합니다
          </p>
        </div>
      </div>
    </div>
  )
}

export default SearchPage
