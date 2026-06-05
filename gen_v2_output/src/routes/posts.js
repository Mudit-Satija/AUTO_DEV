const express = require('express');
const router = express.Router();
const Posts = require('../models/posts.js');

// Get all posts
router.get('/', async (req, res) => {
  try {
    const posts = await Posts.find().sort({ createdAt: -1 });
    res.json(posts);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Get post by ID
router.get('/:id', async (req, res) => {
  try {
    const post = await Posts.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });
    res.json(post);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Post not found' });
    }
    res.status(500).send('Server error');
  }
});

// Create new post
router.post('/', async (req, res) => {
  const { title, content, author, tags } = req.body;

  try {
    const newPost = new Posts({
      title,
      content,
      author,
      tags
    });

    const post = await newPost.save();
    res.json(post);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// Update post
router.put('/:id', async (req, res) => {
  const { title, content, author, tags } = req.body;

  try {
    let post = await Posts.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });

    post.title = title || post.title;
    post.content = content || post.content;
    post.author = author || post.author;
    post.tags = tags || post.tags;

    post = await post.save();
    res.json(post);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Post not found' });
    }
    res.status(500).send('Server error');
  }
});

// Delete post
router.delete('/:id', async (req, res) => {
  try {
    const post = await Posts.findById(req.params.id);
    if (!post) return res.status(404).json({ msg: 'Post not found' });

    await post.remove();
    res.json({ msg: 'Post removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Post not found' });
    }
    res.status(500).send('Server error');
  }
});

module.exports = router;