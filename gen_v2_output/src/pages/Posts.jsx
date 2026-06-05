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
      {posts.length > 0 ? (
        <ul>
          {posts.map(post => (
            <li key={post._id}>
              <strong>{post.title}</strong> - {post.author}
            </li>
          ))}
        </ul>
      ) : (
        <p>No posts found.</p>
      )}
    </div>
  );
};

export default Posts;