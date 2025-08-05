import NotificationModel from "../models/notifacationModel.js";
/**
 * Create a new notification
 */
export const createNotification = async (req, res) => {
  const { header, content, citizen_id, is_global, type, icon } = req.body;

  try {
    const notification = await NotificationModel.create({
      header,
      content,
      citizen_id: is_global ? null : citizen_id || null,
      is_global: is_global || false,
      type: type || "info",
      icon: icon || "",
    });

    res.status(201).json({
      message: "Notification created successfully",
      data: {
        notification,
      },
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to create notification",
      error: error.message,
    });
  }
};

/**
 * Get all notifications (optionally filtered by user or global)
 */
export const getNotifications = async (req, res) => {
  const { citizen_id, is_global } = req.query;

  try {
    const filter = {};
    if (citizen_id) filter.citizen_id = citizen_id;
    if (is_global !== undefined) filter.is_global = is_global === "true";

    const notifications = await NotificationModel.find(filter).sort({
      created_at: -1,
    });

    return res.status(201).json({
      message: "Notification fetched successfully",
      data: {
        notifications,
      },
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to retrieve notifications",
      error: error.message,
    });
  }
};

/**
 * Get a single notification by ID
 */
export const getNotificationById = async (req, res) => {
  const { id } = req.params;

  try {
    const notification = await NotificationModel.findById(id);

    if (!notification) {
      return res.status(404).json({ message: "Notification not found" });
    }

    res.status(200).json(notification);
  } catch (error) {
    res.status(500).json({
      message: "Failed to retrieve notification",
      error: error.message,
    });
  }
};

/**
 * Update a notification
 */
export const updateNotification = async (req, res) => {
  const { id } = req.params;
  const { header, content, citizen_id, is_global, type, icon, is_read } =
    req.body;

  try {
    const notification = await NotificationModel.findById(id);

    if (!notification) {
      return res.status(404).json({ message: "Notification not found" });
    }

    notification.header = header ?? notification.header;
    notification.content = content ?? notification.content;
    notification.citizen_id = is_global
      ? null
      : citizen_id ?? notification.citizen_id;
    notification.is_global = is_global ?? notification.is_global;
    notification.type = type ?? notification.type;
    notification.icon = icon ?? notification.icon;
    notification.is_read = is_read ?? notification.is_read;
    notification.updated_at = new Date();

    await notification.save();

    res.status(200).json({
      message: "Notification updated successfully",
      data: {
        notification,
      },
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to update notification",
      error: error.message,
    });
  }
};

export const markAllAsRead = async (req, res) => {
  const { citizen_id } = req.body;
  try {
    const notifications = await NotificationModel.updateMany(
      {
        citizen_id,
        is_read: false,
      },
      { $set: { is_read: true } }
    );
    return res.status(200).json({
      message: "Update successfully!",
      data: {
        notifications,
      },
    });
  } catch (error) {}
};

/**
 * Delete a notification
 */
export const deleteNotification = async (req, res) => {
  const { id } = req.params;

  try {
    const notification = await NotificationModel.findByIdAndDelete(id);

    if (!notification) {
      return res.status(404).json({ message: "Notification not found" });
    }

    res.status(200).json({ message: "Notification deleted successfully" });
  } catch (error) {
    res.status(500).json({
      message: "Failed to delete notification",
      error: error.message,
    });
  }
};

/**
 * Get global notifications only
 */
export const getGlobalNotifications = async (req, res) => {
  try {
    const notifications = await NotificationModel.find({
      is_global: true,
    }).sort({
      created_at: -1,
    });

    res.status(200).json(notifications);
  } catch (error) {
    res.status(500).json({
      message: "Failed to retrieve global notifications",
      error: error.message,
    });
  }
};

/**
 * Get notifications by citizen_id
 */
export const getNotificationsByCitizenId = async (req, res) => {
  const { citizen_id } = req.params;

  try {
    const notifications = await NotificationModel.find({
      citizen_id: citizen_id,
    }).sort({
      created_at: -1,
    });

    if (notifications.length === 0) {
      return res
        .status(404)
        .json({ message: "No notifications found for this user" });
    }

    return res.status(200).json({
      message: "Notifications retrieved successfully",
      data: {
        notifications,
      },
    });
  } catch (error) {
    return res.status(500).json({
      message: "Failed to retrieve notifications",
      error: error.message,
    });
  }
};
