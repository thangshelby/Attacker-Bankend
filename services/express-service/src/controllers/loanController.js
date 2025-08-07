import * as TruveraService from "../services/thirparty/truvera.service.js";
import MASConversationModel from "../models/MASConversationModel.js";
import StudentModel from "../models/studentModel.js";
import UserModel from "../models/userModel.js";
import LoanContractModel from "../models/loanContractModel.js";
import AcademicModel from "../models/academicModel.js";
import * as notificationController from "./notificationController.js";

const initialLoanProfile = {
  age_group: "", //*
  age: 0,
  gender: "",
  province_region: "", //*
  university: "",
  university_tier: "", //*
  public_university: true, //*
  major_category: "",
  gpa_normalized: 0, //*
  study_year: 0,
  club: "", //*
  family_income: 0,
  has_part_time_job: false,
  existing_debt: 0, //*
  guarantor: "",
  loan_amount_requested: 0,
  loan_purpose: "",
};

export const createLoanContract = async (req, res) => {
  try {
    const { student_id } = req.body;
    const student = await StudentModel.findById(student_id);
    const newLoan = new LoanContractModel({
      ...req.body,
    });
    await newLoan.save();
    
    // Create notification for loan creation
    const notification = {
      citizen_id: student.citizen_id,
      header: "Loan Contract Created",
      content: `Your loan contract with ID ${newLoan._id} has been created successfully.`,
      type: "success",
      icon: "check-circle",
      is_read: false,
    };
    
    await notificationController.createNotification(notification);
    createLoanProfile(student._id, newLoan);
    return res.status(201).json({
      message: "Loan contract created successfully",
      data: {
        loan: newLoan,
      },
      status: true,
    });
  } catch (error) {
    console.error("Error creating loan contract:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
};

const createLoanProfile = async (student_id, loan) => {
  const student = await StudentModel.findById(student_id);
  const user = await UserModel.findById(student.citizen_id);
  const academic = await AcademicModel.findOne({ student_id: student._id });
  try {
    const loanProfile = {
      age_group: classifyAgeGroup(user.age),
      age: user.age,
      gender: user.gender,
      province_region: "Nam",
      university: student.university,
      university_tier: 1,
      public_university: true,
      major_category: student.major_name,
      gpa_normalized: academic.gpa / 4,
      study_year: academic.study_year,
      club: academic.club,
      family_income: loan.family_income,
      has_part_time_job: true,
      existing_debt: false,
      guarantor: loan.guarantor,
      loan_amount_requested: loan.loan_amount_requested,
      loan_purpose: loan.loan_purpose || loan.custom_purpose,
    };

    const response = await fetch(`http://127.0.0.1:8000/api/v1/debate-loan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loanProfile),
    });
    const ress = await response.json();

    storeMASConversation(ress);
  
  } catch (error) {
    console.error("Error creating loan profile:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
};

export const createProofRequest = async (req, res) => {
  try {
    const student_id = req.params.student_id;
    const result = await TruveraService.createProofRequest(student_id);
    return res.status(200).json(result);
  } catch (error) {}
};

export const storeMASConversation = async (data) => {
  try {
    const conversation = new MASConversationModel({
      responses: data.responses,
      rule_based: data.rule_based,
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
