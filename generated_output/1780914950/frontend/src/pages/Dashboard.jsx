import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const Dashboard = () => {
  const [taskStats, setTaskStats] = useState({});
  const [categoryStats, setCategoryStats] = useState({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const taskResponse = await api.get('/tasks/stats');
        setTaskStats(taskResponse.data);

        const categoryResponse = await api.get('/categories/stats');
        setCategoryStats(categoryResponse.data);
      } catch (error) {
        console.error('Failed to fetch stats', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
      <div style={{ marginBottom: '2rem' }}>
        <h2>Task Statistics</h2>
        <p>Total Tasks: {taskStats.total || 0}</p>
        <p>Completed: {taskStats.completed || 0}</p>
        <p>Pending: {taskStats.pending || 0}</p>
      </div>
      <div>
        <h2>Category Statistics</h2>
        <p>Total Categories: {categoryStats.total || 0}</p>
        <p>Tasks per Category: {categoryStats.tasksPerCategory ? JSON.stringify(categoryStats.tasksPerCategory) : 'N/A'}</p>
      </div>
    </div>
  );
};

export default Dashboard;