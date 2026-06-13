const express = require("express");
const router = express.Router();
const Category = require("../models/category");

// GET all categories for a user
router.get("/", async (req, res) => {
  try {
    const categories = await Category.find({ userId: req.user._id }).sort("name");
    res.json(categories);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET category by ID
router.get("/:id", async (req, res) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) return res.status(404).json({ message: "Category not found" });
    if (category.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });
    res.json(category);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST create category
router.post("/", async (req, res) => {
  const { name, color } = req.body;

  try {
    const category = new Category({
      userId: req.user._id,
      name,
      color,
    });

    const savedCategory = await category.save();
    res.status(201).json(savedCategory);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT update category
router.put("/:id", async (req, res) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) return res.status(404).json({ message: "Category not found" });
    if (category.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });

    const { name, color } = req.body;
    if (name) category.name = name;
    if (color) category.color = color;

    const updatedCategory = await category.save();
    res.json(updatedCategory);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE category
router.delete("/:id", async (req, res) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) return res.status(404).json({ message: "Category not found" });
    if (category.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });

    await category.remove();
    res.json({ message: "Category deleted" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;