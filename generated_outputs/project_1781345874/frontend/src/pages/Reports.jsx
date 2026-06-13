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
        const response = await api.get('/api/reports');
        setReports(response.data);
        setError('');
      } catch (err) {
        setError('Failed to load reports. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Reports</h1>
      </div>
      <div className="section">
        <h2>Generated Reports</h2>
        <div className="items-grid">
          {reports.length === 0 ? (
            <div className="empty-state">
              <p>No reports generated yet. Generate a report to see your financial insights.</p>
              <button className="btn btn-primary">Generate Report</button>
            </div>
          ) : (
            reports.map(report => (
              <div key={report._id} className="item-card">
                <div className="item-title">{report.title}</div>
                <div className="item-details">
                  <span className="stat-value">{report.period}</span>
                  <span className="badge badge-info">{report.type}</span>
                  <span>{new Date(report.generatedAt).toLocaleDateString()}</span>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary btn-sm">View</button>
                  <button className="btn btn-primary btn-sm">Download</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="section">
        <h2>Report Templates</h2>
        <div className="items-grid">
          {['Monthly Expense Summary', 'Income vs Expense', 'Category Breakdown', 'Budget vs Actual'].map((template, index) => (
            <div key={index} className="item-card">
              <div className="item-title">{template}</div>
              <div className="item-details">
                <span className="badge badge-warning">Click to generate</span>
              </div>
              <div className="item-actions">
                <button className="btn btn-primary btn-sm">Generate</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Reports;