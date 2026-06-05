module.exports = {
  port: process.env.PORT || 3000,
  dbUri: process.env.MONGODB_URI || 'mongodb://localhost:27017/myapp',
  env: process.env.NODE_ENV || 'development',
  modules: ['posts', 'inventory'],
  pages: ['Dashboard', 'Posts'],
  authEnabled: false
};