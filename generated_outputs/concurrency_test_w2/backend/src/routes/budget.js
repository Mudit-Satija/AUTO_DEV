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
    const budget = new Budget(req.body);
    const savedBudget = await budget.save();
    res.status(201).json(savedBudget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT update budget
router.put("/:id", async (req, res) => {
  try {
    const budget = await Budget.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
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

// GET budgets by month and year for a user
router.get("/monthly", async (req, res) => {
  try {
    const { userId, month, year } = req.query;
    if (!userId || !month || !year) {
      return res.status(400).json({ message: "userId, month, and year are required" });
    }
    const budgets = await Budget.find({
      userId,
      month: parseInt(month),
      year: parseInt(year),
    }).populate("category", "name type color");
    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;