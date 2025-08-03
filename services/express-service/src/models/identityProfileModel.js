import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const IdentityProfileSchema = mongoose.Schema({
  student_id: { type: String, required: true }, //FK
  study_year: { type: String, required: true }, //FK
  term: { type: Number, required: true }, //FK
  name: { type: String, required: true },
  description: { type: String, required: true },
  image: { type: String },
  method: { type: String, default: "key" }, // did or email
  did: { type: String, required: true },
  credential_subject: { type: Object }, // Truvera VC subject
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
