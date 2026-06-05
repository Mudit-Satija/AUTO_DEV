const connectDB = require('../config/database');
const Post = require('../models/posts');
const Inventory = require('../models/inventory');

const seedData = async () => {
  try {
    await connectDB();

    await Post.deleteMany({});
    await Inventory.deleteMany({});

    const posts = [
      {
        title: 'Welcome to the Dashboard',
        content: 'This is the first post on the platform.',
        author: 'System',
        createdAt: new Date(),
      },
      {
        title: 'Latest Inventory Update',
        content: 'Inventory levels have been refreshed for Q3.',
        author: 'System',
        createdAt: new Date(),
      },
    ];

    const inventory = [
      {
        name: 'Product A',
        quantity: 150,
        category: 'Electronics',
        updatedAt: new Date(),
      },
      {
        name: 'Product B',
        quantity: 85,
        category: 'Clothing',
        updatedAt: new Date(),
      },
    ];

    await Post.insertMany(posts);
    await Inventory.insertMany(inventory);

    console.log('Seed data inserted successfully.');
  } catch (error) {
    console.error('Error seeding data:', error.message);
  } finally {
    process.exit(0);
  }
};

seedData();