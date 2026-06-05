const express = require('express');
const eventsRouter = require('./events');
const registrationsRouter = require('./registrations');

const router = express.Router();

router.use('/events', eventsRouter);
router.use('/registrations', registrationsRouter);

module.exports = router;