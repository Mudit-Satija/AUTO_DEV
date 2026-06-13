import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    type: 'expense',
    category: '',
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
        setError('Failed to load transactions');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTransaction(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/transactions', newTransaction);
      setNewTransaction({
        description: '',
        amount: '',
        type: 'expense',
        category: '',
        date: new Date().toISOString().split('T')[0]
      });
      const res = await api.get('/api/transactions');
      setTransactions(res.data);
    } catch (err) {
      setError('Failed to create transaction');
      console.error(err);
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
                required
                min="0"
                step="0.01"
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
                <option value="">Select category</option>
                <option value="food">Food</option>
                <option value="transportation">Transportation</option>
                <option value="housing">Housing</option>
                <option value="utilities">Utilities</option>
                <option value="entertainment">Entertainment</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="savings">Savings</option>
                <option value="salary">Salary</option>
                <option value="gifts">Gifts</option>
                <option value="other">Other</option>
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
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Income</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Expenses</h3>
          <p className="stat-value">${transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Net Balance</h3>
          <p className="stat-value">${(transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + parseFloat(t.amount), 0) - transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + parseFloat(t.amount), 0)).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Transactions</h3>
          <p className="stat-value">{transactions.length}</p>
        </div>
      </div>
      <div className="section">
        <h2>All Transactions</h2>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length > 0 ? (
                transactions.map((transaction, index) => (
                  <tr key={index}>
                    <td>{new Date(transaction.date).toLocaleDateString()}</td>
                    <td>{transaction.description}</td>
                    <td>{transaction.category}</td>
                    <td>
                      <span className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>
                        {transaction.type === 'expense' ? 'Expense' : 'Income'}
                      </span>
                    </td>
                    <td className={transaction.type === 'expense' ? 'badge badge-danger' : 'badge badge-success'}>
                      {transaction.type === 'expense' ? '-' : '+'}${transaction.amount.toFixed(2)}
                    </td>
                    <td>
                      <button className="btn btn-secondary btn-sm">Edit</button>
                      <button className="btn btn-danger btn-sm">Delete</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="empty-state">
                    No transactions found. Add your first transaction above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Transactions;