module.exports = {
  port: process.env.PORT || 5000,
  mongoUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/taskmanager',
  env: process.env.NODE_ENV || 'development',
};