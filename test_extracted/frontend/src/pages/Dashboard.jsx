import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

const Dashboard = () => {
  const [taskStats, setTaskStats] = useState({});
  const [userStats, setUserStats] = useState({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const taskResponse = await api.get('/tasks/stats');
        const userResponse = await api.get('/users/stats');
        setTaskStats(taskResponse.data);
        setUserStats(userResponse.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <h2>Task Statistics</h2>
        <p>Total Tasks: {taskStats.total || 0}</p>
        <p>Completed: {taskStats.completed || 0}</p>
        <p>Pending: {taskStats.pending || 0}</p>
      </div>
      <div>
        <h2>User Statistics</h2>
        <p>Total Users: {userStats.total || 0}</p>
        <p>Active Users: {userStats.active || 0}</p>
      </div>
    </div>
  );
};

export default Dashboard;