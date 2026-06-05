const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri, { useUnifiedTopology: true });

async function seed() {
  try {
    await client.connect();
    const db = client.db('your_db_name');

    const users = [
      {
        username: 'admin',
        email: 'admin@example.com',
        password: '$2a$10$examplehashedpassword', // Replace with actual hashed password
        role: 'admin',
        createdAt: new Date(),
      },
      {
        username: 'user1',
        email: 'user1@example.com',
        password: '$2a$10$examplehashedpassword', // Replace with actual hashed password
        role: 'user',
        createdAt: new Date(),
      },
    ];

    await db.collection('users').insertMany(users);
    console.log('Seed data inserted successfully');
  } catch (err) {
    console.error('Error seeding data:', err);
  } finally {
    await client.close();
  }
}

seed();