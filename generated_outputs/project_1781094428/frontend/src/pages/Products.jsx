import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Products() {
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
  if (error) return <div className="empty-state"><p>Error: {error}</p></div>;

  return (
    <div className="app-wrapper">
      <div className="page-header">
        <h1>Products</h1>
        <p>Manage your product catalog</p>
      </div>

      <div className="section">
        <h2>Product List</h2>
        <div className="items-grid">
          {products.length > 0 ? (
            products.map((product) => (
              <div key={product._id} className="item-card">
                <h3 className="item-title">{product.name}</h3>
                <p className="item-details">
                  {product.description}
                  <br />
                  <strong>Price:</strong> ${product.price.toFixed(2)} | 
                  <strong> Stock:</strong> {product.stock}
                </p>
                <div className="item-actions">
                  <button className="btn btn-primary btn-sm">Edit</button>
                  <button className="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>No products found. Add your first product below.</p>
              <button className="btn btn-primary">Add Product</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}