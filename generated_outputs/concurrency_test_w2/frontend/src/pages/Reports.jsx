import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    period: 'thisMonth',
    category: '',
    type: 'all'
  });

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const params = new URLSearchParams();
        Object.keys(filters).forEach(key => {
          if (filters[key]) params.append(key, filters[key]);
        });
        const res = await api.get(`/api/reports?${params.toString()}`);
        setReports(res.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load reports');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const generateReport = () => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    window.open(`/api/reports/export?${params.toString()}`, '_blank');
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
            <label className="form-label">Period</label>
            <select 
              name="period" 
              className="form-select" 
              value={filters.period} 
              onChange={handleFilterChange}
            >
              <option value="thisMonth">This Month</option>
              <option value="lastMonth">Last Month</option>
              <option value="thisYear">This Year</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              name="category" 
              className="form-select" 
              value={filters.category} 
              onChange={handleFilterChange}
            >
              <option value="">All Categories</option>
              <option value="Food">Food</option>
              <option value="Transportation">Transportation</option>
              <option value="Housing">Housing</option>
              <option value="Utilities">Utilities</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Education">Education</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Type</label>
            <select 
              name="type" 
              className="form-select" 
              value={filters.type} 
              onChange={handleFilterChange}
            >
              <option value="all">All Types</option>
              <option value="expense">Expenses</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div className="form-actions">
            <button className="btn btn-primary" onClick={generateReport}>Export</button>
          </div>
        </div>
      </div>
      <div className="section">
        <h2>Transaction Reports</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Type</th>
                <th>Amount</th>
              </tr>
            </thead>
            <tbody>
              {reports.length === 0 ? (
                <tr>
                  <td colSpan="5" className="empty-state">
                    No transactions match your filters.
                  </td>
                </tr>
              ) : (
                reports.map((report) => (
                  <tr key={report._id}>
                    <td>{new Date(report.date).toLocaleDateString()}</td>
                    <td>{report.description}</td>
                    <td>{report.category}</td>
                    <td>
                      <span className={`badge ${report.type === 'income' ? 'badge-success' : 'badge-danger'}`}>
                        {report.type}
                      </span>
                    </td>
                    <td className={report.type === 'income' ? 'badge-success' : 'badge-danger'}>
                      {report.type === 'income' ? '+' : '-'}${report.amount.toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Reports;