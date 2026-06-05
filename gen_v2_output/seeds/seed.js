const mongoose = require('mongoose');
const dotenv = require('dotenv');
dotenv.config();

const db = require('../src/config/database.js');
const User = require('../src/models/users.js');
const Post = require('../src/models/posts.js');
const Inventory = require('../src/models/inventory.js');
const Role = require('../src/models/roles.js');

const seedData = async () => {
  try {
    await db.connect();

    // Clear existing data
    await User.deleteMany({});
    await Post.deleteMany({});
    await Inventory.deleteMany({});
    await Role.deleteMany({});

    // Create roles
    const adminRole = new Role({
      name: 'admin',
      permissions: ['create', 'read', 'update', 'delete']
    });
    const editorRole = new Role({
      name: 'editor',
      permissions: ['create', 'read', 'update']
    });
    const viewerRole = new Role({
      name: 'viewer',
      permissions: ['read']
    });

    await Promise.all([adminRole.save(), editorRole.save(), viewerRole.save()]);

    // Create users
    const adminUser = new User({
      username: 'admin',
      email: 'admin@example.com',
      password: 'password123', // In production, hash this
      role: adminRole._id
    });

    const editorUser = new User({
      username: 'editor',
      email: 'editor@example.com',
      password: 'password123', // In production, hash this
      role: editorRole._id
    });

    const viewerUser = new User({
      username: 'viewer',
      email: 'viewer@example.com',
      password: 'password123', // In production, hash this
      role: viewerRole._id
    });

    await Promise.all([adminUser.save(), editorUser.save(), viewerUser.save()]);

    // Create posts
    const post1 = new Post({
      title: 'Welcome to Our Platform',
      content: 'This is the first post on our platform.',
      author: adminUser._id,
      published: true
    });

    const post2 = new Post({
      title: 'Getting Started with React',
      content: 'React is a powerful JavaScript library for building user interfaces.',
      author: editorUser._id,
      published: true
    });

    const post3 = new Post({
      title: 'Draft Post',
      content: 'This is a draft post that is not yet published.',
      author: editorUser._id,
      published: false
    });

    await Promise.all([post1.save(), post2.save(), post3.save()]);

    // Create inventory items
    const item1 = new Inventory({
      name: 'Laptop',
      description: 'High-performance laptop for developers',
      quantity: 15,
      category: 'Electronics',
      location: 'Warehouse A'
    });

    const item2 = new Inventory({
      name: 'Mouse',
      description: 'Wireless ergonomic mouse',
      quantity: 50,
      category: 'Electronics',
      location: 'Warehouse B'
    });

    const item3 = new Inventory({
      name: 'Keyboard',
      description: 'Mechanical keyboard with RGB lighting',
      quantity: 25,
      category: 'Electronics',
      location: 'Warehouse A'
    });

    await Promise.all([item1.save(), item2.save(), item3.save()]);

    console.log('Seed data successfully inserted');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
};

seedData();