import { Server } from "socket.io";
class SocketConfig {
  constructor() {
    this.io = null;
    this.connectedUsers = new Map(); // Store connected users
    this.activeRooms = new Set(); // Track active chat rooms
  }

  /**
   * Initialize Socket.IO server
   * @param {Object} server - HTTP server instance
   * @returns {Object} Socket.IO instance
   */
  initialize(server) {
    this.io = new Server(server, {
      cors: {
        origin: [
          "http://localhost:5173",
          "https://your-backend-app.onrender.com",
        ], // Frontend origin
        credentials: true,
        methods: ["GET", "POST"],
      },
      transports: ["websocket", "polling"],
    });

    this.setupEventHandlers();
    console.log("✅ Socket.IO server initialized");

    return this.io;
  }

  /**
   * Setup all Socket.IO event handlers
   */
  setupEventHandlers() {
    this.io.on("connection", (socket) => {
      const { citizen_id } = socket.handshake.auth;
      console.log(
        `🔌 New socket connection: ${socket.id} (Citizen ID: ${citizen_id})`
      );
      this.connectedUsers.set(citizen_id, {
        socketId: socket.id,
      });
      // Handle user authentication/identification
      socket.on("user_join", (userData) => {
        this.handleUserJoin(socket, userData);
      });

      // Handle joining chat rooms
      socket.on("join_room", (roomId) => {
        this.handleJoinRoom(socket, roomId);
      });

      // Handle leaving chat rooms
      socket.on("leave_room", (roomId) => {
        this.handleLeaveRoom(socket, roomId);
      });

      // Handle chat messages
      socket.on("send_message", (messageData) => {
        this.handleSendMessage(socket, messageData);
      });

      // Handle typing indicators
      socket.on("typing_start", (data) => {
        this.handleTypingStart(socket, data);
      });

      socket.on("typing_stop", (data) => {
        this.handleTypingStop(socket, data);
      });

      // Handle loan application notifications
      socket.on("loan_status_update", (loanData) => {
        this.handleLoanStatusUpdate(socket, loanData);
      });

      // Handle user disconnect
      socket.on("disconnect", () => {
        this.handleUserDisconnect(socket);
      });

      // Handle error events
      socket.on("error", (error) => {
        console.error(`❌ Socket error for ${socket.id}:`, error);
      });
    });
  }

  /**
   * Handle user joining (authentication)
   */
  handleUserJoin(socket, userData) {
    try {
      const { userId, username, role } = userData;

      // Store user info
      this.connectedUsers.set(socket.id, {
        userId,
        username,
        role,
        joinedAt: new Date(),
        rooms: new Set(),
      });

      socket.userId = userId;
      socket.username = username;
      socket.role = role;

      // Join user to their personal room
      socket.join(`user_${userId}`);

      console.log(
        `👤 User joined: ${username} (${role}) - Socket: ${socket.id}`
      );

      // Notify user of successful connection
      socket.emit("user_joined", {
        success: true,
        message: "Connected successfully",
        socketId: socket.id,
      });

      // Broadcast user online status to relevant users
      this.broadcastUserStatus(userId, "online");
    } catch (error) {
      console.error("Error handling user join:", error);
      socket.emit("user_join_error", { error: error.message });
    }
  }

  /**
   * Handle joining chat rooms
   */
  handleJoinRoom(socket, roomId) {
    try {
      socket.join(roomId);
      this.activeRooms.add(roomId);

      // Update user's rooms
      const user = this.connectedUsers.get(socket.id);
      if (user) {
        user.rooms.add(roomId);
      }

      console.log(`📱 User ${socket.username} joined room: ${roomId}`);

      // Notify others in the room
      socket.to(roomId).emit("user_joined_room", {
        username: socket.username,
        userId: socket.userId,
        roomId,
      });

      // Send room info to user
      socket.emit("room_joined", {
        roomId,
        message: `Joined room ${roomId} successfully`,
      });
    } catch (error) {
      console.error("Error joining room:", error);
      socket.emit("room_join_error", { error: error.message });
    }
  }

