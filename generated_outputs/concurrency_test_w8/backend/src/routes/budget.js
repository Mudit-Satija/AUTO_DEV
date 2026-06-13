const express = require("express");
const router = express.Router();
const Budget = require("../models/budget");

// GET all budgets for a user
router.get("/", async (req, res) => {
  try {
    const budgets = await Budget.find({ userId: req.user._id })
      .populate("category", "name color")
      .sort({ year: -1, month: -1 });
    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET budget by ID
router.get("/:id", async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id)
      .populate("category", "name color");
    if (!budget) return res.status(404).json({ message: "Budget not found" });
    if (budget.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });
    res.json(budget);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// POST create budget
router.post("/", async (req, res) => {
  const { category, amount, month, year } = req.body;

  try {
    const budget = new Budget({
      userId: req.user._id,
      category,
      amount,
      month,
      year,
    });

    const savedBudget = await budget.save();
    res.status(201).json(savedBudget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT update budget
router.put("/:id", async (req, res) => {
  try {
    const budget = await Budget.findById(req.params.id);
    if (!budget) return res.status(404).json({ message: "Budget not found" });
    if (budget.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });

    const { category, amount, month, year } = req.body;
    if (category) budget.category = category;
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
    const budget = await Budget.findById(req.params.id);
    if (!budget) return res.status(404).json({ message: "Budget not found" });
    if (budget.userId.toString() !== req.user._id.toString())
      return res.status(403).json({ message: "Unauthorized" });

    await budget.remove();
    res.json({ message: "Budget deleted" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET budgets by month and year for analytics
router.get("/analytics/:year/:month", async (req, res) => {
  try {
    const { year, month } = req.params;
    const budgets = await Budget.find({
      userId: req.user._id,
      year: parseInt(year),
      month: parseInt(month),
    })
      .populate("category", "name color")
      .sort("category");

    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;