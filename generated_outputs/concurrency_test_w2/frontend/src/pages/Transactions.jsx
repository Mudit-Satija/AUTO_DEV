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
        const res = await api.get('/api/transactions');
        setTransactions(res.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load transactions');
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const handleAddTransaction = async (e) => {
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
      setError(err.response?.data?.message || 'Failed to create transaction');
    }
  };

  const handleDeleteTransaction = async (id) => {
    try {
      await api.delete(`/api/transactions/${id}`);
      const res = await api.get('/api/transactions');
      setTransactions(res.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete transaction');
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
        <form onSubmit={handleAddTransaction}>
          <div className="form-group">
            <label className="form-label">Description</label>
            <input 
              type="text" 
              className="form-input" 
              value={newTransaction.description} 
              onChange={(e) => setNewTransaction({...newTransaction, description: e.target.value})}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input 
              type="number" 
              className="form-input" 
              value={newTransaction.amount} 
              onChange={(e) => setNewTransaction({...newTransaction, amount: e.target.value})}
              required
              min="0"
              step="0.01"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category</label>
            <select 
              className="form-select" 
              value={newTransaction.category} 
              onChange={(e) => setNewTransaction({...newTransaction, category: e.target.value})}
              required
            >
              <option value="">Select Category</option>
              <option value="Food">Food</option>
              <option value="Transportation">Transportation</option>
              <option value="Housing">Housing</option>
              <option value="Utilities">Utilities</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Education">Education</option>
              <option value="Salary">Salary</option>
              <option value="Freelance">Freelance</option>
              <option value="Investments">Investments</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Type</label>
            <select 
              className="form-select" 
              value={newTransaction.type} 
              onChange={(e) => setNewTransaction({...newTransaction, type: e.target.value})}
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Date</label>
            <input 
              type="date" 
              className="form-input" 
              value={newTransaction.date} 
              onChange={(e) => setNewTransaction({...newTransaction, date: e.target.value})}
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
          <h3>Total Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount || 0), 0).toFixed(2)}</p>
        </div>
      </div>
      <div className="section">
        <h2>Transaction List</h2>
        <div className="items-grid">
          {transactions.length === 0 ? (
            <div className="empty-state">
              <p>No transactions yet. Add your first transaction to get started.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('form').reset()}>Add Transaction</button>
            </div>
          ) : (
            transactions.map((transaction) => (
              <div key={transaction._id} className="item-card">
                <div className="item-title">{transaction.description}</div>
                <div className="item-details">
                  <span className={transaction.type === 'income' ? 'badge badge-success' : 'badge badge-danger'}>
                    {transaction.type === 'income' ? '+' : '-'}${transaction.amount}
                  </span>
                  <span>{transaction.category}</span>
                  <span>{new Date(transaction.date).toLocaleDateString()}</span>
                </div>
                <div className="item-actions">
                  <button 
                    className="btn btn-danger btn-sm" 
                    onClick={() => handleDeleteTransaction(transaction._id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Transactions;