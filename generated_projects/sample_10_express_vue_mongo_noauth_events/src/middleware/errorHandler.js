const errorHandler = (err, req, res, next) => {
  console.error(err.stack);

  const statusCode = res.statusCode === 200 ? 500 : res.statusCode;
  const message = statusCode === 500 ? 'Internal Server Error' : err.message;

  res.status(statusCode).json({
    success: false,
    message: message,
    ...(process.env.NODE_ENV === 'development' ? { stack: err.stack } : {})
  });
};

module.exports = errorHandler;