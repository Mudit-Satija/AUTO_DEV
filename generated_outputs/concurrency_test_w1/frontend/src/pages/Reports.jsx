import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/reports');
        setReports(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load reports. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Reports</h1>
      </div>
      <div className="section">
        <h2>Monthly Reports</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Total Income</th>
                <th>Total Expenses</th>
                <th>Net Balance</th>
                <th>Transactions</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {reports.length > 0 ? (
                reports.map(report => (
                  <tr key={report.month}>
                    <td>{new Date(report.month).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</td>
                    <td>${report.totalIncome.toFixed(2)}</td>
                    <td>${report.totalExpenses.toFixed(2)}</td>
                    <td>${report.netBalance.toFixed(2)}</td>
                    <td>{report.transactionCount}</td>
                    <td>
                      <button className="btn btn-secondary btn-sm" onClick={() => window.open(`/api/reports/download?month=${report.month}`, '_blank')}>
                        Download
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="empty-state">
                    <p>No reports available.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="section">
        <h2>Category Reports</h2>
        <div className="items-grid">
          {reports.length > 0 ? (
            reports.flatMap(report => 
              (report.categoryBreakdown || []).map(category => ({
                ...category,
                month: report.month
              }))
            ).map((item, index) => {
              const month = new Date(item.month).toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
              return (
                <div key={index} className="item-card">
                  <div className="item-title">{item.category}</div>
                  <div className="item-details">
                    <p>Month: {month}</p>
                    <p>Amount: ${item.amount.toFixed(2)}</p>
                    <p>Percentage: {item.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-state">
              <p>No category breakdown data available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;