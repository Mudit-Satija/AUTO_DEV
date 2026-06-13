import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newBudget, setNewBudget] = useState({ category: '', amount: '', month: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBudgetsAndCategories = async () => {
      try {
        setLoading(true);
        const [budgetsRes, categoriesRes] = await Promise.all([
          api.get('/api/budgets'),
          api.get('/api/categories')
        ]);
        setBudgets(budgetsRes.data);
        setCategories(categoriesRes.data);
        setError('');
      } catch (err) {
        setError('Failed to load budgets and categories. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchBudgetsAndCategories();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewBudget(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/budgets', newBudget);
      setNewBudget({ category: '', amount: '', month: '' });
      const response = await api.get('/api/budgets');
      setBudgets(response.data);
    } catch (err) {
      setError('Failed to create budget. Please check your inputs and try again.');
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p></div></div>;

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
                required
                min="0"
                step="0.01"
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
            <button type="submit" className="btn btn-primary">Add Budget</button>
          </div>
        </form>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Budgets</h3>
          <p className="stat-value">{budgets.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Allocated</h3>
          <p className="stat-value">${budgets.reduce((sum, b) => sum + parseFloat(b.amount), 0).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Over Budget</h3>
          <p className="stat-value">{budgets.filter(b => b.spent > b.amount).length}</p>
        </div>
      </div>
      <div className="section">
        <h2>Budget List</h2>
        <div className="items-grid">
          {budgets.length === 0 ? (
            <div className="empty-state">
              <p>No budgets set yet. Add a budget to get started.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('form').style.display = 'block'}>Add Budget</button>
            </div>
          ) : (
            budgets.map(budget => (
              <div key={budget._id} className="item-card">
                <div className="item-title">{categories.find(c => c._id === budget.category)?.name || 'Unknown'}</div>
                <div className="item-details">
                  <span className="stat-value">${budget.amount.toFixed(2)}</span>
                  <span className="badge badge-info">${budget.spent.toFixed(2)} spent</span>
                  <span className="badge badge-warning">{((budget.spent / budget.amount) * 100).toFixed(0)}% used</span>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary btn-sm">Edit</button>
                  <button className="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Budgets;