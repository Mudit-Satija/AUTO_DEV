import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/api/dashboard');
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading dashboard...</p>;

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome to the dashboard.</p>
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