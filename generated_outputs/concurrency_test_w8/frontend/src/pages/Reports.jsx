import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/reports');
        setReports(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load reports');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setDateRange(prev => ({ ...prev, [name]: value }));
  };

  const generateCustomReport = async () => {
    if (!dateRange.start || !dateRange.end) return;
    try {
      const res = await api.get('/api/reports/custom', {
        params: { start: dateRange.start, end: dateRange.end }
      });
      setReports(res.data);
    } catch (err) {
      setError('Failed to generate custom report');
      console.error(err);
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Reports</h1>
      </div>
      <div className="form-card">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label" htmlFor="start">Start Date</label>
            <input
              type="date"
              id="start"
              name="start"
              className="form-input"
              value={dateRange.start}
              onChange={handleDateChange}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="end">End Date</label>
            <input
              type="date"
              id="end"
              name="end"
              className="form-input"
              value={dateRange.end}
              onChange={handleDateChange}
            />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={generateCustomReport}>Generate Report</button>
          </div>
        </div>
      </div>
      <div className="section">
        <h2>Monthly Summary</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Income</th>
                <th>Expenses</th>
                <th>Net</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {reports.length > 0 ? (
                reports.map((report, index) => (
                  <tr key={index}>
                    <td>{report.month}</td>
                    <td>${report.income.toFixed(2)}</td>
                    <td>${report.expenses.toFixed(2)}</td>
                    <td className={report.net >= 0 ? 'badge badge-success' : 'badge badge-danger'}>
                      ${report.net.toFixed(2)}
                    </td>
                    <td>{report.transactionCount}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="empty-state">
                    No reports available. Try generating a custom report.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="section">
        <h2>Category Breakdown</h2>
        <div className="items-grid">
          {reports.length > 0 ? (
            reports.flatMap(report => report.categoryBreakdown || []).map((category, index) => (
              <div key={index} className="card">
                <div className="card-header">
                  <h3>{category.category}</h3>
                </div>
                <div className="card-content">
                  <div className="progress-bar" style={{ width: `${(category.percentage || 0)}%`, backgroundColor: '#10b981' }}>
                    <span className="stat-value">${category.amount.toFixed(2)} ({category.percentage.toFixed(1)}%)</span>
                  </div>
                </div>
                <div className="card-footer">
                  <span className="badge">{category.count} transactions</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No category data available.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reports;