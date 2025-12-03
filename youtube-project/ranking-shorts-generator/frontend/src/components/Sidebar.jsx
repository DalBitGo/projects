import { NavLink } from 'react-router-dom'
import { FaSearch, FaCheckSquare, FaVideo, FaEye, FaHistory } from 'react-icons/fa'

function Sidebar({ isOpen }) {
  const navItems = [
    {
      path: '/',
      icon: FaSearch,
      label: '검색',
      description: 'TikTok 영상 검색',
    },
    {
      path: '/history',
      icon: FaHistory,
      label: '검색 이력',
      description: '이전 검색 결과',
    },
  ]

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white border-r border-gray-200 transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-0 -translate-x-full'
      }`}
    >
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <div className="flex-1">
              <div className="text-sm font-medium">{item.label}</div>
              <div className="text-xs text-gray-500">{item.description}</div>
            </div>
          </NavLink>
        ))}

        <div className="pt-4 mt-4 border-t border-gray-200">
          <div className="px-4 py-2">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              워크플로우
            </h3>
          </div>
          <div className="space-y-1 px-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FaSearch className="w-4 h-4" />
              <span>1. 검색</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FaCheckSquare className="w-4 h-4" />
              <span>2. 선택</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FaVideo className="w-4 h-4" />
              <span>3. 생성</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FaEye className="w-4 h-4" />
              <span>4. 미리보기</span>
            </div>
          </div>
        </div>
      </nav>
    </aside>
  )
}

export default Sidebar
