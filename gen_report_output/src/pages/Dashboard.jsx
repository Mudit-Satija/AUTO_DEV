import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await api.get('/api/dashboard');
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <p>Loading dashboard...</p>;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome to the admin dashboard.</p>
      {data && (
        <div>
          <p>Total Posts: {data.totalPosts}</p>
          <p>Total Inventory Items: {data.totalInventory}</p>
          <p>Total Roles: {data.totalRoles}</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;