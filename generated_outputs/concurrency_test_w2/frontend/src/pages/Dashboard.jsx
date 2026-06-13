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
        const [metricsRes, transactionsRes, billsRes] = await Promise.all([
          api.get('/api/dashboard/metrics'),
          api.get('/api/transactions/recent'),
          api.get('/api/budgets/upcoming')
        ]);
        setMetrics(metricsRes.data);
        setRecentTransactions(transactionsRes.data);
        setUpcomingBills(billsRes.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load dashboard data');
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
          <h3>Current Balance</h3>
          <p className="stat-value">${metrics.balance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Income</h3>
          <p className="stat-value">${metrics.monthlyIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Expenses</h3>
          <p className="stat-value">${metrics.monthlyExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Spending vs Budget</h3>
          <p className="stat-value">{metrics.budgetUtilization ? `${Math.round(metrics.budgetUtilization)}%` : '0%'}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentTransactions.length === 0 ? (
            <div className="empty-state">
              <p>No recent transactions yet.</p>
            </div>
          ) : (
            recentTransactions.map((transaction) => (
              <div key={transaction._id} className="activity-item">
                <div className="activity-title">{transaction.description}</div>
                <div className="activity-meta">
                  <span className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount}
                  </span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                  <span className="badge badge-info">{transaction.category}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="section">
        <h2>Upcoming Bills</h2>
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
                  <span>${bill.amount}</span>
                  <span>{new Date(bill.dueDate).toLocaleDateString()}</span>
                  <span className="badge badge-warning">{bill.category}</span>
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