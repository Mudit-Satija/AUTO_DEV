const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const UserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

const PostSchema = new mongoose.Schema({
  title: { type: String, required: true },
  content: { type: String, required: true },
  author: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

const CommentSchema = new mongoose.Schema({
  content: { type: String, required: true },
  author: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  post: { type: mongoose.Schema.Types.ObjectId, ref: 'Post', required: true },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', UserSchema);
const Post = mongoose.model('Post', PostSchema);
const Comment = mongoose.model('Comment', CommentSchema);

const seedData = async () => {
  try {
    await mongoose.connect('mongodb://localhost:27017/yourapp-dev', {
      useNewUrlParser: true,
      useUnifiedTopology: true
    });

    console.log('Connected to MongoDB');

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash('password123', salt);

    const user1 = new User({
      username: 'john_doe',
      email: 'john@example.com',
      password: hashedPassword
    });

    const user2 = new User({
      username: 'jane_smith',
      email: 'jane@example.com',
      password: hashedPassword
    });

    await User.deleteMany({});
    await Post.deleteMany({});
    await Comment.deleteMany({});

    const savedUser1 = await user1.save();
    const savedUser2 = await user2.save();

    const post1 = new Post({
      title: 'First Post',
      content: 'This is the content of the first post.',
      author: savedUser1._id
    });

    const post2 = new Post({
      title: 'Second Post',
      content: 'This is the content of the second post.',
      author: savedUser2._id
    });

    const savedPost1 = await post1.save();
    const savedPost2 = await post2.save();

    const comment1 = new Comment({
      content: 'Great post!',
      author: savedUser2._id,
      post: savedPost1._id
    });

    const comment2 = new Comment({
      content: 'I agree with this.',
      author: savedUser1._id,
      post: savedPost2._id
    });

    await comment1.save();
    await comment2.save();

    console.log('Seed data successfully inserted');
    process.exit(0);
  } catch (error) {
    console.error('Error seeding data:', error);
    process.exit(1);
  }
};

seedData();