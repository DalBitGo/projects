import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SearchPage from './pages/SearchPage'
import SelectPage from './pages/SelectPage'
import GeneratePage from './pages/GeneratePage'
import PreviewPage from './pages/PreviewPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/select/:searchId" element={<SelectPage />} />
          <Route path="/generate/:projectId" element={<GeneratePage />} />
          <Route path="/preview/:projectId" element={<PreviewPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
