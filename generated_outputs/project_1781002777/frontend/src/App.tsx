import './App.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import CourseDetails from './pages/CourseDetails';
import Assignments from './pages/Assignments';
import Calendar from './pages/Calendar';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-indigo-600 text-white shadow-md">
          <div className="container mx-auto px-4 py-3 flex space-x-6">
            <Link to="/" className="hover:text-indigo-200 transition-colors">Dashboard</Link>
            <Link to="/courses" className="hover:text-indigo-200 transition-colors">Courses</Link>
            <Link to="/assignments" className="hover:text-indigo-200 transition-colors">Assignments</Link>
            <Link to="/calendar" className="hover:text-indigo-200 transition-colors">Calendar</Link>
          </div>
        </nav>

        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/courses/:id" element={<CourseDetails />} />
            <Route path="/assignments" element={<Assignments />} />
            <Route path="/calendar" element={<Calendar />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;