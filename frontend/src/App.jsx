import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import DecisionDetailPage from './pages/DecisionDetailPage';
import RecordDetailPage from './pages/RecordDetailPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ProjectsPage />} />
        <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        <Route path="/decisions/:decisionId" element={<DecisionDetailPage />} />
        <Route path="/records/:recordId" element={<RecordDetailPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
