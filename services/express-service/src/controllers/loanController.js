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
      message: "Khoản vay đã được tạo thành công",
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

    if (!student_id) {
      console.error("No student_id provided");
      return res.status(400).json({
        message: "student_id is required",
        status: false,
      });
    }

    const student = await StudentModel.findOne({ student_id });

    if (!student) {
      console.error("Student not found with student_id:", student_id);
      return res.status(404).json({
        message: "Student not found",
        status: false,
      });
    }
    const user = await UserModel.findOne({ citizen_id: student.citizen_id });

    // Set default values for simplified form
    const amount = parseInt(req.body.loan_amount_requested, 10) || 0;
    const tenor = 12; // Default to 12 months
    const interestRate = 0.08; // Default to 8% for "Pay at maturity" method

    const totalInterest = Math.round(amount * interestRate * (tenor / 12));
    const totalPayment = amount + totalInterest;

    const loanData = {
      ...req.body,
      name: user.name,
      citizen_id: student.citizen_id, // Add citizen_id from student record
      loan_tenor: tenor,
      payment_method: "Trả cả gốc và lãi vào ngày đáo hạn",
      monthly_installment: 0,
      total_interest: totalInterest,
      total_payment: totalPayment,
    };

    const newLoan = new LoanContractModel(loanData);
    await newLoan.save();

    // Create notification for loan creation
    try {
      const notification = {
        citizen_id: student.citizen_id,
        header: "Khoản vay mới đã được tạo",
        content: `Hợp đồng vay của bạn với ID ${newLoan._id} đã được tạo thành công.`,
        type: "success",
        icon: "check-circle",
        is_read: false,
      };

      await notificationController.createNotification(notification);
      console.log("Notification created successfully");
    } catch (notificationError) {
      console.error("Error creating notification:", notificationError);
      // Don't fail the whole request for notification error
    }

    // Create loan profile (don't await to avoid blocking response)
    try {
      createLoanProfile(student.student_id, newLoan);
      console.log("Loan profile creation initiated");
    } catch (profileError) {
      console.error("Error creating loan profile:", profileError);
      // Don't fail the whole request for profile error
    }

    return res.status(201).json({
      message: "Loan contract created successfully",
      data: {
        loan: newLoan,
      },
      status: true,
    });
  } catch (error) {
    console.error("Error creating loan contract:", error);
    console.error("Error stack:", error.stack);
    return res.status(500).json({
      error: "Internal server error",
      message: error.message,
      details: process.env.NODE_ENV === "development" ? error.stack : undefined,
    });
  }
};

