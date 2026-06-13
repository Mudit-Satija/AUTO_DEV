import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Analytics = () => {
  const [stats, setStats] = useState({});
  const [breakdown, setBreakdown] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const [statsRes, breakdownRes] = await Promise.all([
          api.get('/api/analytics/stats'),
          api.get('/api/analytics/breakdown')
        ]);
        setStats(statsRes.data);
        setBreakdown(breakdownRes.data);
        setError('');
      } catch (err) {
        setError('Failed to load analytics data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Analytics</h1>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${stats.totalExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${stats.totalIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${stats.netBalance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{stats.transactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.length > 0 ? (
            <div className="items-grid">
              {breakdown.map((item, index) => (
                <div key={index} className="card">
                  <div className="card-header">
                    <h3>{item.category || 'Uncategorized'}</h3>
                  </div>
                  <div className="card-content">
                    <div className="progress-bar" style={{ width: `${(item.amount / stats.totalExpenses) * 100 || 0}%`, backgroundColor: item.color || '#3b82f6' }}>
                      <span className="stat-value">${item.amount.toFixed(2)}</span>
                    </div>
                  </div>
                  <div className="card-footer">
                    <span className="badge">{item.count} transactions</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No spending data available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;