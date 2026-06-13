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
            <label className="form-label" htmlFor="period">Period</label>
            <select
              id="period"
              name="period"
              className="form-select"
              value={filter.period}
              onChange={handleFilterChange}
            >
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              className="form-select"
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
                <th>Amount</th>
                <th>Percentage</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {reports.expenses?.length > 0 ? (
                reports.expenses.map((item, index) => (
                  <tr key={index}>
                    <td>{item.category}</td>
                    <td>${item.amount.toFixed(2)}</td>
                    <td>{item.percentage.toFixed(1)}%</td>
                    <td>{item.count}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="empty-state">
                    No expense data for this period.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="section">
        <h2>Income Summary</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Source</th>
                <th>Amount</th>
                <th>Percentage</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {reports.income?.length > 0 ? (
                reports.income.map((item, index) => (
                  <tr key={index}>
                    <td>{item.source}</td>
                    <td>${item.amount.toFixed(2)}</td>
                    <td>{item.percentage.toFixed(1)}%</td>
                    <td>{item.count}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="empty-state">
                    No income data for this period.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}