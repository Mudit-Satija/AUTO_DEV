import { useEffect, useState } from 'react';
import api from '../services/api';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products');
        setProducts(response.data);
      } catch (error) {
        console.error('Failed to fetch products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) return <p>Loading products...</p>;

  return (
    <div>
      <h2>Products</h2>
      <div className="product-grid">
        {products.map(product => (
          <div key={product.id} className="card">
            <h3>{product.name}</h3>
            <p>${product.price}</p>
            <p>{product.description}</p>
            <button className="primary">Add to Cart</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Products;