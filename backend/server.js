const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const multer = require('multer');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// CRITICAL: Middleware order matters!
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Debug logger
app.use((req, res, next) => {
  console.log('--- Request ---');
  console.log('Method:', req.method);
  console.log('URL:', req.url);
  console.log('Body:', req.body);
  console.log('---------------');
  next();
});

// File upload config
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files allowed!'), false);
    }
  }
});

// User Schema
const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email']
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

// Auth middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'] || req.headers['Authorization'];
  if (!authHeader) {
    return res.status(401).json({ error: 'Access denied' });
  }

  const token = authHeader.startsWith('Bearer ') ? authHeader.split(' ')[1] : authHeader;
  if (!token) {
    return res.status(401).json({ error: 'Access denied' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET || 'secret-key');
    req.user = payload;
    next();
  } catch (err) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// ============= ROUTES =============

// Health check
app.get('/api/health', (req, res) => {
  console.log('Health check hit');
  res.json({ 
    status: 'ok', 
    message: 'Backend is running',
    timestamp: new Date().toISOString()
  });
});

// Register
app.post('/register', async (req, res) => {
  console.log('=== REGISTER ROUTE HIT ===');
  console.log('Body received:', req.body);
  
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      console.log('Missing fields');
      return res.status(400).json({ error: 'Email and password required' });
    }

    if (password.length < 6) {
      console.log('Password too short');
      return res.status(400).json({ error: 'Password must be 6+ characters' });
    }

    // Check existing user
    console.log('Checking for existing user...');
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      console.log('Email already exists');
      return res.status(400).json({ error: 'Email already exists' });
    }

    // Create user
    console.log('Hashing password...');
    const hashedPassword = await bcrypt.hash(password, 12);
    
    console.log('Creating user...');
    const user = new User({ email, password: hashedPassword });
    await user.save();

    // Generate token
    console.log('Generating token...');
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET || 'secret-key',
      { expiresIn: '7d' }
    );

    console.log('SUCCESS - User registered:', email);
    return res.status(201).json({
      message: 'Account created!',
      token,
      user: { email: user.email }
    });

  } catch (error) {
    console.error('REGISTRATION ERROR:', error);
    
    if (error.code === 11000) {
      return res.status(400).json({ error: 'Email already exists' });
    }
    
    if (error.name === 'ValidationError') {
      return res.status(400).json({ error: error.message });
    }
    
    return res.status(500).json({ error: 'Registration failed: ' + error.message });
  }
});

// Login
app.post('/login', async (req, res) => {
  console.log('=== LOGIN ROUTE HIT ===');
  console.log('Body received:', req.body);
  
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET || 'secret-key',
      { expiresIn: '7d' }
    );

    console.log('SUCCESS - Login successful:', email);
    return res.json({
      message: 'Login successful!',
      token,
      user: { email: user.email }
    });

  } catch (error) {
    console.error('LOGIN ERROR:', error);
    return res.status(500).json({ error: 'Login failed' });
  }
});

// File upload
app.post('/api/upload', authenticateToken, upload.single('pdf'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF uploaded' });
    }

    console.log('PDF uploaded:', req.file.originalname);
    return res.json({
      message: 'PDF uploaded successfully',
      fileName: req.file.originalname,
      fileSize: req.file.size
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ error: 'Upload failed' });
  }
});

// Get user
app.get('/api/user', authenticateToken, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId).select('-password');
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    return res.json({ 
      user: { 
        email: user.email, 
        createdAt: user.createdAt 
      } 
    });
  } catch (error) {
    console.error('Get user error:', error);
    return res.status(500).json({ error: 'Failed to get user' });
  }
});

// Error handler
app.use((err, req, res, next) => {
  console.error('ERROR HANDLER:', err);
  
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({ error: 'File too large (5MB max)' });
  }
  
  if (err.message === 'Only PDF files allowed!') {
    return res.status(400).json({ error: 'Only PDF files allowed' });
  }
  
  if (err instanceof SyntaxError && err.status === 400) {
    return res.status(400).json({ error: 'Invalid JSON' });
  }
  
  return res.status(500).json({ error: 'Server error' });
});

// MongoDB connection and server start
async function startServer() {
  try {
    const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017/cramit';
    console.log('Connecting to MongoDB...');
    await mongoose.connect(uri);
    console.log('Connected to MongoDB successfully');
    
    app.listen(PORT, () => {
      console.log('=============================');
      console.log(`Server running on http://localhost:${PORT}`);
      console.log(`Health: http://localhost:${PORT}/api/health`);
      console.log(`Register: POST http://localhost:${PORT}/register`);
      console.log(`Login: POST http://localhost:${PORT}/login`);
      console.log('=============================');
    });
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
}

startServer();