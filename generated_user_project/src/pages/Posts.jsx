import React, { useEffect, useState } from 'react';
import api from '../services/api';

const Posts = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await api.get('/api/posts');
        setPosts(response.data);
      } catch (error) {
        console.error('Failed to fetch posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  if (loading) return <p>Loading posts...</p>;

  return (
    <div>
      <h2>Posts</h2>
      {posts.length > 0 ? (
        <ul>
          {posts.map(post => (
            <li key={post._id}>
              <h3>{post.title}</h3>
              <p>{post.content.substring(0, 100)}...</p>
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