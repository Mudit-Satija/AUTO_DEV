import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  });

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/reports');
        setReports(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load reports. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const handleDateChange = (e) => {
    setDateRange({
      ...dateRange,
      [e.target.name]: e.target.value
    });
  };

  const generateReport = async () => {
    if (!dateRange.startDate || !dateRange.endDate) {
      setError('Please select both start and end dates.');
      return;
    }
    try {
      setLoading(true);
      const res = await api.get('/api/reports', {
        params: { startDate: dateRange.startDate, endDate: dateRange.endDate }
      });
      setReports(res.data);
      setError('');
    } catch (err) {
      setError('Failed to generate report. Please check your date range and try again.');
    } finally {
      setLoading(false);
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
            <label className="form-label">Start Date</label>
            <input
              type="date"
              name="startDate"
              value={dateRange.startDate}
              onChange={handleDateChange}
              className="form-input"
            />
          </div>
          <div className="form-group">
            <label className="form-label">End Date</label>
            <input
              type="date"
              name="endDate"
              value={dateRange.endDate}
              onChange={handleDateChange}
              className="form-input"
            />
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={generateReport}>Generate Report</button>
          </div>
        </div>
      </div>
      <div className="section">
        <h2>Financial Summary</h2>
        {reports.length === 0 ? (
          <div className="empty-state">
            <p>No reports available. Generate a report using the date range above.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date Range</th>
                  <th>Total Income</th>
                  <th>Total Expenses</th>
                  <th>Net Balance</th>
                  <th>Transactions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report, index) => (
                  <tr key={index}>
                    <td>{report.period}</td>
                    <td>${report.totalIncome.toFixed(2)}</td>
                    <td>${report.totalExpenses.toFixed(2)}</td>
                    <td>${report.netBalance.toFixed(2)}</td>
                    <td>{report.transactionCount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="section">
        <h2>Category Breakdown</h2>
        {reports.length === 0 ? (
          <div className="empty-state">
            <p>No category data available. Generate a report to see breakdowns.</p>
          </div>
        ) : (
          <div className="items-grid">
            {reports.flatMap(report => 
              report.categoryBreakdown.map((category, idx) => (
                <div key={`${report.period}-${idx}`} className="item-card">
                  <div className="item-title">{category.category}</div>
                  <div className="item-details">
                    <span>Amount: ${category.amount.toFixed(2)}</span>
                    <span>Percentage: {category.percentage.toFixed(1)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;