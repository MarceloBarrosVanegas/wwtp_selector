import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Gantt from './pages/Gantt'
import MapView from './pages/MapView'
import Charts from './pages/Charts'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/gantt" element={<Gantt />} />
        <Route path="/map" element={<MapView />} />
        <Route path="/charts" element={<Charts />} />
      </Routes>
    </Layout>
  )
}

export default App
