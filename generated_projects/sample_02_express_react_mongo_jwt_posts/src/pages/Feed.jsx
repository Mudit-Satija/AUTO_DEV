import { useEffect, useState } from 'react';
import api from '../services/api';

function Feed() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const response = await api.get('/posts');
        setPosts(response.data);
      } catch (error) {
        console.error('Failed to fetch posts:', error);
      }
    };

    fetchPosts();
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Feed</h1>
      {posts.map(post => (
        <div key={post._id} style={{ border: '1px solid #ddd', margin: '10px 0', padding: '10px' }}>
          <h3>{post.title}</h3>
          <p>{post.content}</p>
        </div>
      ))}
    </div>
  );
}

export default Feed;