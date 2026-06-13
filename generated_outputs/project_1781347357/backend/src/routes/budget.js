const express = require("express");
const router = express.Router();
const Budget = require("../models/budget");

// GET all budgets for a user
router.get("/", async (req, res, next) => {
  try {
    const { userId } = req.query;
    if (!userId) {
      return res.status(400).json({ success: false, message: "userId is required" });
    }
    const budgets = await Budget.find({ userId }).populate("category", "name type color");
    res.json({ success: true, data: budgets });
  } catch (err) {
    next(err);
  }
});

// GET budget by ID
router.get("/:id", async (req, res, next) => {
  try {
    const budget = await Budget.findById(req.params.id).populate("category", "name type color");
    if (!budget) {
      return res.status(404).json({ success: false, message: "Budget not found" });
    }
    res.json({ success: true, data: budget });
  } catch (err) {
    next(err);
  }
});

// POST create budget
router.post("/", async (req, res, next) => {
  try {
    const { userId, category, amount, month, year } = req.body;
    if (!userId || !category || amount === undefined || !month || !year) {
      return res.status(400).json({ success: false, message: "All fields are required: userId, category, amount, month, year" });
    }
    const budget = new Budget({ userId, category, amount, month, year });
    await budget.save();
    await budget.populate("category", "name type color");
    res.status(201).json({ success: true, data: budget });
  } catch (err) {
    next(err);
  }
});

// PUT update budget
router.put("/:id", async (req, res, next) => {
  try {
    const budget = await Budget.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!budget) {
      return res.status(404).json({ success: false, message: "Budget not found" });
    }
    await budget.populate("category", "name type color");
    res.json({ success: true, data: budget });
  } catch (err) {
    next(err);
  }
});

// DELETE budget
router.delete("/:id", async (req, res, next) => {
  try {
    const budget = await Budget.findByIdAndDelete(req.params.id);
    if (!budget) {
      return res.status(404).json({ success: false, message: "Budget not found" });
    }
    res.json({ success: true, message: "Budget deleted successfully" });
  } catch (err) {
    next(err);
  }
});

// GET budgets by month and year for a user
router.get("/monthly", async (req, res, next) => {
  try {
    const { userId, month, year } = req.query;
    if (!userId || !month || !year) {
      return res.status(400).json({ success: false, message: "userId, month, and year are required" });
    }
    const budgets = await Budget.find({ userId, month: parseInt(month), year: parseInt(year) })
      .populate("category", "name type color");
    res.json({ success: true, data: budgets });
  } catch (err) {
    next(err);
  }
});

// GET total spending by category for a user in a month
router.get("/summary", async (req, res, next) => {
  try {
    const { userId, month, year } = req.query;
    if (!userId || !month || !year) {
      return res.status(400).json({ success: false, message: "userId, month, and year are required" });
    }
    const summary = await Budget.aggregate([
      { $match: { userId: mongoose.Types.ObjectId(userId), month: parseInt(month), year: parseInt(year) } },
      {
        $lookup: {
          from: "categories",
          localField: "category",
          foreignField: "_id",
          as: "categoryInfo"
        }
      },
      { $unwind: "$categoryInfo" },
      {
        $group: {
          _id: "$categoryInfo.name",
          total: { $sum: "$amount" },
          type: { $first: "$categoryInfo.type" },
          color: { $first: "$categoryInfo.color" }
        }
      }
    ]);
    res.json({ success: true, data: summary });
  } catch (err) {
    next(err);
  }
});

module.exports = router;