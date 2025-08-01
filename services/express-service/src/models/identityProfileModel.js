import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const IdentityProfileSchema = mongoose.Schema({
  student_id: { type: String, unique: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  image: { type: String },
  method: { type: String, enum: ["did", "web3"], default: "did" },
  did: { type: String, required: true },
  verifiable_credential: {
    type: String,
  },
  status: { type: String, enum: ["active", "inactive"], default: "inactive" },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

IdentityProfileSchema.plugin(mongooseUniqueValidator, {
  message: "already exists.",
});
const IdentityProfileModel = mongoose.model(
  "IdentityProfile",
  IdentityProfileSchema
);

export default IdentityProfileModel;
