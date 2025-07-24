import UserModel from "../models/userModel.js";
import StudentModel from "../models/studentModel.js";
// import SupporterModel from "../models/supporterModel.js";

export const updateUser = async (req, res) => {
  try {
  } catch (error) {}
};

export const getUserById = async (req, res) => {
  try {
    const user = await UserModel.findById(req.params.id, "-password");
    if (!user) {
      return res.status(404).json({
        message: "User not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "User fetched successfully",
      data: user,
      status: true,
    });
  } catch (err) {
    res.status(500).json({
      message: "Failed to fetch user",
      error: err.message,
      status: false,
    });
  }
};

export const getAllUsers = async (req, res) => {
  try {
    const users = await UserModel.find({}, "-password");
    res.status(200).json({
      message: "Users fetched successfully",
      data: users,
      status: true,
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to fetch users",
      error: error.message,
      status: false,
    });
  }
};
export const getUsersBySchoolName = async (req, res) => {
  try {
  } catch (error) {}
};

export const getUsersBySchoolId = async (req, res) => {
  try {
  } catch (error) {}
};

export const getUsersByRole = async (req, res) => {
  try {
    const users = await UserModel.find({ role: req.params.role }, "-password");
    res.status(200).json({
      message: "Users fetched successfully",
      data: users,
      status: true,
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to fetch users",
      error: error.message,
      status: false,
    });
  }
};

export const deleteUserById = async (req, res) => {
  try {
  } catch (error) {}
};
