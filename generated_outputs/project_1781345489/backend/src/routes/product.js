const express = require('express');
const Product = require('../models/product');
const router = express.Router();

// GET all products
router.get('/', async (req, res, next) => {
  try {
    const products = await Product.find();
    res.json({
      success: true,
      data: products,
    });
  } catch (err) {
    next(err);
  }
});

// GET product by ID
router.get('/:id', async (req, res, next) => {
  try {
    const product = await Product.findById(req.params.id);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found',
      });
    }
    res.json({
      success: true,
      data: product,
    });
  } catch (err) {
    next(err);
  }
});

// POST create product
router.post('/', async (req, res, next) => {
  try {
    const { name, description, price, stock, category, imageUrl } = req.body;

    if (!name || !description || price === undefined || stock === undefined || !category) {
      return res.status(400).json({
        success: false,
        message: 'Missing required fields: name, description, price, stock, category',
      });
    }

    const product = new Product({
      name,
      description,
      price,
      stock,
      category,
      imageUrl,
    });

    await product.save();
    res.status(201).json({
      success: true,
      data: product,
    });
  } catch (err) {
    next(err);
  }
});

// PUT update product
router.put('/:id', async (req, res, next) => {
  try {
    const { name, description, price, stock, category, imageUrl } = req.body;

    const product = await Product.findByIdAndUpdate(
      req.params.id,
      {
        name,
        description,
        price,
        stock,
        category,
        imageUrl,
      },
      { new: true, runValidators: true }
    );

    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found',
      });
    }

    res.json({
      success: true,
      data: product,
    });
  } catch (err) {
    next(err);
  }
});

// DELETE product
router.delete('/:id', async (req, res, next) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);
    if (!product) {
      return res.status(404).json({
        success: false,
        message: 'Product not found',
      });
    }
    res.json({
      success: true,
      message: 'Product deleted successfully',
    });
  } catch (err) {
    next(err);
  }
});

module.exports = router;