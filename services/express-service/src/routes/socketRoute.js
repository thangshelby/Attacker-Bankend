import express from "express";
import * as socketController from "../controllers/socketController.js";
import jwtMiddleware from "../middleware/middleware.js";

const socketRouter = express.Router();

/**
 * @swagger
 * components:
 *   schemas:
 *     NotificationRequest:
 *       type: object
 *       required:
 *         - userId
 *         - notification
 *       properties:
 *         userId:
 *           type: string
 *           description: Target user ID
 *         notification:
 *           type: object
 *           properties:
 *             type:
 *               type: string
 *               example: "info"
 *             title:
 *               type: string
 *               example: "Notification Title"
 *             message:
 *               type: string
 *               example: "Your loan application has been updated"
 *             data:
 *               type: object
 *               description: Additional notification data
 *     BroadcastRequest:
 *       type: object
 *       required:
 *         - notification
 *       properties:
 *         notification:
 *           type: object
 *           properties:
 *             type:
 *               type: string
 *               example: "announcement"
 *             title:
 *               type: string
 *               example: "System Announcement"
 *             message:
 *               type: string
 *               example: "System maintenance scheduled"
 *     LoanStatusRequest:
 *       type: object
 *       required:
 *         - userId
 *         - loanId
 *         - status
 *       properties:
 *         userId:
 *           type: string
 *           description: User ID to notify
 *         loanId:
 *           type: string
 *           description: Loan application ID
 *         status:
 *           type: string
 *           enum: [pending, approved, rejected, processing]
 *           description: New loan status
 *         message:
 *           type: string
 *           description: Optional custom message
 */

/**
 * @swagger
 * /api/v1/socket/notify-user:
 *   post:
 *     summary: Send notification to specific user via Socket.IO
 *     tags: [Socket.IO]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/NotificationRequest'
 *     responses:
 *       200:
 *         description: Notification sent successfully
 *       400:
 *         description: Missing required data
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Server error
 */
socketRouter.post("/notify-user", jwtMiddleware, socketController.sendNotificationToUser);

/**
 * @swagger
 * /api/v1/socket/broadcast:
 *   post:
 *     summary: Broadcast notification to all connected users
 *     tags: [Socket.IO]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/BroadcastRequest'
 *     responses:
 *       200:
 *         description: Notification broadcasted successfully
 *       400:
 *         description: Missing notification data
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Server error
 */
socketRouter.post("/broadcast", jwtMiddleware, socketController.broadcastNotification);

/**
 * @swagger
 * /api/v1/socket/loan-status:
 *   post:
 *     summary: Send loan status update to user
 *     tags: [Socket.IO]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/LoanStatusRequest'
 *     responses:
 *       200:
 *         description: Loan status update sent successfully
 *       400:
 *         description: Missing required fields
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Server error
 */
socketRouter.post("/loan-status", jwtMiddleware, socketController.sendLoanStatusUpdate);

/**
 * @swagger
 * /api/v1/socket/stats:
 *   get:
 *     summary: Get Socket.IO server statistics
 *     tags: [Socket.IO]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Socket.IO statistics
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                 statistics:
 *                   type: object
 *                   properties:
 *                     connectedUsers:
 *                       type: number
 *                     totalConnections:
 *                       type: number
 *                     serverUptime:
 *                       type: number
 *                     users:
 *                       type: array
 *                       items:
 *                         type: object
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Server error
 */
socketRouter.get("/stats", jwtMiddleware, socketController.getSocketStats);

/**
 * @swagger
 * /api/v1/socket/python-notification:
 *   post:
 *     summary: Handle notification from Python service (MAS workflow)
 *     tags: [Socket.IO]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - message
 *               - request_id
 *               - decision
 *             properties:
 *               message:
 *                 type: string
 *                 example: "MAS conversation completed"
 *               request_id:
 *                 type: string
 *                 example: "uuid-12345"
 *               decision:
 *                 type: string
 *                 enum: [approve, reject]
 *               timestamp:
 *                 type: number
 *                 example: 1691234567.89
 *     responses:
 *       200:
 *         description: Python notification processed successfully
 *       400:
 *         description: Missing required data
 *       500:
 *         description: Server error
 */
socketRouter.post("/python-notification", socketController.handlePythonNotification);

/**
 * @swagger
 * /api/v1/socket/system-message:
 *   post:
 *     summary: Send system message to chat room
 *     tags: [Socket.IO]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - roomId
 *               - message
 *             properties:
 *               roomId:
 *                 type: string
 *                 example: "room_123"
 *               message:
 *                 type: string
 *                 example: "Welcome to the chat room!"
 *               messageType:
 *                 type: string
 *                 default: "system"
 *                 example: "system"
 *     responses:
 *       200:
 *         description: System message sent successfully
 *       400:
 *         description: Missing required data
 *       401:
 *         description: Unauthorized
 *       500:
 *         description: Server error
 */
socketRouter.post("/system-message", jwtMiddleware, socketController.sendSystemMessage);

export default socketRouter;
