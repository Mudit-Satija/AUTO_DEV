const express = require("express");
const router = express.Router();
const Budget = require("../models/budget");

// GET all budgets for a user
router.get("/", async (req, res) => {
  try {
    const userId = req.query.userId;
    if (!userId) {
      return res.status(400).json({ message: "userId is required" });
    }
    const budgets = await Budget.find({ userId }).populate("category", "name type");
    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET budget by ID
router.get("/:id", async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id).populate("category", "name type");
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
  const { userId, category, amount, month, year } = req.body;

  if (!userId || !category || amount === undefined || !month || !year) {
    return res.status(400).json({ message: "All fields are required: userId, category, amount, month, year" });
  }

  const budget = new Budget({ userId, category, amount, month, year });
  try {
    const newBudget = await budget.save();
    res.status(201).json(newBudget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT update budget
router.put("/:id", async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id);
    if (!budget) {
      return res.status(404).json({ message: "Budget not found" });
    }

    const { userId, category, amount, month, year } = req.body;

    if (userId !== undefined) budget.userId = userId;
    if (category !== undefined) budget.category = category;
    if (amount !== undefined) budget.amount = amount;
    if (month !== undefined) budget.month = month;
    if (year !== undefined) budget.year = year;

    const updatedBudget = await budget.save();
    res.json(updatedBudget);
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