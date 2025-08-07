import { request } from "http";
import mongoose from "mongoose";
const { Schema } = mongoose;

const MASConversationSchema = new mongoose.Schema(
  {
    loan_id: { type: String, required: true }, // FK to LoanContract
    request_id: { type: String, required: true }, // Unique ID for the request
    request_data: { type: Object, required: true }, // Data sent in the request
    result_stringify: { type: String, required: true }, // Stringified result from
    decision: {
      type: String,
      enum: ["approve", "reject", "unknown"],
      default: "unknown",
    }, // Decision made by MAS
    processing_time: { type: Number, required: true }, // Time taken for processing in milliseconds
  },
  {
    timestamps: { createdAt: "created_at" },
  }
);
const MASConversationModel = mongoose.model(
  "MASConversation",
  MASConversationSchema
);
export default MASConversationModel;
