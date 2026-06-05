import api from '../services/api';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [stats, setStats] = useState({});

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome to the admin dashboard.</p>
      <div>
        <strong>Total Users:</strong> {stats.totalUsers || 'Loading...'}
      </div>
      <div>
        <strong>Total Orders:</strong> {stats.totalOrders || 'Loading...'}
      </div>
      <div>
        <strong>Total Products:</strong> {stats.totalProducts || 'Loading...'}
      </div>
    </div>
  );
}