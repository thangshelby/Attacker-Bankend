import { db } from "../server.js";

export const getAllNotifications = async (req, res) => {
  try {
    const results = await db.then(async (db) => {
      const notifications = await db
        .collection("notifications")
        .find({})
        .sort({ created_at: -1 })
        .toArray();
      return notifications;
    });

    res.status(200).json({
      message: "Notifications fetched successfully",
      data: results,
      status: true,
    });
  } catch (error) {
    console.error("Error fetching notifications:", error);
    res.status(500).json({
      message: "Failed to fetch notifications",
      error: error.message,
      status: false,
    });
  }
};

export const getNotificationsByCitizenId = async (req, res) => {
  const { citizen_id } = req.params;

  try {
    const results = await db.then(async (db) => {
      const notifications = await db
        .collection("notifications")
        .find({ citizen_id: citizen_id })
        .sort({ created_at: -1 })
        .toArray();
      return notifications;
    });

    res.status(200).json({
      message: "User notifications fetched successfully",
      data: results,
      status: true,
    });
  } catch (error) {
    console.error("Error fetching user notifications:", error);
    res.status(500).json({
      message: "Failed to fetch user notifications",
      error: error.message,
      status: false,
    });
  }
};

export const createNotification = async (newNotification) => {
  try {
    const result = await db.then(async (db) => {
      const insertResult = await db
        .collection("notifications")
        .insertOne(newNotification);
      return insertResult;
    });
  } catch (error) {
    console.error("Error creating notification:", error);
    res.status(500).json({
      message: "Failed to create notification",
      error: error.message,
      status: false,
    });
  }
};

export const updateNotification = async (req, res) => {
  const { notification_id } = req.params;
  const updateData = { ...req.body, updated_at: new Date() };

  try {
    const result = await db.then(async (db) => {
      const { ObjectId } = await import("mongodb");
      const updateResult = await db
        .collection("notifications")
        .updateOne(
          { _id: new ObjectId(notification_id) },
          { $set: updateData }
        );
      return updateResult;
    });

    if (result.matchedCount === 0) {
      return res.status(404).json({
        message: "Notification not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "Notification updated successfully",
      status: true,
    });
  } catch (error) {
    console.error("Error updating notification:", error);
    res.status(500).json({
      message: "Failed to update notification",
      error: error.message,
      status: false,
    });
  }
};

export const markAllAsRead = async (req, res) => {
  const { citizen_id } = req.body;

  try {
    const result = await db.then(async (db) => {
      const updateResult = await db
        .collection("notifications")
        .updateMany(
          { citizen_id: citizen_id },
          { $set: { is_read: true, updated_at: new Date() } }
        );
      return updateResult;
    });

    res.status(200).json({
      message: `${result.modifiedCount} notifications marked as read`,
      status: true,
    });
  } catch (error) {
    console.error("Error marking notifications as read:", error);
    res.status(500).json({
      message: "Failed to mark notifications as read",
      error: error.message,
      status: false,
    });
  }
};

export const deleteNotification = async (req, res) => {
  const { notification_id } = req.params;

  try {
    const result = await db.then(async (db) => {
      const { ObjectId } = await import("mongodb");
      const deleteResult = await db
        .collection("notifications")
        .deleteOne({ _id: new ObjectId(notification_id) });
      return deleteResult;
    });

    if (result.deletedCount === 0) {
      return res.status(404).json({
        message: "Notification not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "Notification deleted successfully",
      status: true,
    });
  } catch (error) {
    console.error("Error deleting notification:", error);
    res.status(500).json({
      message: "Failed to delete notification",
      error: error.message,
      status: false,
    });
  }
};
