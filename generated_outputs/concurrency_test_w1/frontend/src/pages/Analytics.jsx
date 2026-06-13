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
          <h3>Transactions</h3>
          <p className="stat-value">{metrics.transactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {breakdown.map((item, index) => (
                <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ minWidth: '120px', fontWeight: '500' }}>{item.category}</span>
                  <div style={{ flex: 1, height: '20px', backgroundColor: '#f0f0f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${(item.amount / metrics.totalExpenses) * 100}%`,
                        backgroundColor: index === 0 ? '#3b82f6' : index === 1 ? '#10b981' : index === 2 ? '#f59e0b' : '#ef4444',
                        borderRadius: '10px',
                        transition: 'width 0.5s ease'
                      }}
                    ></div>
                  </div>
                  <span style={{ minWidth: '80px', textAlign: 'right', fontWeight: '500' }}>
                    ${item.amount.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>No breakdown data available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;