import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FaArrowRight, FaCheckCircle, FaSpinner } from 'react-icons/fa'
import Button from '../components/Button'
import VideoCard from '../components/VideoCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { searchAPI, projectsAPI, videosAPI } from '../services/api'
import useStore from '../store/useStore'

function SelectPage() {
  const { searchId } = useParams()
  const navigate = useNavigate()

  const {
    videos,
    setVideos,
    selectedVideos,
    toggleVideoSelection,
    clearSelectedVideos,
    setVideosLoading,
    videosLoading,
  } = useStore()

  const [search, setSearch] = useState(null)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadSearchResults()
  }, [searchId])

  const loadSearchResults = async () => {
    try {
      setVideosLoading(true)

      // 검색 상태 확인 (폴링)
      const checkStatus = async () => {
        const statusData = await searchAPI.getStatus(searchId)

        if (statusData.status === 'processing') {
          // 아직 진행 중이면 2초 후 다시 체크
          setTimeout(checkStatus, 2000)
        } else if (statusData.status === 'completed') {
          // 완료되면 결과 로드
          const result = await searchAPI.getById(searchId)
          setSearch(result)
          setVideos(result.videos)
          setVideosLoading(false)
        } else if (statusData.status === 'failed') {
          setError('검색에 실패했습니다: ' + statusData.error_message)
          setVideosLoading(false)
        }
      }

      checkStatus()
    } catch (err) {
      setError(err.message)
      setVideosLoading(false)
    }
  }

  const handleCreateProject = async () => {
    if (selectedVideos.length < 3) {
      setError('최소 3개 이상의 영상을 선택해주세요')
      return
    }

    if (selectedVideos.length > 10) {
      setError('최대 10개까지 선택 가능합니다')
      return
    }

    try {
      setCreating(true)
      setError('')

      // 1. 프로젝트 생성
      const project = await projectsAPI.create(
        `Ranking - ${search.keyword}`,
        `${search.keyword} 랭킹 쇼츠`
      )

      // 2. 선택된 영상 추가
      const videoIds = selectedVideos.map((v) => v.id)
      await projectsAPI.addVideos(project.id, videoIds)

      // 3. 영상 다운로드 시작
      await videosAPI.downloadBatch(videoIds)

      // 4. 생성 페이지로 이동
      clearSelectedVideos()
      navigate(`/generate/${project.id}`)
    } catch (err) {
      setError(err.message || '프로젝트 생성 중 오류가 발생했습니다')
    } finally {
      setCreating(false)
    }
  }

  if (videosLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" message="검색 결과를 불러오는 중..." />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          영상 선택
        </h1>
        <p className="text-gray-600">
          랭킹 쇼츠에 사용할 영상을 선택하세요 (3~10개)
        </p>
      </div>

      {/* Search Info */}
      {search && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">검색 키워드</p>
              <p className="text-lg font-semibold text-gray-900">
                #{search.keyword}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">검색 결과</p>
              <p className="text-lg font-semibold text-gray-900">
                {videos.length}개
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Selection Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6 sticky top-20 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FaCheckCircle className="w-5 h-5 text-primary-600" />
            <span className="font-medium text-gray-900">
              {selectedVideos.length}개 선택됨
            </span>
            <span className="text-sm text-gray-500">
              (최소 3개, 최대 10개)
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {selectedVideos.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => clearSelectedVideos()}
              >
                선택 초기화
              </Button>
            )}

            <Button
              variant="primary"
              size="md"
              onClick={handleCreateProject}
              disabled={selectedVideos.length < 3 || creating}
              loading={creating}
              icon={FaArrowRight}
            >
              {creating ? '프로젝트 생성 중...' : '다음 단계로'}
            </Button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Video Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {videos.map((video) => (
          <VideoCard
            key={video.id}
            video={video}
            selected={selectedVideos.some((v) => v.id === video.id)}
            onSelect={() => toggleVideoSelection(video)}
          />
        ))}
      </div>

      {/* Empty State */}
      {videos.length === 0 && !videosLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">검색 결과가 없습니다</p>
        </div>
      )}
    </div>
  )
}

export default SelectPage
