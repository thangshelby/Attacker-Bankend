import socketConfig from "../config/socket.js";

/**
 * Socket Controller - Handle Socket.IO operations from API endpoints
 */

/**
 * Send notification to specific user
 */
export const sendNotificationToUser = (req, res) => {
  try {
    const { userId, notification } = req.body;

    if (!userId || !notification) {
      return res.status(400).json({
        success: false,
        message: "Missing userId or notification data"
      });
    }

    // Send notification via Socket.IO
    socketConfig.sendNotificationToUser(userId, notification);

    return res.status(200).json({
      success: true,
      message: "Notification sent successfully",
      recipient: userId
    });

  } catch (error) {
    console.error("Error sending notification:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to send notification",
      error: error.message
    });
  }
};

/**
 * Broadcast notification to all connected users
 */
export const broadcastNotification = (req, res) => {
  try {
    const { notification } = req.body;

    if (!notification) {
      return res.status(400).json({
        success: false,
        message: "Missing notification data"
      });
    }

    // Broadcast via Socket.IO
    socketConfig.broadcastNotification(notification);

    return res.status(200).json({
      success: true,
      message: "Notification broadcasted successfully",
      recipients: "all_users"
    });

  } catch (error) {
    console.error("Error broadcasting notification:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to broadcast notification",
      error: error.message
    });
  }
};

/**
 * Send loan status update to user
 */
export const sendLoanStatusUpdate = (req, res) => {
  try {
    const { userId, loanId, status, message } = req.body;

    if (!userId || !loanId || !status) {
      return res.status(400).json({
        success: false,
        message: "Missing required fields: userId, loanId, status"
      });
    }

    const notification = {
      type: "loan_status_update",
      loanId,
      status,
      message: message || `Loan application ${status}`,
      timestamp: new Date()
    };

    // Send via Socket.IO
    socketConfig.sendNotificationToUser(userId, notification);

    return res.status(200).json({
      success: true,
      message: "Loan status update sent successfully",
      recipient: userId,
      loanId,
      status
    });

  } catch (error) {
    console.error("Error sending loan status update:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to send loan status update",
      error: error.message
    });
  }
};

/**
 * Get Socket.IO server statistics
 */
export const getSocketStats = (req, res) => {
  try {
    const connectedUsersCount = socketConfig.getConnectedUsersCount();
    const connectedUsers = socketConfig.getAllConnectedUsers();

    return res.status(200).json({
      success: true,
      statistics: {
        connectedUsers: connectedUsersCount,
        totalConnections: connectedUsers.length,
        serverUptime: process.uptime(),
        users: connectedUsers.map(user => ({
          userId: user.userId,
          username: user.username,
          role: user.role,
          joinedAt: user.joinedAt,
          roomsCount: user.rooms.size
        }))
      }
    });

  } catch (error) {
    console.error("Error getting socket stats:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to get socket statistics",
      error: error.message
    });
  }
};

/**
 * Handle Python service notifications (from MAS workflow)
 */
export const handlePythonNotification = (req, res) => {
  try {
    const { message, request_id, decision, timestamp } = req.body;

    console.log(`📨 Python notification: ${decision} for request ${request_id}`);

    // Broadcast MAS decision result to all admins or specific users
    const notification = {
      type: "mas_decision",
      request_id,
      decision,
      message,
      timestamp,
      source: "python_service"
    };

    // Broadcast to all connected users (you can modify this to target specific users)
    socketConfig.broadcastNotification(notification);

    return res.status(200).json({
      success: true,
      message: "Python notification processed successfully",
      request_id
    });

  } catch (error) {
    console.error("Error handling Python notification:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to process Python notification",
      error: error.message
    });
  }
};

/**
 * Send chat message via API (for system messages)
 */
export const sendSystemMessage = (req, res) => {
  try {
    const { roomId, message, messageType = "system" } = req.body;

    if (!roomId || !message) {
      return res.status(400).json({
        success: false,
        message: "Missing roomId or message"
      });
    }

    const messagePayload = {
      id: Date.now().toString(),
      userId: "system",
      username: "System",
      message,
      messageType,
      timestamp: new Date(),
      roomId
    };

    // Send via Socket.IO
    const io = socketConfig.getIO();
    io.to(roomId).emit("new_message", messagePayload);

    return res.status(200).json({
      success: true,
      message: "System message sent successfully",
      roomId
    });

  } catch (error) {
    console.error("Error sending system message:", error);
    return res.status(500).json({
      success: false,
      message: "Failed to send system message",
      error: error.message
    });
  }
};