  /**
   * Handle leaving chat rooms
   */
  handleLeaveRoom(socket, roomId) {
    try {
      socket.leave(roomId);

      // Update user's rooms
      const user = this.connectedUsers.get(socket.id);
      if (user) {
        user.rooms.delete(roomId);
      }

      console.log(`📤 User ${socket.username} left room: ${roomId}`);

      // Notify others in the room
      socket.to(roomId).emit("user_left_room", {
        username: socket.username,
        userId: socket.userId,
        roomId,
      });
    } catch (error) {
      console.error("Error leaving room:", error);
    }
  }

  /**
   * Handle sending messages
   */
  handleSendMessage(socket, messageData) {
    try {
      const { roomId, message, messageType = "text" } = messageData;

      const messagePayload = {
        id: Date.now().toString(),
        userId: socket.userId,
        username: socket.username,
        message,
        messageType,
        timestamp: new Date(),
        roomId,
      };

      // Send to room
      this.io.to(roomId).emit("new_message", messagePayload);

      console.log(`💬 Message sent in room ${roomId} by ${socket.username}`);

      // TODO: Save message to database
      // await saveMessageToDatabase(messagePayload);
    } catch (error) {
      console.error("Error sending message:", error);
      socket.emit("message_error", { error: error.message });
    }
  }

  /**
   * Handle typing indicators
   */
  handleTypingStart(socket, data) {
    const { roomId } = data;
    socket.to(roomId).emit("user_typing_start", {
      userId: socket.userId,
      username: socket.username,
      roomId,
    });
  }

  handleTypingStop(socket, data) {
    const { roomId } = data;
    socket.to(roomId).emit("user_typing_stop", {
      userId: socket.userId,
      username: socket.username,
      roomId,
    });
  }

  /**
   * Handle loan application status updates
   */
  handleLoanStatusUpdate(socket, loanData) {
    try {
      const { targetUserId, loanId, status, message } = loanData;

      // Send notification to specific user
      this.io.to(`user_${targetUserId}`).emit("loan_notification", {
        loanId,
        status,
        message,
        timestamp: new Date(),
      });

      console.log(
        `💰 Loan notification sent to user ${targetUserId}: ${status}`
      );
    } catch (error) {
      console.error("Error sending loan notification:", error);
    }
  }

  /**
   * Handle user disconnect
   */
  handleUserDisconnect(socket) {
    try {
      const user = this.connectedUsers.get(socket.id);

      if (user) {
        console.log(
          `👋 User disconnected: ${user.username} - Socket: ${socket.id}`
        );

        // Broadcast user offline status
        this.broadcastUserStatus(user.userId, "offline");

        // Clean up user data
        this.connectedUsers.delete(socket.id);
      } else {
        console.log(`❓ Unknown user disconnected: ${socket.id}`);
      }
    } catch (error) {
      console.error("Error handling disconnect:", error);
    }
  }

  /**
   * Broadcast user online/offline status
   */
  broadcastUserStatus(userId, status) {
    this.io.emit("user_status_update", {
      userId,
      status,
      timestamp: new Date(),
    });
  }

  /**
   * Send notification to specific user
   */
  sendNotificationToUser(userId, notification) {
    this.io.to(`user_${userId}`).emit("notification", {
      ...notification,
      timestamp: new Date(),
    });
  }

  /**
   * Send notification to all users
   */
  broadcastNotification(notification) {
    this.io.emit("broadcast_notification", {
      ...notification,
      timestamp: new Date(),
    });
  }

  /**
   * Get connected users count
   */
  getConnectedUsersCount() {
    return this.connectedUsers.size;
  }

  /**
   * Get user info by socket ID
   */
  getUserBySocketId(socketId) {
    return this.connectedUsers.get(socketId);
  }

  /**
   * Get all connected users
   */
  getAllConnectedUsers() {
    return Array.from(this.connectedUsers.values());
  }

  /**
   * Get Socket.IO instance
   */
  getIO() {
    return this.io;
  }
}

// Export singleton instance
const socketConfig = new SocketConfig();
export default socketConfig;
