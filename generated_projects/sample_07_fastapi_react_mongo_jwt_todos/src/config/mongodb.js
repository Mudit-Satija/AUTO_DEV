const { MongoClient } = require('mongodb');

const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const client = new MongoClient(uri, { useUnifiedTopology: true });

let db;

async function connectDB() {
  if (db) return db;
  try {
    await client.connect();
    db = client.db(process.env.MONGODB_DB_NAME || 'your_db_name');
    console.log('Connected to MongoDB');
    return db;
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    throw error;
  }
}

module.exports = { connectDB, client };