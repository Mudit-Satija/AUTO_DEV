const express = require('express');
const router = express.Router();

const postsRouter = require('./posts');
const inventoryRouter = require('./inventory');
const rolesRouter = require('./roles');

router.use('/posts', postsRouter);
router.use('/inventory', inventoryRouter);
router.use('/roles', rolesRouter);

module.exports = router;