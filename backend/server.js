const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const multer = require("multer");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const helmet = require("helmet");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

/* ====================== SECURITY MIDDLEWARE ====================== */

app.use(helmet());
app.use(cors({
  origin: "*", // tighten later if needed
  methods: ["GET", "POST"]
}));
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true }));

/* ====================== RATE LIMITERS ====================== */

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { error: "Too many attempts. Try again later." }
});

const uploadLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10
});

/* ====================== FILE UPLOAD CONFIG ====================== */

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (_, file, cb) => {
    if (file.mimetype === "application/pdf") cb(null, true);
    else cb(new Error("Only PDF files allowed"));
  }
});

/* ====================== DATABASE ====================== */

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, "Invalid email"]
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model("User", userSchema);

/* ====================== AUTH HELPERS ====================== */

function generateToken(user) {
  if (!process.env.JWT_SECRET) {
    throw new Error("JWT_SECRET not configured");
  }

  return jwt.sign(
    { userId: user._id, email: user.email },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );
}

function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "Unauthorized" });

  const token = authHeader.split(" ")[1];
  if (!token) return res.status(401).json({ error: "Unauthorized" });

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(403).json({ error: "Invalid or expired token" });
  }
}

/* ====================== ROUTES ====================== */

// Health
app.get("/api/health", (_, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Register
app.post("/api/auth/register", authLimiter, async (req, res) => {
  const { email, password } = req.body;

  if (typeof email !== "string" || typeof password !== "string") {
    return res.status(400).json({ error: "Invalid input" });
  }

  if (password.length < 6) {
    return res.status(400).json({ error: "Password too short" });
  }

  try {
    const exists = await User.findOne({ email });
    if (exists) {
      return res.status(400).json({ error: "Email already registered" });
    }

    const hashed = await bcrypt.hash(password, 12);
    const user = await User.create({ email, password: hashed });

    const token = generateToken(user);

    res.status(201).json({
      message: "Account created",
      token,
      user: { email: user.email }
    });

  } catch (err) {
    res.status(500).json({ error: "Registration failed" });
  }
});

// Login
app.post("/api/auth/login", authLimiter, async (req, res) => {
  const { email, password } = req.body;

  if (typeof email !== "string" || typeof password !== "string") {
    return res.status(400).json({ error: "Invalid input" });
  }

  try {
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const ok = await bcrypt.compare(password, user.password);
    if (!ok) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const token = generateToken(user);

    res.json({
      message: "Login successful",
      token,
      user: { email: user.email }
    });

  } catch {
    res.status(500).json({ error: "Login failed" });
  }
});

// Upload (future use)
app.post(
  "/api/upload",
  authenticate,
  uploadLimiter,
  upload.single("pdf"),
  (req, res) => {
    if (!req.file) {
      return res.status(400).json({ error: "No PDF uploaded" });
    }

    res.json({
      message: "PDF accepted",
      name: req.file.originalname,
      size: req.file.size
    });
  }
);

/* ====================== GLOBAL ERROR HANDLER ====================== */

app.use((err, _, res, __) => {
  if (err.message.includes("PDF")) {
    return res.status(400).json({ error: err.message });
  }
  res.status(500).json({ error: "Server error" });
});

/* ====================== START SERVER ====================== */

async function start() {
  await mongoose.connect(process.env.MONGODB_URI);
  app.listen(PORT, () =>
    console.log(`Server running on port ${PORT}`)
  );
}

start();
