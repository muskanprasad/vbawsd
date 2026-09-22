// src/server.js
require("dotenv").config();
const express = require("express");
const connectDB = require("./config/db");
const cors = require("cors");

const authRoutes = require("./routes/auth");
const voiceRoutes = require("./routes/voice");

const app = express();
const PORT = process.env.PORT || "https://vbawsd-server.onrender.com";

// Connect MongoDB
connectDB();

/* ---------- CORS (allow React dev origin) ---------- */
app.use(
  cors({
    origin: "https://vbawsd-client.onrender.com", // your Vite dev server
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

/* ---------- RAW AUDIO FOR WAV (voice enroll) ---------- */
app.use(
  express.raw({
    type: "audio/wav",
    limit: "15mb",
  })
);

/* ---------- JSON FOR NORMAL APIs ---------- */
app.use(express.json({ limit: "5mb" }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/voice", voiceRoutes);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
