import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Categories from './pages/Categories';

function App() {
  return (
    <BrowserRouter>
      <div>
        <nav>
          <Link to="/">Dashboard</Link> | 
          <Link to="/tasks">Tasks</Link> | 
          <Link to="/categories">Categories</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/categories" element={<Categories />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;