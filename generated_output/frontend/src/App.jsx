import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Categories from './pages/Categories';

function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: '20px' }}>
        <nav style={{ marginBottom: '20px', borderBottom: '1px solid #ccc' }}>
          <Link to="/" style={{ marginRight: '20px', textDecoration: 'none', color: '#333' }}>
            Dashboard
          </Link>
          <Link to="/tasks" style={{ marginRight: '20px', textDecoration: 'none', color: '#333' }}>
            Tasks
          </Link>
          <Link to="/categories" style={{ textDecoration: 'none', color: '#333' }}>
            Categories
          </Link>
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