import * as TruveraService from '../services/truvera.service.js'
import MASConversationModel from "../models/MASConversationModel.js";
import StudentModel from "../models/studentModel.js";
import UserModel from "../models/userModel.js";
import LoanProfileModel from "../models/loanProfileModel.js";
// Loan Controller for handling loan application requests and MAS workflow integration

const initialLoanProfile = {
  age_group: "",
  age: 0,
  gender: "",
  province_region: "",
  university: "",
  university_tier: "",
  public_university: true,
  major_name: "",
  gpa: "",
  club: "",
  family_income: 0,
  has_part_time_job: false,
  existing_debt: 0,
  gurantor: "",
  loan_amount_requested: 0,
  loan_purpose: "",
};

export const createLoanProfile = async () => {
  try {

  } catch (error) {}
};

export const createProofRequest= async(req, res) => {
  
  try {
    const student_id = req.params.student_id
    const result = await TruveraService.createProofRequest(student_id);
    return res.status(200).json(result);
  } catch (error) {
    
  }
}

export const storeMASConversation = async (data) => {
  try {
    const conversation = new MASConversationModel({
      responses: data.responses, // << không stringify
      rule_based: data.rule_based, // tên phải khớp schema
      agent_status: data.agent_status,
      final_result: data.final_result,
      processing_time_seconds: data.processing_time_seconds,
      request_id: data.request_id,
    });

    await conversation.save();
    return conversation;
  } catch (error) {
    console.error("Error storing MAS conversation:", error);
    throw error;
  }
};

const classifyAgeGroup = (age) => {};
const classifyUniversity = (university) => {};
const classifyRegion = (province) => {};
