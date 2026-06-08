import { BrowserRouter, Routes, Route, Navigate, Link, Outlet } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Categories from './pages/Categories';
import Login from './pages/Login';
import Register from './pages/Register';

const PrivateRoute = () => {
  return <Outlet />;
};

const App = () => {
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  return (
    <BrowserRouter>
      <div>
        <nav style={{ padding: '10px', backgroundColor: '#f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Link to="/">Home</Link>
            <Link to="/dashboard" style={{ marginLeft: '10px' }}>Dashboard</Link>
            <Link to="/tasks" style={{ marginLeft: '10px' }}>Tasks</Link>
            <Link to="/categories" style={{ marginLeft: '10px' }}>Categories</Link>
            <Link to="/login" style={{ marginLeft: '10px' }}>Login</Link>
            <Link to="/register" style={{ marginLeft: '10px' }}>Register</Link>
          </div>
        </nav>

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<PrivateRoute />}>
            <Route index element={<Dashboard />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="tasks" element={<Tasks />} />
            <Route path="categories" element={<Categories />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;