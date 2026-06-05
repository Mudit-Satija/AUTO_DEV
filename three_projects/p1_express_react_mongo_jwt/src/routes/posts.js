const express = require('express');
const router = express.Router();
const Post = require('../models/posts.js');

// Get all posts
router.get('/', async (req, res) => {
  try {
    const posts = await Post.find().sort({ createdAt: -1 });
    res.json(posts);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Get post by ID
router.get('/:id', async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });
    res.json(post);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Create new post
router.post('/', async (req, res) => {
  const { title, content, author, category } = req.body;

  try {
    const newPost = new Post({ title, content, author, category });
    await newPost.save();
    res.json(newPost);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Update post
router.put('/:id', async (req, res) => {
  const { title, content, author, category } = req.body;

  try {
    let post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });

    post.title = title || post.title;
    post.content = content || post.content;
    post.author = author || post.author;
    post.category = category || post.category;

    await post.save();
    res.json(post);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Delete post
router.delete('/:id', async (req, res) => {
  try {
    const post = await Post.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });

    await post.remove();
    res.json({ msg: 'Post removed' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;