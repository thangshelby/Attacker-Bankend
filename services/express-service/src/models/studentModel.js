import mongoose from 'mongoose';
import mongooseUniqueValidator from 'mongoose-unique-validator';

const StudentSchema = mongoose.Schema({
  citizen_id: { type: String, ref: 'User', required: true },
  student_id: { type: String, required: true, unique: true },
  university: { type: String, required: true },
  faculty_name: { type: String, required: true },
  major_name: { type: String, required: true },
  year_of_study: { type: Number, required: true },
  class_id: { type: String, required: true },
  web3_address: { type: String },
  did: { type: String },
  field1: { type: String }, // đổi tên nếu biết rõ
  field2: { type: String }, // đổi tên nếu biết rõ
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

StudentSchema.plugin(mongooseUniqueValidator, {
  message: 'already exists.',
});
const StudentModel = mongoose.model('Student', StudentSchema);

export default StudentModel;
