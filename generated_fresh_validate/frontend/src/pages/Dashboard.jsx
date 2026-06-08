import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    tasks: {},
    categories: {},
    users: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [tasksResponse, categoriesResponse, usersResponse] = await Promise.all([
          api.get('/tasks/stats'),
          api.get('/categories/stats'),
          api.get('/users/stats')
        ]);

        setStats({
          tasks: tasksResponse.data,
          categories: categoriesResponse.data,
          users: usersResponse.data
        });
      } catch (err) {
        setError('Failed to fetch statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <h2>Tasks</h2>
          <p>Total: {stats.tasks.total || 0}</p>
          <p>Completed: {stats.tasks.completed || 0}</p>
          <p>Pending: {stats.tasks.pending || 0}</p>
        </div>
        <div className="stat-card">
          <h2>Categories</h2>
          <p>Total: {stats.categories.total || 0}</p>
          <p>Active: {stats.categories.active || 0}</p>
          <p>Inactive: {stats.categories.inactive || 0}</p>
        </div>
        <div className="stat-card">
          <h2>Users</h2>
          <p>Total: {stats.users.total || 0}</p>
          <p>Active: {stats.users.active || 0}</p>
          <p>Inactive: {stats.users.inactive || 0}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;