import React, { useState, useEffect } from 'react';
import api from '../services/api';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await api.get('/products');
        setProducts(response.data);
      } catch (err) {
        setError(err.response?.data?.message || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Products</h1>
        <p>Manage your product catalog</p>
      </div>

      <div className="form-card">
        <div className="form-group">
          <label className="form-label">Add New Product</label>
          <p className="form-input" style={{ color: 'var(--secondary-color)' }}>
            Product creation is handled via backend API only. Use the API endpoint /products to create new products.
          </p>
        </div>
        <div className="form-actions">
          <button className="btn btn-primary" disabled>
            Create Product
          </button>
        </div>
      </div>

      <div className="section">
        <h2>Product Catalog</h2>
        {products.length > 0 ? (
          <div className="items-grid">
            {products.map(product => (
              <div key={product._id} className="item-card">
                <h3 className="item-title">{product.name}</h3>
                <div className="item-details">
                  <p><strong>Category:</strong> {product.category}</p>
                  <p><strong>Price:</strong> ${product.price.toFixed(2)}</p>
                  <p><strong>Stock:</strong> {product.stock}</p>
                </div>
                <div className="item-actions">
                  <button className="btn btn-secondary btn-sm" disabled>
                    Edit
                  </button>
                  <button className="btn btn-danger btn-sm" disabled>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>No products found. Add your first product via the API.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Products;