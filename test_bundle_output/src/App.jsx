import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { BrowserRouter } from 'react-router-dom';

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({
          id: payload.sub,
          email: payload.email,
          role: payload.role
        });
      } catch (err) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    localStorage.setItem('token', userData.token);
    setUser({
      id: userData.id,
      email: userData.email,
      role: userData.role
    });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div className="App">
        <header>
          <h1>React JWT App</h1>
          {user ? (
            <button onClick={logout}>Logout</button>
          ) : (
            <Navigate to="/login" />
          )}
        </header>
        <main>
          <Routes>
            <Route path="/login" element={<Login onLogin={login} />} />
            <Route path="/dashboard" element={user ? <Dashboard user={user} /> : <Navigate to="/login" />} />
            <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (response.ok) {
      onLogin(data);
    } else {
      alert(data.message || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
    </form>
  );
};

const Dashboard = ({ user }) => {
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, {user.email}!</p>
      <p>Role: {user.role}</p>
    </div>
  );
};

export default App;