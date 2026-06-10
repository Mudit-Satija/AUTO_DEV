import React, { useState, useEffect } from 'react';
import api from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    activeCustomers: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [productsRes, ordersRes] = await Promise.all([
          api.get('/products'),
          api.get('/orders')
        ]);

        const totalRevenue = ordersRes.data.reduce((sum, order) => sum + order.totalAmount, 0);
        
        setStats({
          totalProducts: productsRes.data.length,
          totalOrders: ordersRes.data.length,
          totalRevenue: totalRevenue.toFixed(2),
          activeCustomers: new Set(ordersRes.data.map(o => o.customerId)).size
        });

        // Mock recent activity from orders
        setRecentActivity(ordersRes.data.slice(-5).map(order => ({
          id: order._id,
          title: `Order #${order.orderNumber}`,
          description: `Customer: ${order.customerName}`,
          date: new Date(order.createdAt).toLocaleDateString()
        })));

        // Mock upcoming items
        setUpcoming([
          { id: 1, title: 'Monthly Inventory Review', date: '2024-01-15' },
          { id: 2, title: 'Supplier Meeting', date: '2024-01-20' },
          { id: 3, title: 'Sales Report Due', date: '2024-01-25' }
        ]);
      } catch (err) {
        setError(err.response?.data?.message || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your shop performance</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p className="stat-value">{stats.totalProducts}</p>
        </div>
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p className="stat-value">{stats.totalOrders}</p>
        </div>
        <div className="stat-card">
          <h3>Total Revenue</h3>
          <p className="stat-value">${stats.totalRevenue}</p>
        </div>
        <div className="stat-card">
          <h3>Active Customers</h3>
          <p className="stat-value">{stats.activeCustomers}</p>
        </div>
      </div>

      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentActivity.length > 0 ? (
            recentActivity.map(activity => (
              <div key={activity.id} className="activity-item">
                <h3 className="activity-title">{activity.title}</h3>
                <p className="activity-meta">{activity.description}</p>
                <p className="activity-meta">{activity.date}</p>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent activity yet.</p>
            </div>
          )}
        </div>
      </div>

      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcoming.map(item => (
            <div key={item.id} className="upcoming-item">
              <h3 className="upcoming-title">{item.title}</h3>
              <p className="upcoming-meta">Due: {new Date(item.date).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;