import React from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get('/dashboard');
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
      <p>Welcome to the dashboard!</p>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
};

export default Dashboard;