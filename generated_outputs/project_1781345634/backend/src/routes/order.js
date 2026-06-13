const express = require('express');
const Order = require('../models/order');
const router = express.Router();

// GET all orders
router.get('/', async (req, res, next) => {
  try {
    const orders = await Order.find().populate('productId', 'name price');
    res.status(200).json({
      success: true,
      count: orders.length,
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
    res.status(200).json({
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

    // Validate product exists and has sufficient stock
    const product = await Product.findById(productId);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found',
      });
    }
    if (product.stock < quantity) {
      return res.status(400).json({
        success: false,
        message: 'Insufficient stock',
      });
    }

    const totalAmount = product.price * quantity;

    const order = await Order.create({
      productId,
      quantity,
      totalAmount,
      customerName,
      customerEmail,
    });

    // Reduce stock
    product.stock -= quantity;
    await product.save();

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
    const validStatuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled'];

    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid status',
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

    res.status(200).json({
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

    // Restore stock
    const product = await Product.findById(order.productId);
    if (product) {
      product.stock += order.quantity;
      await product.save();
    }

    res.status(200).json({
      success: true,
      message: 'Order deleted',
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;