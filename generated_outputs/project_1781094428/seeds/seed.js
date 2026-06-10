const mongoose = require('mongoose');
const Product = require('../models/Product');
const Order = require('../models/Order');

const seedDatabase = async () => {
  await mongoose.connect('mongodb://localhost:27017/shopmanager', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });

  await Product.deleteMany({});
  await Order.deleteMany({});

  const products = [
    {
      name: 'Wireless Mouse',
      description: 'Ergonomic wireless mouse with scroll wheel',
      price: 29.99,
      category: 'Electronics',
      stock: 50,
    },
    {
      name: 'Bluetooth Speaker',
      description: 'Portable waterproof Bluetooth speaker',
      price: 79.99,
      category: 'Electronics',
      stock: 30,
    },
    {
      name: 'Coffee Mug',
      description: 'Ceramic coffee mug with handle',
      price: 12.5,
      category: 'Kitchen',
      stock: 100,
    },
    {
      name: 'Notebook',
      description: '120-page lined notebook',
      price: 5.99,
      category: 'Stationery',
      stock: 200,
    },
    {
      name: 'Headphones',
      description: 'Over-ear noise-cancelling headphones',
      price: 199.99,
      category: 'Electronics',
      stock: 25,
    },
  ];

  const orders = [
    {
      customerName: 'John Doe',
      customerEmail: 'john.doe@example.com',
      items: [
        { productId: null, name: 'Wireless Mouse', quantity: 2, price: 29.99 },
        { productId: null, name: 'Coffee Mug', quantity: 1, price: 12.5 },
      ],
      total: 72.48,
      status: 'shipped',
      date: new Date('2023-10-15'),
    },
    {
      customerName: 'Jane Smith',
      customerEmail: 'jane.smith@example.com',
      items: [
        { productId: null, name: 'Bluetooth Speaker', quantity: 1, price: 79.99 },
        { productId: null, name: 'Notebook', quantity: 5, price: 5.99 },
      ],
      total: 109.94,
      status: 'pending',
      date: new Date('2023-10-16'),
    },
    {
      customerName: 'Alice Johnson',
      customerEmail: 'alice.johnson@example.com',
      items: [
        { productId: null, name: 'Headphones', quantity: 1, price: 199.99 },
        { productId: null, name: 'Coffee Mug', quantity: 3, price: 12.5 },
      ],
      total: 237.49,
      status: 'delivered',
      date: new Date('2023-10-14'),
    },
  ];

  const createdProducts = await Product.insertMany(products);

  const productMap = {};
  createdProducts.forEach(product => {
    productMap[product.name] = product._id;
  });

  orders.forEach(order => {
    order.items = order.items.map(item => ({
      ...item,
      productId: productMap[item.name] || null,
    }));
  });

  await Order.insertMany(orders);

  console.log('Database seeded successfully');
  mongoose.disconnect();
};

seedDatabase().catch(console.error);