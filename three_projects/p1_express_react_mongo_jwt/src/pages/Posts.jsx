import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Posts = () => {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await api.get('/api/posts');
        setPosts(response.data);
      } catch (error) {
        console.error('Failed to fetch posts:', error);
      }
    };

    fetchPosts();
  }, []);

  return (
    <div>
      <h2>Posts</h2>
      {posts.length === 0 ? (
        <p>No posts found.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {posts.map(post => (
            <li key={post._id} style={{ border: '1px solid #ddd', padding: '1rem', margin: '0.5rem 0', borderRadius: '4px' }}>
              <h3>{post.title}</h3>
              <p>{post.content.substring(0, 100)}{post.content.length > 100 ? '...' : ''}</p>
              <small>Author: {post.author}</small>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Posts;