const mongoose = require('mongoose');
const db = require('../src/config/database.js');
const Post = require('../src/models/posts.js');
const Inventory = require('../src/models/inventory.js');

async function seed() {
  try {
    await db.connect();

    // Clear existing data
    await Post.deleteMany({});
    await Inventory.deleteMany({});

    // Seed posts
    const postsData = [
      {
        title: 'Welcome to Our Platform',
        content: 'This is the first post on our platform. Enjoy exploring!',
        author: 'System',
        createdAt: new Date('2023-01-15T10:00:00Z'),
        updatedAt: new Date('2023-01-15T10:00:00Z')
      },
      {
        title: 'Getting Started with React',
        content: 'React is a powerful JavaScript library for building user interfaces.',
        author: 'Admin',
        createdAt: new Date('2023-01-20T14:30:00Z'),
        updatedAt: new Date('2023-01-20T14:30:00Z')
      },
      {
        title: 'Express.js Best Practices',
        content: 'Use middleware effectively, structure routes cleanly, and validate inputs.',
        author: 'Developer',
        createdAt: new Date('2023-01-25T09:15:00Z'),
        updatedAt: new Date('2023-01-25T09:15:00Z')
      }
    ];

    await Post.insertMany(postsData);

    // Seed inventory
    const inventoryData = [
      {
        name: 'Laptop',
        category: 'Electronics',
        quantity: 15,
        price: 999.99,
        updatedAt: new Date('2023-01-15T10:00:00Z')
      },
      {
        name: 'Mouse',
        category: 'Electronics',
        quantity: 50,
        price: 29.99,
        updatedAt: new Date('2023-01-15T10:00:00Z')
      },
      {
        name: 'Keyboard',
        category: 'Electronics',
        quantity: 30,
        price: 79.99,
        updatedAt: new Date('2023-01-15T10:00:00Z')
      },
      {
        name: 'Notebook',
        category: 'Stationery',
        quantity: 100,
        price: 5.99,
        updatedAt: new Date('2023-01-15T10:00:00Z')
      }
    ];

    await Inventory.insertMany(inventoryData);

    console.log('✅ Seed data successfully inserted!');
  } catch (error) {
    console.error('❌ Error seeding database:', error);
  } finally {
    await mongoose.connection.close();
  }
}

seed();