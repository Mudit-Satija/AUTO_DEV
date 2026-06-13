import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Reports() {
  const [reports, setReports] = useState([])
  const [filters, setFilters] = useState({ period: 'month', category: '' })
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchReportsAndCategories = async () => {
      try {
        setLoading(true)
        const [reportsRes, categoriesRes] = await Promise.all([
          api.get('/api/reports', { params: filters }),
          api.get('/api/categories')
        ])
        setReports(reportsRes.data)
        setCategories(categoriesRes.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load reports')
      } finally {
        setLoading(false)
      }
    }

    fetchReportsAndCategories()
  }, [filters])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Reports</h1>
      </div>
      <div className="form-card">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Period</label>
            <select className="form-select" name="period" value={filters.period} onChange={handleFilterChange}>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select className="form-select" name="category" value={filters.category} onChange={handleFilterChange}>
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat._id} value={cat._id}>{cat.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      <div className="section">
        <h2>Expense Report</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Amount</th>
                <th>Percentage</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {reports.length > 0 ? (
                reports.map((report, index) => (
                  <tr key={index}>
                    <td>{report.categoryName}</td>
                    <td>${report.amount.toFixed(2)}</td>
                    <td>{report.percentage.toFixed(1)}%</td>
                    <td>{report.transactionCount}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="empty-state">
                    No data available for selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="section">
        <h2>Income vs Expenses</h2>
        <div className="chart-container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ flex: 1, marginRight: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Income</span>
                <span>${reports.reduce((sum, r) => sum + (r.type === 'income' ? r.amount : 0), 0).toFixed(2)}</span>
              </div>
              <div style={{ width: '100%', backgroundColor: '#e0e0e0', height: '20px', borderRadius: '10px', overflow: 'hidden' }}>
                <div 
                  style={{ 
                    width: '100%', 
                    height: '100%', 
                    backgroundColor: '#10b981',
                    borderRadius: '10px'
                  }}
                />
              </div>
            </div>
            <div style={{ flex: 1, marginLeft: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span>Expenses</span>
                <span>${reports.reduce((sum, r) => sum + (r.type === 'expense' ? r.amount : 0), 0).toFixed(2)}</span>
              </div>
              <div style={{ width: '100%', backgroundColor: '#e0e0e0', height: '20px', borderRadius: '10px', overflow: 'hidden' }}>
                <div 
                  style={{ 
                    width: `${(reports.reduce((sum, r) => sum + (r.type === 'expense' ? r.amount : 0), 0) / (reports.reduce((sum, r) => sum + (r.type === 'income' ? r.amount : 0), 0) || 1)) * 100}%`, 
                    height: '100%', 
                    backgroundColor: '#ef4444',
                    borderRadius: '10px',
                    transition: 'width 0.5s ease'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}