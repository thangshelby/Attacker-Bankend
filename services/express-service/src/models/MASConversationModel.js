// import mongoose from "mongoose";

// const MASConversationSchema = new mongoose.Schema({
// //   loan_profile_id: { type: String, required: true },
// //   student__id: { type: String, required: true },
//   responses: {
//     type: { String },
//     required: true,
//   },
//   rule_based: { type: String, required: true },
//   agent_status: { type: String },
//   final_result: { type: String },
//   processing_time_seconds: { type: String },
//   request_metadata: { type: String },

//   request_id: { type: String, required: true },
//   created_at: { type: Date, default: Date.now },
// });

// const MASConversationModel = mongoose.model(
//   "MASConversation",
//   MASConversationSchema
// );

// export default MASConversationModel; // Ensure you have node-fetch installed
// models/MASConversationModel.js
import mongoose from "mongoose";
const { Schema } = mongoose;

const MASConversationSchema = new mongoose.Schema({
  responses: { type: Schema.Types.Mixed, required: true },
  rule_based: { type: Schema.Types.Mixed, required: true },
  agent_status: { type: Schema.Types.Mixed },
  final_result: { type: Schema.Types.Mixed },
  processing_time_seconds: { type: Number },
  request_id: { type: String, required: true, index: true, unique: true },
}, {
  timestamps: { createdAt: "created_at", updatedAt: "updated_at" }
});

const MASConversationModel = mongoose.model("MASConversation", MASConversationSchema);
export default MASConversationModel;
