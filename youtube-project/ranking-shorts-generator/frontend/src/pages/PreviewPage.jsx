import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FaDownload, FaArrowLeft, FaPlay } from 'react-icons/fa'
import Button from '../components/Button'
import LoadingSpinner from '../components/LoadingSpinner'
import { projectsAPI } from '../services/api'

function PreviewPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadProject()
  }, [projectId])

  const loadProject = async () => {
    try {
      const data = await projectsAPI.getById(projectId)

      if (data.status !== 'completed' || !data.final_video) {
        setError('영상이 아직 생성되지 않았습니다')
      } else {
        setProject(data)
      }

      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (project?.final_video?.file_path) {
      // 다운로드 링크 생성
      const downloadUrl = `http://localhost:8000${project.final_video.file_path}`
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = `ranking-shorts-${project.id}.mp4`
      link.click()
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
    else if (bytes < 1073741824) return (bytes / 1048576).toFixed(2) + ' MB'
    else return (bytes / 1073741824).toFixed(2) + ' GB'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" message="프로젝트를 불러오는 중..." />
      </div>
    )
  }

  if (error || !project?.final_video) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8">
          <p className="text-red-700 mb-4">{error || '영상을 찾을 수 없습니다'}</p>
          <Button variant="primary" onClick={() => navigate('/')}>
            홈으로 돌아가기
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            미리보기 & 다운로드
          </h1>
          <p className="text-gray-600">
            생성된 랭킹 쇼츠 영상을 확인하고 다운로드하세요
          </p>
        </div>
        <Button
          variant="outline"
          icon={FaArrowLeft}
          onClick={() => navigate('/')}
        >
          새로운 검색
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Video Player */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {project.title}
            </h2>

            {/* Video */}
            <div className="bg-gray-900 rounded-lg overflow-hidden aspect-[9/16] max-w-md mx-auto">
              <video
                controls
                className="w-full h-full"
                src={`http://localhost:8000${project.final_video.file_path}`}
              >
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Download Button */}
            <div className="mt-6">
              <Button
                variant="primary"
                size="lg"
                icon={FaDownload}
                onClick={handleDownload}
                className="w-full"
              >
                영상 다운로드
              </Button>
            </div>
          </div>
        </div>

        {/* Info Sidebar */}
        <div className="space-y-6">
          {/* Video Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              영상 정보
            </h3>

            <dl className="space-y-3">
              <div>
                <dt className="text-sm text-gray-600">파일 크기</dt>
                <dd className="text-base font-medium text-gray-900">
                  {formatFileSize(project.final_video.file_size)}
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-600">영상 길이</dt>
                <dd className="text-base font-medium text-gray-900">
                  {project.final_video.duration}초
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-600">해상도</dt>
                <dd className="text-base font-medium text-gray-900">
                  1080 x 1920 (9:16)
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-600">포함된 영상</dt>
                <dd className="text-base font-medium text-gray-900">
                  {project.selected_videos?.length || 0}개
                </dd>
              </div>

              <div>
                <dt className="text-sm text-gray-600">생성 시간</dt>
                <dd className="text-base font-medium text-gray-900">
                  {new Date(project.final_video.created_at).toLocaleString('ko-KR')}
                </dd>
              </div>
            </dl>
          </div>

          {/* Original Videos */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              원본 영상 목록
            </h3>

            <div className="space-y-3">
              {project.selected_videos?.map((video, index) => (
                <div
                  key={video.id}
                  className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                    #{index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {video.title || 'No title'}
                    </p>
                    <p className="text-xs text-gray-500">@{video.author}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Usage Tips */}
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              💡 사용 팁
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• YouTube Shorts에 최적화된 9:16 비율입니다</li>
              <li>• 각 영상은 7초로 자동 편집됩니다</li>
              <li>• 랭킹 오버레이가 포함되어 있습니다</li>
              <li>• 배경음악이 자동으로 추가됩니다</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PreviewPage
