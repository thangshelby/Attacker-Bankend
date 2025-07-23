import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const SupporterSchema = mongoose.Schema({
  student_id: { type: String, ref: "Student", required: true },
  supporter_occupation: { type: String },
  supporter_income_range: { type: String },
  supporter_job: { type: String },
  support_relationship: { type: String },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

SupporterSchema.plugin(mongooseUniqueValidator, {
  message: "already exists.",
});
const SupporterModel = mongoose.model("SupporterModel", SupporterSchema);

export default SupporterModel;
