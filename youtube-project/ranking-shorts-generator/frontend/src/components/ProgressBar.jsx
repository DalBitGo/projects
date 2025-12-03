import clsx from 'clsx'

function ProgressBar({ progress = 0, message = '', status = 'processing' }) {
  const statusColors = {
    processing: 'bg-primary-600',
    completed: 'bg-green-600',
    failed: 'bg-red-600',
    idle: 'bg-gray-400',
  }

  return (
    <div className="w-full">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={clsx(
            'h-full rounded-full transition-all duration-500 ease-out',
            statusColors[status]
          )}
          style={{ width: `${Math.min(progress, 100)}%` }}
        >
          {status === 'processing' && (
            <div className="h-full w-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse" />
          )}
        </div>
      </div>

      {/* Info */}
      <div className="flex items-center justify-between mt-2">
        <span className="text-sm text-gray-600">{message}</span>
        <span className="text-sm font-medium text-gray-900">
          {Math.round(progress)}%
        </span>
      </div>
    </div>
  )
}

export default ProgressBar
