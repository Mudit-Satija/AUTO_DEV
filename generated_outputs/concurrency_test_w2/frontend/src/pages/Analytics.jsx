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
        const [metricsRes, breakdownRes] = await Promise.all([
          api.get('/api/analytics/metrics'),
          api.get('/api/analytics/breakdown')
        ]);
        setMetrics(metricsRes.data);
        setBreakdown(breakdownRes.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load analytics data');
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
          <p className="stat-value">${metrics.totalExpenses?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${metrics.totalIncome?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${metrics.netBalance?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Spending This Month</h3>
          <p className="stat-value">${metrics.monthlySpending?.toFixed(2) || '0.00'}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item) => (
            <div key={item.category} className="breakdown-section">
              <div className="breakdown-label">{item.category}</div>
              <div className="breakdown-bar">
                <div 
                  className="breakdown-fill" 
                  style={{ width: `${(item.amount / metrics.totalExpenses) * 100 || 0}%`, backgroundColor: item.color || '#3b82f6' }}
                ></div>
              </div>
              <div className="breakdown-value">${item.amount.toFixed(2)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Analytics;