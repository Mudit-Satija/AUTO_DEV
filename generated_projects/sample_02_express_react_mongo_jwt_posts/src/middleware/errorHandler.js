const errorHandler = (err, req, res, next) => {
  console.error(err.stack);

  if (res.headersSent) {
    return next(err);
  }

  const statusCode = err.status || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    success: false,
    message,
    error: process.env.NODE_ENV === 'development' ? err : {}
  });
};

module.exports = errorHandler;