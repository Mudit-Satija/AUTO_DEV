const express = require("express");
const router = express.Router();
const Budget = require("../models/budget");

// GET /api/budgets - Get all budgets for a user
router.get("/", async (req, res) => {
  try {
    const userId = req.query.userId;
    if (!userId) {
      return res.status(400).json({ message: "userId is required" });
    }

    const budgets = await Budget.find({ userId }).populate("category", "name type color");
    res.json(budgets);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// GET /api/budgets/:id - Get budget by ID
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

// POST /api/budgets - Create a new budget
router.post("/", async (req, res) => {
  try {
    const budget = new Budget(req.body);
    const createdBudget = await budget.save();
    res.status(201).json(createdBudget);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// PUT /api/budgets/:id - Update budget
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

// DELETE /api/budgets/:id - Delete budget
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

// GET /api/budgets/monthly - Get monthly budget summary for user
router.get("/monthly", async (req, res) => {
  try {
    const userId = req.query.userId;
    const month = req.query.month;
    const year = req.query.year;

    if (!userId || !month || !year) {
      return res.status(400).json({ message: "userId, month, and year are required" });
    }

    const budgets = await Budget.find({ userId, month: parseInt(month), year: parseInt(year) })
      .populate("category", "name type color");

    const summary = {
      totalBudget: 0,
      incomeBudget: 0,
      expenseBudget: 0,
      categories: [],
    };

    budgets.forEach(budget => {
      summary.totalBudget += budget.amount;
      if (budget.category.type === 'income') {
        summary.incomeBudget += budget.amount;
      } else {
        summary.expenseBudget += budget.amount;
      }
      summary.categories.push({
        id: budget.category._id,
        name: budget.category.name,
        type: budget.category.type,
        color: budget.category.color,
        amount: budget.amount,
      });
    });

    res.json(summary);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;