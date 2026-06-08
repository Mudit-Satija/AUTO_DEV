const express = require('express');
const router = express.Router();

const calculatorRoutes = require('./calculator');

router.use('/calculator', calculatorRoutes);

module.exports = router;