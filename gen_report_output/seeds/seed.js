const connectDB = require('../config/database');
const User = require('../models/users');
const Post = require('../models/posts');
const Inventory = require('../models/inventory');
const Role = require('../models/roles');

const seedDatabase = async () => {
  try {
    await connectDB();

    // Clear existing data
    await User.deleteMany({});
    await Post.deleteMany({});
    await Inventory.deleteMany({});
    await Role.deleteMany({});

    // Create roles
    const adminRole = new Role({ name: 'admin' });
    const userRole = new Role({ name: 'user' });
    await adminRole.save();
    await userRole.save();

    // Create users
    const adminUser = new User({
      username: 'admin',
      email: 'admin@example.com',
      password: 'admin123', // In production, hash this password
      role: adminRole._id,
    });
    const regularUser = new User({
      username: 'user',
      email: 'user@example.com',
      password: 'user123', // In production, hash this password
      role: userRole._id,
    });
    await adminUser.save();
    await regularUser.save();

    // Create posts
    const post1 = new Post({
      title: 'First Post',
      content: 'This is the content of the first post.',
      author: adminUser._id,
    });
    const post2 = new Post({
      title: 'Second Post',
      content: 'This is the content of the second post.',
      author: regularUser._id,
    });
    await post1.save();
    await post2.save();

    // Create inventory items
    const item1 = new Inventory({
      name: 'Laptop',
      quantity: 10,
      price: 999.99,
      category: 'Electronics',
    });
    const item2 = new Inventory({
      name: 'Mouse',
      quantity: 50,
      price: 29.99,
      category: 'Electronics',
    });
    await item1.save();
    await item2.save();

    console.log('Database seeded successfully');
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    process.exit(0);
  }
};

seedDatabase();