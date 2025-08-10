import mongoose from "mongoose";
import mongooseUniqueValidator from "mongoose-unique-validator";

const LoanContractSchema = mongoose.Schema({
  student_id: { type: String, ref: "Student", required: true },
  citizen_id: { type: String, ref: "Citizen", required: true },
  name: { type: String},
  loan_amount_requested: { type: Number, required: true },
  loan_tenor: { type: Number, required: true }, // in months
  loan_purpose: { type: String, required: true },
  custom_purpose: { type: String, default: "" },
  guarantor: { type: String, default: "" },
  family_income: { type: String, required: true },
  payment_method: { type: String, required: true }, 
  payment_frequency: { type: String, default: "" },
  monthly_installment: { type: Number, required: true },
  total_interest: { type: Number, required: true },
  total_payment: { type: Number, required: true },
  status: {
    type: String,
    enum: ["pending", "rejected", "accepted"],
    default: "pending",
  },
  reason: { type: String, default: "" },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now },
});

LoanContractSchema.plugin(mongooseUniqueValidator, {
  message: "already exists.",
});

LoanContractSchema.pre("save", function (next) {
  this.updated_at = new Date();
  next();
});

const LoanContractModel = mongoose.model("LoanContract", LoanContractSchema);

export default LoanContractModel;
