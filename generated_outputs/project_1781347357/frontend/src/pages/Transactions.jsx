import api from '../services/api'
import { useState, useEffect } from 'react'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    type: 'expense',
    category: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const fetchTransactionsAndCategories = async () => {
      try {
        setLoading(true)
        const [transactionsRes, categoriesRes] = await Promise.all([
          api.get('/api/transactions'),
          api.get('/api/categories')
        ])
        setTransactions(transactionsRes.data)
        setCategories(categoriesRes.data)
        setError('')
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load transactions and categories')
      } finally {
        setLoading(false)
      }
    }

    fetchTransactionsAndCategories()
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setNewTransaction(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/transactions', newTransaction)
      setSuccess('Transaction added successfully!')
      setNewTransaction({
        description: '',
        amount: '',
        type: 'expense',
        category: '',
        date: new Date().toISOString().split('T')[0]
      })
      const res = await api.get('/api/transactions')
      setTransactions(res.data)
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to add transaction')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return
    try {
      await api.delete(`/api/transactions/${id}`)
      setTransactions(transactions.filter(t => t._id !== id))
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete transaction')
    }
  }

  if (loading) return <div className="app-wrapper">Loading...</div>
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Transactions</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="description">Description</label>
              <input
                type="text"
                id="description"
                name="description"
                className="form-input"
                value={newTransaction.description}
                onChange={handleInputChange}
                placeholder="e.g. Grocery shopping"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="amount">Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                className="form-input"
                value={newTransaction.amount}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="type">Type</label>
              <select
                id="type"
                name="type"
                className="form-select"
                value={newTransaction.type}
                onChange={handleInputChange}
                required
              >
                <option value="expense">Expense</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="category">Category</label>
              <select
                id="category"
                name="category"
                className="form-select"
                value={newTransaction.category}
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
              <label className="form-label" htmlFor="date">Date</label>
              <input
                type="date"
                id="date"
                name="date"
                className="form-input"
                value={newTransaction.date}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Transaction</button>
          </div>
        </form>
        {success && <p className="badge badge-success">{success}</p>}
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${(transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0) - transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0)).toFixed(2)}</p>
        </div>
      </div>
      <div className="section">
        <h2>Transaction List</h2>
        <div className="items-grid">
          {transactions.length > 0 ? (
            transactions.map(transaction => (
              <div key={transaction._id} className="item-card">
                <div className="item-title">{transaction.description}</div>
                <div className="item-details">
                  <span className={`badge ${transaction.type === 'expense' ? 'badge-danger' : 'badge-success'}`}>
                    {transaction.type === 'expense' ? 'Expense' : 'Income'}
                  </span>
                  <span>${transaction.amount.toFixed(2)}</span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                  <span>{categories.find(c => c._id === transaction.category)?.name || 'Uncategorized'}</span>
                </div>
                <div className="item-actions">
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(transaction._id)}>Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No transactions yet. Add your first transaction above.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('form').style.display = 'block'}>Add Transaction</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}