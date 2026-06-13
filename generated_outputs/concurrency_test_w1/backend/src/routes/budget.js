const express = require("express");
const router = express.Router();
const Budget = require("../models/budget");

// GET all budgets for a user
router.get("/", async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) {
      return res.status(400).json({ message: "userId is required" });
    }
    const budgets = await Budget.find({ userId }).populate("category", "name type color");
    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET budget by ID
router.get("/:id", async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id).populate("category", "name type color");
    if (!budget) {
      return res.status(404).json({ message: "Budget not found" });
    }
    res.json(budget);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST create budget
router.post("/", async (req, res) => {
  try {
    const { userId, category, amount, month } = req.body;
    if (!userId || !category || amount === undefined || !month) {
      return res.status(400).json({ message: "userId, category, amount, and month are required" });
    }
    const budget = new Budget({ userId, category, amount, month });
    const savedBudget = await budget.save();
    res.status(201).json(savedBudget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT update budget
router.put("/:id", async (req, res) => {
  try {
    const { amount, month } = req.body;
    const budget = await Budget.findByIdAndUpdate(
      req.params.id,
      { amount, month, updatedAt: Date.now() },
      { new: true, runValidators: true }
    );
    if (!budget) {
      return res.status(404).json({ message: "Budget not found" });
    }
    res.json(budget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// DELETE budget
router.delete("/:id", async (req, res) => {
  try {
    const budget = await Budget.findByIdAndDelete(req.params.id);
    if (!budget) {
      return res.status(404).json({ message: "Budget not found" });
    }
    res.json({ message: "Budget deleted" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;