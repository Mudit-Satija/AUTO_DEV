const express = require('express');
const router = express.Router();

const postsRouter = require('./posts.js');
const inventoryRouter = require('./inventory.js');
const rolesRouter = require('./roles.js');

router.use('/posts', postsRouter);
router.use('/inventory', inventoryRouter);
router.use('/roles', rolesRouter);

module.exports = router;