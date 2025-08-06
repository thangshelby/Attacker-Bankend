import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const NotificationSchema = new mongoose.Schema({
  citizen_id: { type: String, ref: "User", required: false }, // nếu IsGlobal = true thì có thể null
  header: { type: String, required: true },
  content: { type: String, required: true },
  is_read: { type: Boolean, default: false },
  type: {
    type: String,
    enum: ["success", "info", "warning", "error"],
    default: "info",
  },
  is_global: { type: Boolean, default: false },
  icon: { type: String, default: "" },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

NotificationSchema.plugin(mongooseUniqueValidator, {
  message: "already exists.",
});

// Optional: Auto-update `updated_at` on every save
NotificationSchema.pre("save", function (next) {
  this.updated_at = new Date();
  next();
});

const NotificationModel = mongoose.model("Notification", NotificationSchema);

export default NotificationModel;
