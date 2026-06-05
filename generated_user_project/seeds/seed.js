const { connectDB } = require('../src/config/database');
const User = require('../src/models/users');
const Post = require('../src/models/posts');
const Inventory = require('../src/models/inventory');
const Role = require('../src/models/roles');

const seedDatabase = async () => {
  await connectDB();

  await Role.deleteMany({});
  await User.deleteMany({});
  await Post.deleteMany({});
  await Inventory.deleteMany({});

  const adminRole = new Role({
    name: 'admin',
    permissions: ['create', 'read', 'update', 'delete']
  });
  const userRole = new Role({
    name: 'user',
    permissions: ['read']
  });

  await adminRole.save();
  await userRole.save();

  const adminUser = new User({
    username: 'admin',
    email: 'admin@example.com',
    password: '$2a$10$K6J4Z3wv8u5Y9X2b1Qp7uO9cZ1x3w7v9Y8z6W5r4s2t3u1v2w3x4', // password123
    role: adminRole._id
  });

  const regularUser = new User({
    username: 'user',
    email: 'user@example.com',
    password: '$2a$10$K6J4Z3wv8u5Y9X2b1Qp7uO9cZ1x3w7v9Y8z6W5r4s2t3u1v2w3x4', // password123
    role: userRole._id
  });

  await adminUser.save();
  await regularUser.save();

  const posts = [
    {
      title: 'First Post',
      content: 'This is the content of the first post.',
      author: adminUser._id
    },
    {
      title: 'Second Post',
      content: 'This is the content of the second post.',
      author: regularUser._id
    }
  ];

  const inventories = [
    {
      name: 'Item One',
      quantity: 100,
      category: 'Electronics',
      location: 'Warehouse A'
    },
    {
      name: 'Item Two',
      quantity: 50,
      category: 'Clothing',
      location: 'Warehouse B'
    }
  ];

  await Post.insertMany(posts);
  await Inventory.insertMany(inventories);

  console.log('Database seeded successfully');
};

seedDatabase().catch(err => console.error(err));