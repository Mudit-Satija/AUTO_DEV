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
        const [metricsRes, transactionsRes, billsRes] = await Promise.all([
          api.get('/api/dashboard/metrics'),
          api.get('/api/transactions?limit=5&sort=-date'),
          api.get('/api/budgets?upcoming=true')
        ]);
        setMetrics(metricsRes.data);
        setRecentTransactions(transactionsRes.data);
        setUpcomingBills(billsRes.data);
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
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Balance</h3>
          <p className="stat-value">${metrics.balance?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Spent This Month</h3>
          <p className="stat-value">${metrics.monthlySpent?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Income This Month</h3>
          <p className="stat-value">${metrics.monthlyIncome?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Upcoming Bills</h3>
          <p className="stat-value">{metrics.upcomingBillsCount || 0}</p>
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
            recentTransactions.map(transaction => (
              <div key={transaction._id} className="activity-item">
                <div className="activity-title">{transaction.description}</div>
                <div className="activity-meta">
                  <span className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>
                    {transaction.type === 'expense' ? '-' : '+'}${transaction.amount.toFixed(2)}
                  </span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                  <span className="badge badge-info">{transaction.category?.name || 'Uncategorized'}</span>
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
              <p>No upcoming bills or budgets.</p>
            </div>
          ) : (
            upcomingBills.map(budget => (
              <div key={budget._id} className="upcoming-item">
                <div className="upcoming-title">{budget.category?.name || 'Unknown'}</div>
                <div className="upcoming-meta">
                  <span className="stat-value">${budget.amount.toFixed(2)}</span>
                  <span>{new Date(budget.month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</span>
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