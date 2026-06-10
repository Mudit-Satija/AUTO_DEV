import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    pendingOrders: 0
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

        const products = productsRes.data;
        const orders = ordersRes.data;

        const totalRevenue = orders.reduce((sum, order) => sum + order.totalAmount, 0);
        const pendingOrders = orders.filter(order => order.status === 'pending').length;

        setStats({
          totalProducts: products.length,
          totalOrders: orders.length,
          totalRevenue: totalRevenue.toFixed(2),
          pendingOrders: pendingOrders
        });

        // Recent activity: last 5 orders
        const sortedOrders = [...orders].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        setRecentActivity(sortedOrders.slice(0, 5));

        // Upcoming: orders due in next 7 days (assuming delivery date)
        const today = new Date();
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        const upcomingOrders = orders.filter(order => {
          const deliveryDate = new Date(order.deliveryDate || order.createdAt);
          return deliveryDate >= today && deliveryDate <= nextWeek;
        });
        setUpcoming(upcomingOrders.slice(0, 5));

      } catch (err) {
        setError(err.response?.data?.message || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="empty-state"><p>Error: {error}</p></div>;

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
          <h3>Pending Orders</h3>
          <p className="stat-value">{stats.pendingOrders}</p>
        </div>
      </div>

      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentActivity.length > 0 ? (
            recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <p className="activity-title">Order #{activity._id.slice(-6)}</p>
                <p className="activity-meta">
                  {activity.customerName} - {activity.status} - ${activity.totalAmount}
                </p>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent activity</p>
            </div>
          )}
        </div>
      </div>

      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcoming.length > 0 ? (
            upcoming.map((item, index) => (
              <div key={index} className="upcoming-item">
                <p className="upcoming-title">Order #{item._id.slice(-6)}</p>
                <p className="upcoming-meta">
                  Delivery: {new Date(item.deliveryDate || item.createdAt).toLocaleDateString()}
                </p>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming orders</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}