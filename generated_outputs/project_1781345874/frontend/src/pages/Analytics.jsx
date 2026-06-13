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
        const [metricsRes, breakdownRes] = await Promise.all([
          api.get('/api/analytics/metrics'),
          api.get('/api/analytics/breakdown')
        ]);
        setMetrics(metricsRes.data);
        setBreakdown(breakdownRes.data);
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
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p></div></div>;

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
          <h3>Spending This Month</h3>
          <p className="stat-value">${metrics.monthlySpending?.toFixed(2) || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item) => (
            <div key={item.category} className="breakdown-section">
              <div className="item-title">{item.category}</div>
              <div className="item-details">
                <span className="stat-value">${item.amount.toFixed(2)}</span>
                <div className="progress-bar" style={{ width: `${(item.amount / metrics.totalExpenses) * 100 || 0}%` }}></div>
                <span className="badge badge-info">{item.percentage.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;