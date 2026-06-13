import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Analytics() {
  const [metrics, setMetrics] = useState({})
  const [breakdown, setBreakdown] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        const res = await api.get('/api/analytics')
        setMetrics(res.data.metrics)
        setBreakdown(res.data.breakdown)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load analytics')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [])

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

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
          <h3>Budget Used</h3>
          <p className="stat-value">${metrics.budgetUsed?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Remaining Budget</h3>
          <p className="stat-value">${metrics.remainingBudget?.toFixed(2) || '0.00'}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{metrics.transactionCount || 0}</p>
        </div>
      </div>
      <div className="section">
        <h2>Breakdown</h2>
        <div className="chart-container">
          {breakdown.map((item, index) => (
            <div key={index} className="card">
              <div className="card-header">
                <h3>{item.category}</h3>
              </div>
              <div className="card-content">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ flex: 1, backgroundColor: '#e0e0e0', height: '20px', borderRadius: '10px', overflow: 'hidden' }}>
                    <div 
                      style={{ 
                        height: '100%', 
                        width: `${(item.amount / metrics.totalExpenses) * 100 || 0}%`, 
                        backgroundColor: index === 0 ? '#3b82f6' : index === 1 ? '#10b981' : index === 2 ? '#f59e0b' : '#ef4444',
                        transition: 'width 0.5s ease'
                      }}
                    ></div>
                  </div>
                  <span style={{ fontWeight: 'bold' }}>${item.amount.toFixed(2)}</span>
                </div>
              </div>
              <div className="card-footer">
                <span className="badge badge-info">{item.percentage.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}