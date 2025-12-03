import { FaBars, FaVideo } from 'react-icons/fa'

function Header({ onMenuClick }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            <FaBars className="w-5 h-5 text-gray-600" />
          </button>

          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-primary-500 to-secondary-500 p-2 rounded-lg">
              <FaVideo className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Ranking Shorts Generator
              </h1>
              <p className="text-xs text-gray-500">
                TikTok 랭킹 쇼츠 자동 생성기
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">
            v1.0.0
          </span>
        </div>
      </div>
    </header>
  )
}

export default Header
