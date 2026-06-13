const express = require("express");
const router = express.Router();
const Category = require("../models/category");

// GET all categories
router.get("/", async (req, res, next) => {
  try {
    const categories = await Category.find().sort("name");
    res.json({ success: true, data: categories });
  } catch (err) {
    next(err);
  }
});

// GET category by ID
router.get("/:id", async (req, res, next) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) {
      return res.status(404).json({ success: false, message: "Category not found" });
    }
    res.json({ success: true, data: category });
  } catch (err) {
    next(err);
  }
});

// POST create category
router.post("/", async (req, res, next) => {
  try {
    const { name, type, color } = req.body;
    if (!name || !type) {
      return res.status(400).json({ success: false, message: "name and type are required" });
    }
    if (!["income", "expense"].includes(type)) {
      return res.status(400).json({ success: false, message: "type must be 'income' or 'expense'" });
    }
    const category = new Category({ name, type, color });
    await category.save();
    res.status(201).json({ success: true, data: category });
  } catch (err) {
    next(err);
  }
});

// PUT update category
router.put("/:id", async (req, res, next) => {
  try {
    const category = await Category.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!category) {
      return res.status(404).json({ success: false, message: "Category not found" });
    }
    res.json({ success: true, data: category });
  } catch (err) {
    next(err);
  }
});

// DELETE category
router.delete("/:id", async (req, res, next) => {
  try {
    const category = await Category.findByIdAndDelete(req.params.id);
    if (!category) {
      return res.status(404).json({ success: false, message: "Category not found" });
    }
    res.json({ success: true, message: "Category deleted successfully" });
  } catch (err) {
    next(err);
  }
});

// GET categories by type
router.get("/type/:type", async (req, res, next) => {
  try {
    const { type } = req.params;
    if (!["income", "expense"].includes(type)) {
      return res.status(400).json({ success: false, message: "type must be 'income' or 'expense'" });
    }
    const categories = await Category.find({ type }).sort("name");
    res.json({ success: true, data: categories });
  } catch (err) {
    next(err);
  }
});

module.exports = router;