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
      description: 'Ergonomic wireless mouse with 1200 DPI',
      price: 29.99,
      category: 'Electronics',
      stock: 50,
    },
    {
      name: 'Bluetooth Speaker',
      description: 'Portable Bluetooth speaker with 20-hour battery',
      price: 79.99,
      category: 'Electronics',
      stock: 25,
    },
    {
      name: 'Coffee Mug',
      description: 'Ceramic coffee mug, 12 oz, dishwasher safe',
      price: 12.5,
      category: 'Home',
      stock: 100,
    },
    {
      name: 'Notebook',
      description: 'Hardcover notebook with 120 lined pages',
      price: 8.99,
      category: 'Stationery',
      stock: 75,
    },
    {
      name: 'Headphones',
      description: 'Over-ear noise-cancelling headphones',
      price: 199.99,
      category: 'Electronics',
      stock: 15,
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
      status: 'completed',
      date: new Date('2023-10-15'),
    },
    {
      customerName: 'Jane Smith',
      customerEmail: 'jane.smith@example.com',
      items: [
        { productId: null, name: 'Bluetooth Speaker', quantity: 1, price: 79.99 },
        { productId: null, name: 'Notebook', quantity: 3, price: 8.99 },
      ],
      total: 106.96,
      status: 'pending',
      date: new Date('2023-10-16'),
    },
    {
      customerName: 'Alice Johnson',
      customerEmail: 'alice.johnson@example.com',
      items: [
        { productId: null, name: 'Headphones', quantity: 1, price: 199.99 },
        { productId: null, name: 'Coffee Mug', quantity: 2, price: 12.5 },
      ],
      total: 224.99,
      status: 'shipped',
      date: new Date('2023-10-17'),
    },
  ];

  const createdProducts = await Product.insertMany(products);

  const productIdMap = {};
  createdProducts.forEach(product => {
    productIdMap[product.name] = product._id;
  });

  orders.forEach(order => {
    order.items = order.items.map(item => ({
      ...item,
      productId: productIdMap[item.name],
    }));
  });

  await Order.insertMany(orders);

  console.log('Database seeded successfully');
  mongoose.connection.close();
};

seedDatabase().catch(err => console.error(err));