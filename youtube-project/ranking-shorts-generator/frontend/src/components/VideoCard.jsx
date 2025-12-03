import { FaHeart, FaEye, FaComment, FaShare, FaCheckCircle } from 'react-icons/fa'
import clsx from 'clsx'

function VideoCard({ video, selected = false, onSelect, showStats = true }) {
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`
    }
    return num
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div
      className={clsx(
        'relative bg-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden cursor-pointer group',
        selected && 'ring-2 ring-primary-500'
      )}
      onClick={onSelect}
    >
      {/* Thumbnail */}
      <div className="relative aspect-[9/16] bg-gray-200">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />

        {/* Duration */}
        <div className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
          {formatDuration(video.duration)}
        </div>

        {/* Selected indicator */}
        {selected && (
          <div className="absolute top-2 right-2 bg-primary-500 text-white rounded-full p-1">
            <FaCheckCircle className="w-5 h-5" />
          </div>
        )}

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
      </div>

      {/* Info */}
      <div className="p-3">
        <h3 className="text-sm font-medium text-gray-900 line-clamp-2 mb-2">
          {video.title || 'No title'}
        </h3>

        <p className="text-xs text-gray-600 mb-2">@{video.author}</p>

        {showStats && (
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            <div className="flex items-center space-x-1">
              <FaEye className="w-3 h-3" />
              <span>{formatNumber(video.views)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <FaHeart className="w-3 h-3 text-red-500" />
              <span>{formatNumber(video.likes)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <FaComment className="w-3 h-3" />
              <span>{formatNumber(video.comments)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <FaShare className="w-3 h-3" />
              <span>{formatNumber(video.shares)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default VideoCard
