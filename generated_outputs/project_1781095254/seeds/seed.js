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
      name: 'Laptop',
      description: 'High-performance laptop for professionals',
      price: 999.99,
      category: 'Electronics',
      stock: 15,
    },
    {
      name: 'Coffee Mug',
      description: 'Ceramic coffee mug with insulated design',
      price: 12.5,
      category: 'Kitchen',
      stock: 50,
    },
    {
      name: 'Wireless Headphones',
      description: 'Noise-cancelling wireless headphones',
      price: 199.99,
      category: 'Electronics',
      stock: 25,
    },
    {
      name: 'Notebook',
      description: 'Hardcover notebook with 100 pages',
      price: 8.99,
      category: 'Stationery',
      stock: 100,
    },
    {
      name: 'Bluetooth Speaker',
      description: 'Portable Bluetooth speaker with 20-hour battery',
      price: 79.99,
      category: 'Electronics',
      stock: 30,
    },
  ];

  const orders = [
    {
      customerName: 'John Doe',
      customerEmail: 'john.doe@example.com',
      items: [
        { productId: null, name: 'Laptop', quantity: 1, price: 999.99 },
        { productId: null, name: 'Coffee Mug', quantity: 2, price: 12.5 },
      ],
      totalAmount: 1024.99,
      status: 'completed',
      shippingAddress: '123 Main St, City, Country',
    },
    {
      customerName: 'Jane Smith',
      customerEmail: 'jane.smith@example.com',
      items: [
        { productId: null, name: 'Wireless Headphones', quantity: 1, price: 199.99 },
        { productId: null, name: 'Notebook', quantity: 3, price: 8.99 },
      ],
      totalAmount: 226.96,
      status: 'pending',
      shippingAddress: '456 Oak Ave, City, Country',
    },
    {
      customerName: 'Bob Johnson',
      customerEmail: 'bob.johnson@example.com',
      items: [
        { productId: null, name: 'Bluetooth Speaker', quantity: 1, price: 79.99 },
        { productId: null, name: 'Coffee Mug', quantity: 1, price: 12.5 },
      ],
      totalAmount: 92.49,
      status: 'shipped',
      shippingAddress: '789 Pine Rd, City, Country',
    },
  ];

  const productDocs = await Product.insertMany(products);

  const productMap = {};
  productDocs.forEach(product => {
    productMap[product.name] = product._id;
  });

  orders.forEach(order => {
    order.items = order.items.map(item => ({
      ...item,
      productId: productMap[item.name],
    }));
  });

  await Order.insertMany(orders);

  console.log('Database seeded successfully!');
  mongoose.connection.close();
};

seedDatabase().catch(err => console.error(err));