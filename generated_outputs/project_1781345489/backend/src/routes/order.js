const express = require('express');
const Order = require('../models/order');
const router = express.Router();

// GET all orders
router.get('/', async (req, res, next) => {
  try {
    const orders = await Order.find().populate('productId', 'name price');
    res.json({
      success: true,
      data: orders,
    });
  } catch (err) {
    next(err);
  }
});

// GET order by ID
router.get('/:id', async (req, res, next) => {
  try {
    const order = await Order.findById(req.params.id).populate('productId', 'name price');
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }
    res.json({
      success: true,
      data: order,
    });
  } catch (err) {
    next(err);
  }
});

// POST create order
router.post('/', async (req, res, next) => {
  try {
    const { productId, quantity, customerName, customerEmail } = req.body;

    // Validate required fields
    if (!productId || !quantity || !customerName || !customerEmail) {
      return res.status(400).json({
        success: false,
        message: 'Missing required fields: productId, quantity, customerName, customerEmail',
      });
    }

    // Fetch product to calculate total amount
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found',
      });
    }

    const totalAmount = product.price * quantity;

    const order = new Order({
      productId,
      quantity,
      totalAmount,
      customerName,
      customerEmail,
    });

    await order.save();
    res.status(201).json({
      success: true,
      data: order,
    });
  } catch (err) {
    next(err);
  }
});

// PUT update order status
router.put('/:id/status', async (req, res, next) => {
  try {
    const { status } = req.body;

    if (!status || !['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid status value',
      });
    }

    const order = await Order.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true, runValidators: true }
    );

    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }

    res.json({
      success: true,
      data: order,
    });
  } catch (err) {
    next(err);
  }
});

// DELETE order
router.delete('/:id', async (req, res, next) => {
  try {
    const order = await Order.findByIdAndDelete(req.params.id);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found',
      });
    }
    res.json({
      success: true,
      message: 'Order deleted successfully',
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;