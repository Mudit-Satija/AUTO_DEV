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
      price: 999.99,
      category: 'Electronics',
      stock: 10,
    },
    {
      name: 'Coffee Mug',
      price: 12.5,
      category: 'Kitchen',
      stock: 50,
    },
    {
      name: 'Book: JavaScript Guide',
      price: 29.99,
      category: 'Books',
      stock: 25,
    },
    {
      name: 'Wireless Mouse',
      price: 25.0,
      category: 'Electronics',
      stock: 30,
    },
    {
      name: 'Notebook',
      price: 5.0,
      category: 'Stationery',
      stock: 100,
    },
  ];

  const orders = [
    {
      customerName: 'John Doe',
      customerEmail: 'john@example.com',
      items: [
        { productId: null, name: 'Laptop', quantity: 1, price: 999.99 },
        { productId: null, name: 'Coffee Mug', quantity: 2, price: 12.5 },
      ],
      total: 1024.99,
      status: 'completed',
      date: new Date('2023-10-01'),
    },
    {
      customerName: 'Jane Smith',
      customerEmail: 'jane@example.com',
      items: [
        { productId: null, name: 'Book: JavaScript Guide', quantity: 1, price: 29.99 },
        { productId: null, name: 'Wireless Mouse', quantity: 1, price: 25.0 },
      ],
      total: 54.99,
      status: 'pending',
      date: new Date('2023-10-02'),
    },
    {
      customerName: 'Bob Johnson',
      customerEmail: 'bob@example.com',
      items: [
        { productId: null, name: 'Notebook', quantity: 5, price: 5.0 },
        { productId: null, name: 'Coffee Mug', quantity: 1, price: 12.5 },
      ],
      total: 37.5,
      status: 'shipped',
      date: new Date('2023-10-03'),
    },
  ];

  const createdProducts = await Product.insertMany(products);

  orders.forEach(order => {
    order.items.forEach(item => {
      const product = createdProducts.find(p => p.name === item.name);
      if (product) item.productId = product._id;
    });
  });

  await Order.insertMany(orders);

  console.log('Database seeded successfully');
  mongoose.connection.close();
};

seedDatabase().catch(err => console.error(err));