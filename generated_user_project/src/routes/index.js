const express = require('express');
const postsRouter = require('./posts').router;
const inventoryRouter = require('./inventory').router;
const rolesRouter = require('./roles').router;

const router = express.Router();

router.use('/posts', postsRouter);
router.use('/inventory', inventoryRouter);
router.use('/roles', rolesRouter);

module.exports = router;