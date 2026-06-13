import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({});
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [upcomingBills, setUpcomingBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/dashboard');
        setMetrics(res.data.metrics);
        setRecentTransactions(res.data.recentTransactions);
        setUpcomingBills(res.data.upcomingBills);
        setError('');
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Balance</h3>
          <p className="stat-value">${metrics.totalBalance?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Expenses</h3>
          <p className="stat-value">${metrics.monthlyExpenses?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Income</h3>
          <p className="stat-value">${metrics.monthlyIncome?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions This Month</h3>
          <p className="stat-value">{metrics.monthlyTransactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentTransactions.length === 0 ? (
            <div className="empty-state">
              <p>No recent transactions.</p>
            </div>
          ) : (
            recentTransactions.map((transaction) => (
              <div key={transaction._id} className="activity-item">
                <div className="activity-title">
                  {transaction.description} - ${transaction.amount.toFixed(2)}
                </div>
                <div className="activity-meta">
                  {new Date(transaction.date).toLocaleDateString()} • {transaction.category}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcomingBills.length === 0 ? (
            <div className="empty-state">
              <p>No upcoming bills or payments.</p>
            </div>
          ) : (
            upcomingBills.map((bill) => (
              <div key={bill._id} className="upcoming-item">
                <div className="upcoming-title">{bill.description}</div>
                <div className="upcoming-meta">
                  Due: {new Date(bill.dueDate).toLocaleDateString()} • ${bill.amount.toFixed(2)}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;