const express = require("express");
const router = express.Router();
const Category = require("../models/category");

// GET all categories
router.get("/", async (req, res) => {
  try {
    const categories = await Category.find().sort("name");
    res.json(categories);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET category by ID
router.get("/:id", async (req, res) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) {
      return res.status(404).json({ message: "Category not found" });
    }
    res.json(category);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST create category
router.post("/", async (req, res) => {
  const { name, type } = req.body;

  if (!name || !type) {
    return res.status(400).json({ message: "Name and type are required" });
  }

  if (!["income", "expense"].includes(type)) {
    return res.status(400).json({ message: "Type must be 'income' or 'expense'" });
  }

  const category = new Category({ name, type });
  try {
    const newCategory = await category.save();
    res.status(201).json(newCategory);
  } catch (err) {
    if (err.code === 11000) {
      res.status(409).json({ message: "Category name already exists" });
    } else {
      res.status(400).json({ message: err.message });
    }
  }
});

// PUT update category
router.put("/:id", async (req, res) => {
  try {
    const category = await Category.findById(req.params.id);
    if (!category) {
      return res.status(404).json({ message: "Category not found" });
    }

    const { name, type } = req.body;

    if (name !== undefined) category.name = name;
    if (type !== undefined) {
      if (!["income", "expense"].includes(type)) {
        return res.status(400).json({ message: "Type must be 'income' or 'expense'" });
      }
      category.type = type;
    }

    const updatedCategory = await category.save();
    res.json(updatedCategory);
  } catch (err) {
    if (err.code === 11000) {
      res.status(409).json({ message: "Category name already exists" });
    } else {
      res.status(400).json({ message: err.message });
    }
  }
});

// DELETE category
router.delete("/:id", async (req, res) => {
  try {
    const category = await Category.findByIdAndDelete(req.params.id);
    if (!category) {
      return res.status(404).json({ message: "Category not found" });
    }
    res.json({ message: "Category deleted" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;