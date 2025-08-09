import * as TruveraService from "../services/thirparty/truvera.service.js";
import MASConversationModel from "../models/MASConversationModel.js";
import StudentModel from "../models/studentModel.js";
import UserModel from "../models/userModel.js";
import LoanContractModel from "../models/loanContractModel.js";
import AcademicModel from "../models/academicModel.js";
import * as notificationController from "./notificationController.js";
import { db } from "../server.js";

export const getAllLoanContracts = async (req, res) => {
  try {
    const loanContracts = await LoanContractModel.find().sort({
      createdAt: -1,
    });
    return res.status(200).json({
      message: "Loan contracts retrieved successfully",
      status: true,
      data: {
        loans: loanContracts,
      },
    });
  } catch (error) {
    console.error("Error getting loan contracts:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

export const getLoanContractById = async (req, res) => {
  try {
    const { id } = req.params;
    const loanContract = await LoanContractModel.findById(id);
    if (!loanContract) {
      return res.status(404).json({
        message: "Loan contract not found",
        status: false,
      });
    }
    return res.status(200).json({
      message: "Loan contract retrieved successfully",
      status: true,
      data: {
        loanContract,
      },
    });
  } catch (error) {
    console.error("Error getting loan contract by ID:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

export const getLoanContractsByStudentId = async (req, res) => {
  try {
    const { student_id } = req.params;
    const loanContracts = await LoanContractModel.find({ student_id });
    return res.status(200).json({
      message: "Loan contracts retrieved successfully",
      status: true,
      data: {
        loans: loanContracts,
      },
    });
  } catch (error) {
    console.error("Error getting loan contracts:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

export const createLoanContract = async (req, res) => {
  try {
    const { student_id } = req.body;
    const student = await StudentModel.findOne({ student_id });
    const newLoan = new LoanContractModel({
      ...req.body,
    });
    await newLoan.save();

    // Create notification for loan creation
    const notification = {
      citizen_id: student.citizen_id,
      headers: "Loan Contract Created",
      content: `Your loan contract with ID ${newLoan._id} has been created successfully.`,
      type: "success",
      icon: "check-circle",
      is_read: false,
    };

    await notificationController.createNotification(notification);
    createLoanProfile(student.student_id, newLoan);
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

export const updateLoanContract = async (req, res) => {
  const { status } = req.body;
  console.log(req.body)
  try {
    const { id } = req.params;
    const updatedLoan = await LoanContractModel.findByIdAndUpdate(
      id,
      { ...req.body, updated_at: new Date() },
      { new: true }
    );
    const citizen_id = updatedLoan.citizen_id;
    if (status && status === "accepted") {
      const notification = {
        citizen_id: citizen_id,
        header: "Khoan vay cua ban da duoc chap nhan",
        content: updatedLoan.reason,
        type: "success",
        icon: "check-circle",
        is_read: false,
      };
      await notificationController.createNotification(notification);
      createLoanProfile(student.student_id, updatedLoan);
    }
    if (status && status === "rejected") {
      const notification = {
        citizen_id: citizen_id,
        header: "Khoan vay cua ban da bi tu choi",
        content: updatedLoan.reason,
        type: "error",
        icon: "times-circle",
        is_read: false,
      };
      await notificationController.createNotification(notification);
    }
    // If the loan contract is not found, return a 404 error

    if (!updatedLoan) {
      return res.status(404).json({
        message: "Loan contract not found",
        status: false,
      });
    }
    return res.status(200).json({
      message: "Loan contract updated successfully",
      status: true,
      data: {
        loan: updatedLoan,
      },
    });
  } catch (error) {
    console.error("Error updating loan contract:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

export const getMASConversationById = async (req, res) => {
  try {
    const { loan_id } = req.params;
    const conversation = await MASConversationModel.findOne({
      request_id: loan_id,
    });
    if (!conversation) {
      return res.status(404).json({
        message: "Conversation not found",
        status: false,
      });
    }
    return res.status(200).json({
      message: "Conversation retrieved successfully",
      status: true,
      data: {
        conversation,
      },
    });
  } catch (error) {
    console.error("Error getting MAS conversation by ID:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

const createLoanProfile = async (student_id, loan) => {
  const student = await StudentModel.findOne({ student_id });
  const user = await UserModel.findOne({ citizen_id: student.citizen_id });
  const academic = await AcademicModel.findOne({ student_id });
  try {
    const loanProfile = {
      loan_contract_id: loan._id,
      age_group: classifyAgeGroup(user.age),
      age: user.age || 20,
      gender: user.gender,
      province_region: "Nam",
      // university: student.university,
      university_tier: 1,
      public_university: true,
      major_category: student.major_name,
      gpa_normalized: academic.gpa / 4,
      study_year: parseInt(academic.study_year, 10),
      club: academic.club,
      family_income: parseAverageIncome(loan.family_income),
      has_part_time_job: true,
      existing_debt: false,
      guarantor: loan.guarantor,
      loan_amount_requested: loan.loan_amount_requested,
      loan_purpose: loan.loan_purpose || loan.custom_purpose,
    };
    console.log("Loan Profile:", JSON.stringify(loanProfile));
    fetch(`http://127.0.0.1:8000/api/v1/debate-loan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loanProfile),
    });
    // const ress = await response.json();

    // storeMASConversation(ress);
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
  } catch (error) {
    console.error("Error creating proof request:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
};

const storeMASConversation = async (data) => {
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

const classifyAgeGroup = (age) => {
  return "18-22";
};
const parseAverageIncome = (rangeStr) => {
  const [minStr, maxStr] = rangeStr.split("-");
  const min = parseInt(minStr, 10);
  const max = parseInt(maxStr, 10);
  if (isNaN(min) || isNaN(max)) {
    throw new Error("Invalid income range format");
  }
  return Math.round((min + max) / 2);
};
const classifyUniversity = (university) => {};
const classifyRegion = (province) => {};
