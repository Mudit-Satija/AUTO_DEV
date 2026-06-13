import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState({ period: 'month', category: '' })

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true)
        const res = await api.get('/api/reports', { params: filter })
        setReports(res.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load reports')
      } finally {
        setLoading(false)
      }
    }

    fetchReports()
  }, [filter])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilter(prev => ({ ...prev, [name]: value }))
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
            <select 
              className="form-select" 
              name="period" 
              value={filter.period} 
              onChange={handleFilterChange}
            >
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
              <option value="year">This Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              className="form-select" 
              name="category" 
              value={filter.category} 
              onChange={handleFilterChange}
            >
              <option value="">All Categories</option>
              {reports.categories?.map(cat => (
                <option key={cat._id} value={cat._id}>{cat.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      <div className="section">
        <h2>Expense Summary</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Total</th>
                <th>Percentage</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {reports.expenses?.length > 0 ? (
                reports.expenses.map((item, index) => (
                  <tr key={index}>
                    <td>{item.category}</td>
                    <td>${item.total.toFixed(2)}</td>
                    <td>{item.percentage.toFixed(1)}%</td>
                    <td>{item.count}</td>
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
        <h2>Income vs Expense</h2>
        <div className="chart-container">
          <div className="card">
            <div className="card-header">
              <h3>Income</h3>
            </div>
            <div className="card-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ flex: 1, backgroundColor: '#e0e0e0', height: '30px', borderRadius: '15px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      height: '100%', 
                      width: `${(reports.income / (reports.income + reports.expense)) * 100 || 0}%`, 
                      backgroundColor: '#10b981',
                      transition: 'width 0.5s ease'
                    }}
                  ></div>
                </div>
                <span style={{ fontWeight: 'bold' }}>${reports.income?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-header">
              <h3>Expense</h3>
            </div>
            <div className="card-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ flex: 1, backgroundColor: '#e0e0e0', height: '30px', borderRadius: '15px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      height: '100%', 
                      width: `${(reports.expense / (reports.income + reports.expense)) * 100 || 0}%`, 
                      backgroundColor: '#ef4444',
                      transition: 'width 0.5s ease'
                    }}
                  ></div>
                </div>
                <span style={{ fontWeight: 'bold' }}>${reports.expense?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}