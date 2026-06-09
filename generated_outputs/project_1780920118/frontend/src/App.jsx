import { Routes, Route, Link, Navigate } from 'react-router-dom';
import PendingTasks from './pages/Pending-tasks.jsx';
import CompletedTasks from './pages/Completed-tasks.jsx';

function App() {
  return (
    <>
      <nav>
        <Link to="/pending-tasks">Pending Tasks</Link>
        <Link to="/completed-tasks">Completed Tasks</Link>
      </nav>
      <Routes>
        <Route path="/pending-tasks" element={<PendingTasks />} />
        <Route path="/completed-tasks" element={<CompletedTasks />} />
        <Route path="/" element={<Navigate to="/pending-tasks" />} />
      </Routes>
    </>
  );
}

export default App;