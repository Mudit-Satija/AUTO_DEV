import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PendingTasks from './pages/Pendingtasks.jsx';
import CompletedTasks from './pages/Completedtasks.jsx';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PendingTasks />} />
        <Route path="/completed" element={<CompletedTasks />} />
      </Routes>
    </Router>
  );
}

export default App;