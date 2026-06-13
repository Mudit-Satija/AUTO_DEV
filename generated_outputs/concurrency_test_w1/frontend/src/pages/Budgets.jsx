import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newBudget, setNewBudget] = useState({ categoryId: '', amount: '', month: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
        console.error(err);
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
    if (!newBudget.categoryId || !newBudget.amount || !newBudget.month) return;

    try {
      await api.post('/api/budgets', newBudget);
      setSuccess('Budget created successfully!');
      setNewBudget({ categoryId: '', amount: '', month: '' });
      const budgetsRes = await api.get('/api/budgets');
      setBudgets(budgetsRes.data);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to create budget. Please check your inputs and try again.');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this budget?')) return;

    try {
      await api.delete(`/api/budgets/${id}`);
      const budgetsRes = await api.get('/api/budgets');
      setBudgets(budgetsRes.data);
      setSuccess('Budget deleted successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete budget. Please try again later.');
      console.error(err);
    }
  };

  if (loading) return <div className="app-wrapper">Loading...</div>;
  if (error) return <div className="app-wrapper"><div className="empty-state"><p>{error}</p><button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button></div></div>;

  const totalBudgeted = budgets.reduce((sum, b) => sum + b.amount, 0);
  const totalSpent = budgets.reduce((sum, b) => {
    const spent = b.spent || 0;
    return sum + spent;
  }, 0);

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Budgets</h1>
      </div>
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="categoryId">Category</label>
              <select
                id="categoryId"
                name="categoryId"
                value={newBudget.categoryId}
                onChange={handleInputChange}
                className="form-select"
                required
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category._id} value={category._id}>{category.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="amount">Amount ($)</label>
              <input
                type="number"
                id="amount"
                name="amount"
                value={newBudget.amount}
                onChange={handleInputChange}
                className="form-input"
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
                value={newBudget.month}
                onChange={handleInputChange}
                className="form-input"
                required
              />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">Add Budget</button>
          </div>
        </form>
        {success && <p style={{ color: 'green', marginTop: '0.5rem' }}>{success}</p>}
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Budgeted</h3>
          <p className="stat-value">${totalBudgeted.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Total Spent</h3>
          <p className="stat-value">${totalSpent.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Remaining</h3>
          <p className="stat-value">${(totalBudgeted - totalSpent).toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <h3>Budgets</h3>
          <p className="stat-value">{budgets.length}</p>
        </div>
      </div>
      <div className="section">
        <h2>Current Budgets</h2>
        <div className="items-grid">
          {budgets.length > 0 ? (
            budgets.map(budget => {
              const category = categories.find(c => c._id === budget.categoryId) || { name: 'Unknown' };
              const percentage = budget.amount > 0 ? (budget.spent / budget.amount) * 100 : 0;
              return (
                <div key={budget._id} className="item-card">
                  <div className="item-title">{category.name}</div>
                  <div className="item-details">
                    <p>Month: {new Date(budget.month).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}</p>
                    <p>Budget: ${budget.amount.toFixed(2)}</p>
                    <p>Spent: ${budget.spent?.toFixed(2) || '0.00'}</p>
                    <div style={{ marginTop: '0.5rem', width: '100%', height: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px', overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${Math.min(percentage, 100)}%`,
                          backgroundColor: percentage > 100 ? '#ef4444' : percentage > 80 ? '#f59e0b' : '#10b981',
                          borderRadius: '4px',
                          transition: 'width 0.3s ease'
                        }}
                      ></div>
                    </div>
                    <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
                      {percentage.toFixed(0)}% of budget used
                    </p>
                  </div>
                  <div className="item-actions">
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(budget._id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-state">
              <p>No budgets set yet. Create your first budget above.</p>
              <button className="btn btn-primary" onClick={() => document.querySelector('#categoryId')?.focus()}>Add Budget</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Budgets;