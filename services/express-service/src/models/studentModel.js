import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const StudentSchema = mongoose.Schema({
  citizen_id: { type: String, ref: "User", required: true },
  student_id: { type: String, unique: true },
  university: { type: String },
  faculty_name: { type: String },
  major_name: { type: String },
  year_of_study: { type: Number },
  class_id: { type: String },
  has_parttime_job: { type: Boolean },
  has_supporter: { type: Boolean },
  verified: { type: Boolean, default: false },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

StudentSchema.plugin(mongooseUniqueValidator, {
  message: "already exists.",
});
const StudentModel = mongoose.model("Student", StudentSchema);

export default StudentModel;
