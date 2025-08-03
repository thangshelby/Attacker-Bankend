import mongoose from 'mongoose';
import mongooseUniqueValidator from 'mongoose-unique-validator';

const LoanProfileSchema = mongoose.Schema({
  student_id: { type: String, ref: 'Student', required: true },
  loan_amount_requested: { type: Number, required: true },
  loan_purpose: { type: Number, required: true },
  monthly_installment: { type: Number, required: true },
  status: { type: String, enum: ['pending', 'rejected', 'accepted'], default: 'pending' },
  proof_template_id: { type: String },
  proof_request_id: { type: String },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

LoanProfileSchema.plugin(mongooseUniqueValidator, {
  message: 'already exists.',
});
const LoanProfileModel = mongoose.model('LoanProfile', LoanProfileSchema);

export default LoanProfileModel;
