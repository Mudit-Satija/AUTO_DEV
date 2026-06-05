const mongoose = require('mongoose');
const dotenv = require('dotenv');
dotenv.config();

const db = require('../src/config/database');
const User = require('../src/models/users');
const Post = require('../src/models/posts');
const Inventory = require('../src/models/inventory');
const Role = require('../src/models/roles');

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
      permissions: ['create:post', 'read:post', 'update:post', 'delete:post', 'create:inventory', 'read:inventory', 'update:inventory', 'delete:inventory']
    });
    const userRole = new Role({
      name: 'user',
      permissions: ['read:post', 'read:inventory']
    });

    await adminRole.save();
    await userRole.save();

    // Create users
    const adminUser = new User({
      username: 'admin',
      email: 'admin@example.com',
      password: 'password123', // In production, use bcrypt
      role: adminRole._id
    });

    const regularUser = new User({
      username: 'user',
      email: 'user@example.com',
      password: 'password123', // In production, use bcrypt
      role: userRole._id
    });

    await adminUser.save();
    await regularUser.save();

    // Create posts
    const post1 = new Post({
      title: 'First Post',
      content: 'This is the content of the first post.',
      author: adminUser._id,
      published: true
    });

    const post2 = new Post({
      title: 'Second Post',
      content: 'This is the content of the second post.',
      author: regularUser._id,
      published: true
    });

    await post1.save();
    await post2.save();

    // Create inventory items
    const inventory1 = new Inventory({
      name: 'Laptop',
      description: 'High-performance laptop for development',
      quantity: 10,
      category: 'Electronics',
      addedBy: adminUser._id
    });

    const inventory2 = new Inventory({
      name: 'Mouse',
      description: 'Wireless optical mouse',
      quantity: 50,
      category: 'Electronics',
      addedBy: regularUser._id
    });

    await inventory1.save();
    await inventory2.save();

    console.log('Seed data successfully inserted');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
};

seedData();