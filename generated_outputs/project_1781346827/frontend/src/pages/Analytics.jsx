import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Analytics = () => {
  const [metrics, setMetrics] = useState({});
  const [breakdown, setBreakdown] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/analytics');
        setMetrics(res.data.metrics);
        setBreakdown(res.data.breakdown);
        setError('');
      } catch (err) {
        setError('Failed to load analytics data. Please try again later.');
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
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${metrics.totalIncome?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${metrics.netBalance?.toFixed(2) || 0}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{metrics.transactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item, index) => (
            <div key={index} className="card">
              <div className="card-header">
                <h3>{item.category}</h3>
              </div>
              <div className="card-content">
                <div className="progress-bar" style={{ width: `${(item.amount / metrics.totalExpenses) * 100}%`, backgroundColor: item.color || '#3b82f6' }}>
                  <span style={{ color: 'white', padding: '4px', fontSize: '12px' }}>
                    {item.amount.toFixed(2)} ({item.percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
              <div className="card-footer">
                <span>{item.amount.toFixed(2)} ({item.percentage.toFixed(1)}%)</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;