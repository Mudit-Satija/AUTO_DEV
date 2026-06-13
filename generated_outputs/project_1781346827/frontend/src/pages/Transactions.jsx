import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    category: '',
    type: 'expense',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const res = await api.get('/api/transactions');
        setTransactions(res.data);
        setError('');
      } catch (err) {
        setError('Failed to load transactions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const handleInputChange = (e) => {
    setNewTransaction({
      ...newTransaction,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/transactions', newTransaction);
      setNewTransaction({
        description: '',
        amount: '',
        category: '',
        type: 'expense',
        date: new Date().toISOString().split('T')[0]
      });
      const res = await api.get('/api/transactions');
      setTransactions(res.data);
    } catch (err) {
      setError('Failed to add transaction. Please check your inputs and try again.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) return;
    try {
      await api.delete(`/api/transactions/${id}`);
      const res = await api.get('/api/transactions');
      setTransactions(res.data);
    } catch (err) {
      setError('Failed to delete transaction. Please try again later.');
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Transactions</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input
              type="text"
              name="description"
              value={newTransaction.description}
              onChange={handleInputChange}
              className="form-input"
              placeholder="Enter description"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input
              type="number"
              name="amount"
              value={newTransaction.amount}
              onChange={handleInputChange}
              className="form-input"
              placeholder="Enter amount"
              required
              min="0"
              step="0.01"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              name="category"
              value={newTransaction.category}
              onChange={handleInputChange}
              className="form-select"
              required
            >
              <option value="">Select a category</option>
              <option value="Food">Food</option>
              <option value="Transportation">Transportation</option>
              <option value="Housing">Housing</option>
              <option value="Utilities">Utilities</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Education">Education</option>
              <option value="Salary">Salary</option>
              <option value="Investment">Investment</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Type</label>
            <select
              name="type"
              value={newTransaction.type}
              onChange={handleInputChange}
              className="form-select"
              required
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Date</label>
            <input
              type="date"
              name="date"
              value={newTransaction.date}
              onChange={handleInputChange}
              className="form-input"
              required
            />
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Transaction</button>
          </div>
        </form>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${(transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0) - transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
      </div>
      <div className="section">
        <h2>All Transactions</h2>
        {transactions.length === 0 ? (
          <div className="empty-state">
            <p>No transactions recorded yet. Add your first transaction to get started.</p>
            <button className="btn btn-primary" onClick={() => document.querySelector('form').reset()}>Add Transaction</button>
          </div>
        ) : (
          <div className="items-grid">
            {transactions.map((transaction) => (
              <div key={transaction._id} className="item-card">
                <div className="item-title">{transaction.description}</div>
                <div className="item-details">
                  <span className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount.toFixed(2)}
                  </span>
                  <span>{transaction.category}</span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                </div>
                <div className="item-actions">
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(transaction._id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Transactions;