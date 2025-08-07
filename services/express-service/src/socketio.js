import { Server } from "socket.io"
import { createServer } from "node:http";
import { app } from "./server.js"; // Import the app from server.js
const server = createServer(app); // Create an HTTP server using the Express app
const io = new Server(server);

io.on("connection", (socket) => {
  console.log("a user connected");
});
