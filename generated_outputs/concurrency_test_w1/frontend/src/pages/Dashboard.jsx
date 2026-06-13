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
        const [metricsRes, recentRes, upcomingRes] = await Promise.all([
          api.get('/api/dashboard/metrics'),
          api.get('/api/transactions/recent'),
          api.get('/api/budgets/upcoming')
        ]);
        setMetrics(metricsRes.data);
        setRecentTransactions(recentRes.data);
        setUpcomingBills(upcomingRes.data);
        setError('');
      } catch (err) {
        setError('Failed to load dashboard data. Please try again later.');
        console.error(err);
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
          <h3>Net Balance</h3>
          <p className="stat-value">${metrics.netBalance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${metrics.totalIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{metrics.transactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentTransactions.length > 0 ? (
            recentTransactions.map(transaction => (
              <div key={transaction._id} className="activity-item">
                <div className="activity-title">
                  {transaction.description}
                </div>
                <div className="activity-meta">
                  <span className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toFixed(2)}
                  </span>
                  <span style={{ marginLeft: '0.5rem' }}>
                    {new Date(transaction.date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No recent transactions.</p>
            </div>
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming</h2>
        <div className="upcoming-list">
          {upcomingBills.length > 0 ? (
            upcomingBills.map(bill => (
              <div key={bill._id} className="upcoming-item">
                <div className="upcoming-title">
                  {bill.description}
                </div>
                <div className="upcoming-meta">
                  <span className="badge badge-warning">
                    ${bill.amount.toFixed(2)}
                  </span>
                  <span style={{ marginLeft: '0.5rem' }}>
                    Due {new Date(bill.dueDate).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming bills or expenses.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;