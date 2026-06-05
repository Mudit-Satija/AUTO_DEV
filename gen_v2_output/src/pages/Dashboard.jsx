import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome to the admin dashboard.</p>
      <div>
        <strong>Posts:</strong> {stats.posts || 'Loading...'}<br />
        <strong>Inventory Items:</strong> {stats.inventory || 'Loading...'}<br />
        <strong>Roles:</strong> {stats.roles || 'Loading...'}
      </div>
    </div>
  );
};

export default Dashboard;