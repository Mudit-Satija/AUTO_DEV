import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [upcomingBills, setUpcomingBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [statsRes, transactionsRes, billsRes] = await Promise.all([
          api.get('/api/dashboard/stats'),
          api.get('/api/transactions?limit=5&sort=-date'),
          api.get('/api/budgets/upcoming')
        ]);
        setStats(statsRes.data);
        setRecentTransactions(transactionsRes.data);
        setUpcomingBills(billsRes.data);
        setError('');
      } catch (err) {
        setError('Failed to load dashboard data');
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
          <h3>Total Balance</h3>
          <p className="stat-value">${stats.balance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Expenses</h3>
          <p className="stat-value">${stats.monthlyExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>This Month's Income</h3>
          <p className="stat-value">${stats.monthlyIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Unbudgeted</h3>
          <p className="stat-value">${stats.unbudgeted?.toFixed(2) || '0.00'}</p>
        </div>
      </div>
      <div className="section">
        <h2>Recent Activity</h2>
        <div className="activity-feed">
          {recentTransactions.length > 0 ? (
            recentTransactions.map((transaction, index) => (
              <div key={index} className="activity-item">
                <div className="activity-title">{transaction.description}</div>
                <div className="activity-meta">
                  <span className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>
                    {transaction.type === 'expense' ? '-' : '+'}${transaction.amount.toFixed(2)}
                  </span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                  <span className="badge badge-info">{transaction.category}</span>
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
            upcomingBills.map((bill, index) => (
              <div key={index} className="upcoming-item">
                <div className="upcoming-title">{bill.description}</div>
                <div className="upcoming-meta">
                  <span className="badge badge-warning">${bill.amount.toFixed(2)}</span>
                  <span>{new Date(bill.dueDate).toLocaleDateString()}</span>
                  <span className="badge badge-info">{bill.category}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No upcoming bills or payments.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;