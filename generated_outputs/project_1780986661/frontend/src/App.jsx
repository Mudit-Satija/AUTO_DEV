import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import CreateTask from './pages/CreateTask';
import TaskDetails from './pages/TaskDetails';
import CompletedTasks from './pages/CompletedTasks';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/create" element={<CreateTask />} />
        <Route path="/task/:id" element={<TaskDetails />} />
        <Route path="/completed" element={<CompletedTasks />} />
      </Routes>
    </Router>
  );
}

export default App;