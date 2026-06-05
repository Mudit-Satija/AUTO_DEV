import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Settings = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get('/api/auth/me');
        setUser(response.data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div>
      <h2>Settings</h2>
      {user ? (
        <div>
          <p><strong>Email:</strong> {user.email}</p>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <p>No user data available.</p>
      )}
    </div>
  );
};

export default Settings;