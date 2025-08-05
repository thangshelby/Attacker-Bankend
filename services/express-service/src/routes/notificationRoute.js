import express from "express";
import * as NotificationController from "../controllers/notificationController.js";

const notificationRouter = express.Router();

notificationRouter.get("/", NotificationController.getNotifications);
notificationRouter.get(
  "/user/:citizen_id",
  NotificationController.getNotificationsByCitizenId
);

notificationRouter.post("/", NotificationController.createNotification);
notificationRouter.patch("/:id", NotificationController.updateNotification);
notificationRouter.post(
  "/mark_all_as_read",
  NotificationController.markAllAsRead
);
notificationRouter.delete("/:id", NotificationController.deleteNotification);
notificationRouter.get(
  "/global",
  NotificationController.getGlobalNotifications
);

export default notificationRouter;
