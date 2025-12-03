import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FaPlay, FaEye } from 'react-icons/fa'
import Button from '../components/Button'
import ProgressBar from '../components/ProgressBar'
import LoadingSpinner from '../components/LoadingSpinner'
import { projectsAPI } from '../services/api'
import wsService from '../services/websocket'
import useStore from '../store/useStore'

function GeneratePage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const {
    generationProgress,
    generationStatus,
    generationMessage,
    updateGenerationState,
    resetGeneration,
  } = useStore()

  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [taskId, setTaskId] = useState(null)

  useEffect(() => {
    loadProject()

    return () => {
      if (taskId) {
        wsService.unsubscribeTask(taskId)
      }
    }
  }, [projectId])

  const loadProject = async () => {
    try {
      const data = await projectsAPI.getById(projectId)
      setProject(data)
      setLoading(false)

      // 이미 생성이 진행 중이거나 완료된 경우
      if (data.status === 'processing' || data.status === 'queued') {
        // 작업 상태 모니터링
        monitorProgress()
      } else if (data.status === 'completed') {
        updateGenerationState({
          progress: 100,
          status: 'completed',
          message: '영상 생성이 완료되었습니다!',
        })
      }
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    try {
      setError('')
      resetGeneration()

      const result = await projectsAPI.generate(projectId)
      setTaskId(result.task_id)

      updateGenerationState({
        status: 'processing',
        message: '영상 생성을 시작합니다...',
      })

      // WebSocket으로 실시간 진행 상황 모니터링
      wsService.connect()
      wsService.subscribeTask(result.task_id, handleTaskUpdate)

      // 폴링으로도 백업
      monitorProgress()
    } catch (err) {
      setError(err.message)
      updateGenerationState({
        status: 'failed',
        message: err.message,
      })
    }
  }

  const handleTaskUpdate = (data) => {
    const { state, info } = data

    if (state === 'PROGRESS') {
      updateGenerationState({
        progress: info.percent || 0,
        status: 'processing',
        message: info.status || '처리 중...',
      })
    } else if (state === 'SUCCESS') {
      updateGenerationState({
        progress: 100,
        status: 'completed',
        message: '영상 생성이 완료되었습니다!',
      })
      loadProject() // 프로젝트 정보 갱신
    } else if (state === 'FAILURE') {
      updateGenerationState({
        status: 'failed',
        message: '영상 생성에 실패했습니다',
      })
    }
  }

  const monitorProgress = async () => {
    const checkProgress = async () => {
      try {
        const status = await projectsAPI.getStatus(projectId)

        if (status.status === 'processing') {
          updateGenerationState({
            progress: status.render_progress || 0,
            status: 'processing',
            message: status.task_info?.status || '처리 중...',
          })

          setTimeout(checkProgress, 2000)
        } else if (status.status === 'completed') {
          updateGenerationState({
            progress: 100,
            status: 'completed',
            message: '영상 생성이 완료되었습니다!',
          })
          loadProject()
        } else if (status.status === 'failed') {
          updateGenerationState({
            status: 'failed',
            message: status.error_message || '영상 생성에 실패했습니다',
          })
        }
      } catch (err) {
        console.error('Progress check failed:', err)
      }
    }

    checkProgress()
  }

  const handleViewPreview = () => {
    navigate(`/preview/${projectId}`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" message="프로젝트를 불러오는 중..." />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          랭킹 영상 생성
        </h1>
        <p className="text-gray-600">
          선택한 영상으로 랭킹 쇼츠를 생성합니다
        </p>
      </div>

      {/* Project Info */}
      {project && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            {project.title}
          </h2>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-sm text-gray-600">선택된 영상</p>
              <p className="text-2xl font-bold text-gray-900">
                {project.selected_videos?.length || 0}개
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">예상 영상 길이</p>
              <p className="text-2xl font-bold text-gray-900">
                {(project.selected_videos?.length || 0) * 7}초
              </p>
            </div>
          </div>

          {/* Selected Videos Preview */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              선택된 영상 미리보기
            </h3>
            <div className="grid grid-cols-5 gap-3">
              {project.selected_videos?.map((video, index) => (
                <div key={video.id} className="relative">
                  <img
                    src={video.thumbnail_url}
                    alt={`Video ${index + 1}`}
                    className="w-full aspect-[9/16] object-cover rounded-lg"
                  />
                  <div className="absolute top-1 left-1 bg-black/70 text-white text-xs px-2 py-1 rounded">
                    #{index + 1}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Generation Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        {generationStatus === 'idle' && (
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              영상 생성을 시작하시겠습니까?
            </h3>
            <p className="text-gray-600 mb-6">
              선택한 영상들을 다운로드하고, 랭킹 오버레이를 추가한 후, 하나의 영상으로 합칩니다.
              <br />
              완료까지 약 3~5분 정도 소요됩니다.
            </p>
            <Button
              variant="primary"
              size="lg"
              icon={FaPlay}
              onClick={handleGenerate}
            >
              영상 생성 시작
            </Button>
          </div>
        )}

        {(generationStatus === 'processing' || generationStatus === 'queued') && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              영상 생성 중...
            </h3>
            <ProgressBar
              progress={generationProgress}
              message={generationMessage}
              status={generationStatus}
            />
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                생성이 완료될 때까지 기다려주세요
              </p>
              <p className="text-xs text-gray-500 mt-1">
                페이지를 새로고침해도 진행 상황이 유지됩니다
              </p>
            </div>
          </div>
        )}

        {generationStatus === 'completed' && (
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <FaEye className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              생성 완료!
            </h3>
            <p className="text-gray-600 mb-6">
              랭킹 쇼츠 영상이 성공적으로 생성되었습니다
            </p>
            <Button
              variant="primary"
              size="lg"
              icon={FaEye}
              onClick={handleViewPreview}
            >
              미리보기 & 다운로드
            </Button>
          </div>
        )}

        {generationStatus === 'failed' && (
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
              <span className="text-3xl">❌</span>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              생성 실패
            </h3>
            <p className="text-red-600 mb-6">{generationMessage}</p>
            <Button variant="primary" size="lg" onClick={handleGenerate}>
              다시 시도
            </Button>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
    </div>
  )
}

export default GeneratePage
