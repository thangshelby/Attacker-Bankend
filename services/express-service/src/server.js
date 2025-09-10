import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import routes from "./routes/index.js";
import setupSwagger from "./swagger.js";
import bodyParser from "body-parser";
import { createServer } from "node:http";
import cookieParser from "cookie-parser";
import { connectDatabase } from "./config/connectDB.js";
import multer from "multer";
import socketConfig from "./config/socket.js";

dotenv.config();

const app = express();
const server = createServer(app);

// Initialize Socket.IO
const io = socketConfig.initialize(server);

// Parse application/json
app.use(bodyParser.json());

// Parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(
  cors({
    origin: [
      "http://localhost:5173",
      "https://attacker-frontend-1.onrender.com",
    ], // Frontend origin
    credentials: true, // Allow cookies and credentials
  })
);

export const db = connectDatabase();
export const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // giới hạn 10MB (tuỳ bạn)
});

// Make Socket.IO available to other parts of the app
export { io, socketConfig };

app.use(cookieParser());

setupSwagger(app);
routes(app);

const PORT = process.env.PORT || 5000;

server.listen(PORT, () => {
  console.log(`🚀 Server listening at http://localhost:${PORT}`);
  console.log(`📊 Swagger UI: http://localhost:${PORT}/api-docs`);
  console.log(`🔌 Socket.IO: Ready for connections`);

  // Open Swagger UI in the browser automatically
  // open("http://localhost:5000/api-docs");
});
