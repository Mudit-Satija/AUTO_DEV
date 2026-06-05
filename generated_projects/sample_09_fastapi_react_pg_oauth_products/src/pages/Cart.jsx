import { useEffect, useState } from 'react';
import api from '../services/api';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await api.get('/cart');
        setCartItems(response.data);
      } catch (error) {
        console.error('Failed to fetch cart:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCart();
  }, []);

  if (loading) return <p>Loading cart...</p>;

  const totalPrice = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <div>
      <h2>Your Cart</h2>
      {cartItems.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          {cartItems.map(item => (
            <div key={item.id} className="cart-item">
              <div>
                <h3>{item.name}</h3>
                <p>${item.price} x {item.quantity}</p>
              </div>
              <span>${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
          <div className="cart-total">
            Total: ${totalPrice.toFixed(2)}
          </div>
        </>
      )}
    </div>
  );
};

export default Cart;