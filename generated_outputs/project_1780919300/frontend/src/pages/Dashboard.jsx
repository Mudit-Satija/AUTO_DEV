import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

const Dashboard = () => {
  const [taskStats, setTaskStats] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [tasksResponse, usersResponse] = await Promise.all([
          api.get('/tasks/stats'),
          api.get('/users/stats')
        ]);
        setTaskStats(tasksResponse.data);
        setUserStats(usersResponse.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <h2>Task Statistics</h2>
        <p>Total Tasks: {taskStats?.total || 0}</p>
        <p>Completed: {taskStats?.completed || 0}</p>
        <p>Pending: {taskStats?.pending || 0}</p>
      </div>
      <div>
        <h2>User Statistics</h2>
        <p>Total Users: {userStats?.total || 0}</p>
        <p>Active Users: {userStats?.active || 0}</p>
        <p>Inactive Users: {userStats?.inactive || 0}</p>
      </div>
    </div>
  );
};

export default Dashboard;