export const updateLoanContract = async (req, res) => {
  const { status } = req.body;
  console.log("🔍 Update loan request body:", req.body);
  console.log("🔍 Loan ID from params:", req.params.id);

  try {
    const { id } = req.params;

    // Check if loan exists first
    const existingLoan = await LoanContractModel.findById(id);
    if (!existingLoan) {
      console.log("❌ Loan contract not found with ID:", id);
      return res.status(404).json({
        message: "Loan contract not found",
        status: false,
      });
    }

    console.log("✅ Found existing loan:", existingLoan._id);

    const updatedLoan = await LoanContractModel.findByIdAndUpdate(
      id,
      { ...req.body, updated_at: new Date() },
      { new: true }
    );

    const citizen_id = updatedLoan.citizen_id;
    console.log("📧 Creating notification for citizen_id:", citizen_id);

    if (status && status === "accepted") {
      const notification = {
        citizen_id: citizen_id,
        header: "Khoản vay của bạn đã được chấp nhận",
        content:
          updatedLoan.reason || "Khoản vay của bạn đã được duyệt thành công",
        type: "success",
        icon: "check-circle",
        is_read: false,
      };
      await notificationController.createNotification(notification);
      console.log("✅ Admin approved loan directly - no MAS needed");
    }

    if (status && status === "rejected") {
      const notification = {
        citizen_id: citizen_id,
        header: "Khoản vay của bạn đã bị từ chối",
        content: updatedLoan.reason || "Khoản vay của bạn không được chấp nhận",
        type: "error",
        icon: "times-circle",
        is_read: false,
      };
      await notificationController.createNotification(notification);
    }

    console.log("✅ Loan contract updated successfully:", updatedLoan._id);
    return res.status(200).json({
      message: "Loan contract updated successfully",
      status: true,
      data: {
        loan: updatedLoan,
      },
    });
  } catch (error) {
    console.error("❌ Error updating loan contract:", error);
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
    console.log("Fetching MAS conversation for loan_id:", loan_id);

    // Find by loan_id field (not request_id) since that's how it's stored
    const conversation = await MASConversationModel.findOne({
      loan_id: loan_id,
    });
    if (!conversation) {
      console.log("No conversation found for loan_id:", loan_id);
      return res.status(404).json({
        message: "Conversation not found",
        status: false,
      });
    }

    console.log("Found conversation:", conversation._id);
    console.log("Conversation decision:", conversation.decision);

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
  try {
    const student = await StudentModel.findOne({ student_id });
    const user = await UserModel.findOne({ citizen_id: student?.citizen_id });
    const academic = await AcademicModel.findOne({ student_id });

    if (!student || !user || !loan) {
      console.error("Missing required data for loan profile:", {
        student: !!student,
        user: !!user,
        loan: !!loan,
      });
      return;
    }

    const loanProfile = {
      // Data from loan object (user input)
      loan_amount_requested: loan.loan_amount_requested,
      guarantor: loan.guarantor,
      family_income: parseInt(loan.family_income, 10),
      existing_debt: loan.existing_debt === "true",
      loan_purpose: loan.loan_purpose,

      // Data from student, user, academic records
      age_group: classifyAgeGroup(user.age) || "18-22",
      age: user.age || 20,
      gender: user.gender || "Nam",
      major_category: student.major_name || "STEM",
      gpa_normalized: (academic?.gpa || 3.0) / 4,
      study_year: parseInt(academic?.study_year || 3, 10),
      club: academic?.club || "Câu lạc bộ IT",

      // Hardcoded test data as requested
      province_region: "Bắc",
      university_tier: 1,
      public_university: false,
      has_part_time_job: true,

      // Unique identifier
      loan_contract_id: loan._id?.toString() || `loan-${Date.now()}`,
    };

    console.log(
      "Loan Profile to be sent to MAS:",
      JSON.stringify(loanProfile, null, 2)
    );

    const response = await fetch(`http://127.0.0.1:8000/api/v1/debate-loan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loanProfile),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error from debate-loan API:", response.status, errorText);
      return;
    }

    const ress = await response.json();
    console.log("MAS Response:", JSON.stringify(ress, null, 2));

    // Store MAS conversation
    try {
      const conversation = await storeMASConversation(ress);
      console.log("✅ MAS conversation stored with ID:", conversation._id);
    } catch (storeError) {
      console.error("❌ Error storing MAS conversation:", storeError);
    }
  } catch (error) {
    console.error("Error creating loan profile:", error);
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
  if (!rangeStr || typeof rangeStr !== "string") {
    console.log("Invalid rangeStr:", rangeStr);
    return 15000000; // Default fallback: 15M VND
  }

  console.log("Parsing income range:", rangeStr);

  // Handle "<10000000" format
  if (rangeStr.startsWith("<")) {
    const maxValue = parseInt(rangeStr.substring(1), 10);
    if (!isNaN(maxValue)) {
      return Math.round(maxValue / 2); // Average from 0 to max
    }
  }

  // Handle ">100000000" format
  if (rangeStr.startsWith(">")) {
    const minValue = parseInt(rangeStr.substring(1), 10);
    if (!isNaN(minValue)) {
      return minValue + 25000000; // Add 25M to min value as estimate
    }
  }

  // Handle "10000000-20000000" format
  if (rangeStr.includes("-")) {
    const [minStr, maxStr] = rangeStr.split("-");
    const min = parseInt(minStr, 10);
    const max = parseInt(maxStr, 10);
    if (!isNaN(min) && !isNaN(max)) {
      return Math.round((min + max) / 2);
    }
  }

  // If all parsing fails, try to parse as single number
  const singleValue = parseInt(rangeStr, 10);
  if (!isNaN(singleValue)) {
    return singleValue;
  }

  console.error("Could not parse income range:", rangeStr);
  return 15000000; // Default fallback: 15M VND
};
const classifyUniversity = (university) => {};
const classifyRegion = (province) => {};
