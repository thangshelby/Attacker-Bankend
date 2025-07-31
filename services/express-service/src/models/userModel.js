import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const UserSchema = mongoose.Schema({
  citizen_id: { type: String, unique: true },
  name: { type: String, required: true },
  birth: { type: Date },
  gender: {
    type: String,
    enum: ["male", "female", "others", ""],
    default: "",
  },
  address: { type: String },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  number: { type: String },
  citizen_image_front: { type: String },
  citizen_image_back: { type: String },
  role: { type: String, enum: ["Admin", "User"], default: "User" },
  kyc_status: {
    type: String,
    enum: ["Pending", "Verified", "Rejected"],
    default: "Pending",
  },
  otp_token: { type: String },
  verified: { type: Boolean, default: false },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

UserSchema.plugin(mongooseUniqueValidator, {
  message: "email already exists.",
});
const UserModel = mongoose.model("User", UserSchema);

export default UserModel;
