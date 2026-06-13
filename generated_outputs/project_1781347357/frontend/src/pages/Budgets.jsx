import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Budgets() {
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [newBudget, setNewBudget] = useState({ category: '', amount: '', month: '' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const fetchBudgetsAndCategories = async () => {
      try {
        setLoading(true)
        const [budgetsRes, categoriesRes] = await Promise.all([
          api.get('/api/budgets'),
          api.get('/api/categories')
        ])
        setBudgets(budgetsRes.data)
        setCategories(categoriesRes.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load budgets and categories')
      } finally {
        setLoading(false)
      }
    }

    fetchBudgetsAndCategories()
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setNewBudget(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/budgets', newBudget)
      setSuccess('Budget created successfully!')
      setNewBudget({ category: '', amount: '', month: '' })
      const res = await api.get('/api/budgets')
      setBudgets(res.data)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create budget')
    }
  }

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Budgets</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                className="form-select"
                value={newBudget.category}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a category</option>
                {categories.map(cat => (
                  <option key={cat._id} value={cat._id}>{cat.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="amount">Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                className="form-input"
                value={newBudget.amount}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="month">Month</label>
              <input
                type="month"
                id="month"
                name="month"
                className="form-input"
                value={newBudget.month}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Create Budget</button>
          </div>
        </form>
        {success && <p className="badge badge-success">{success}</p>}
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Budgets</h3>
          <p className="stat-value">{budgets.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Allocated</h3>
          <p className="stat-value">${budgets.reduce((sum, b) => sum + b.amount, 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Over Budget</h3>
          <p className="stat-value">{budgets.filter(b => b.spent > b.amount).length}</p>
        </div>
        <div className="stat-card">
          <h3>Under Budget</h3>
          <p className="stat-value">{budgets.filter(b => b.spent < b.amount).length}</p>
        </div>
      </div>
      <div className="section">
        <h2>Budget List</h2>
        <div className="items-grid">
          {budgets.length > 0 ? (
            budgets.map(budget => (
              <div key={budget._id} className="item-card">
                <div className="item-title">{categories.find(c => c._id === budget.category)?.name || 'Unknown'}</div>
                <div className="item-details">
                  <span>Amount: ${budget.amount.toFixed(2)}</span>
                  <span>Spent: ${budget.spent.toFixed(2)}</span>
                  <span>Month: {new Date(budget.month).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</span>
                </div>
                <div className="item-actions">
                  <span className={`badge ${budget.spent > budget.amount ? 'badge-danger' : budget.spent < budget.amount ? 'badge-success' : 'badge-info'}`}>
                    {budget.spent > budget.amount ? 'Over' : budget.spent < budget.amount ? 'Under' : 'On Track'}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No budgets set yet. Create your first budget above.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('form').style.display = 'block'}>Add Budget</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}