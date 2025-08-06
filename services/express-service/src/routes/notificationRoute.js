import { Router } from "express";
import {
  getAllNotifications,
  getNotificationsByCitizenId,
  createNotification,
  updateNotification,
  markAllAsRead,
  deleteNotification,
} from "../controllers/notificationController.js";

const router = Router();

// GET all notifications
router.get("/", getAllNotifications);

// GET notifications by citizen ID
router.get("/user/:citizen_id", getNotificationsByCitizenId);

// POST create new notification
router.post("/", createNotification);

// PATCH update notification
router.patch("/:notification_id", updateNotification);

// POST mark all notifications as read
router.post("/mark_all_as_read", markAllAsRead);

// DELETE notification
router.delete("/:notification_id", deleteNotification);

export default router;
