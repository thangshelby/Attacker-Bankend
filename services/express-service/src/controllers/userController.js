import UserModel from "../models/userModel.js";

export const updateUser = async (req, res) => {
  const {
    _id,
    citizen_id,
    name,
    birth,
    gender,
    address,
    email,
    phone,
    citizen_card_front,
    citizen_card_back,
    role,
    kyc_status,
    otp_token,
  } = req.body;

  try {
    const user = await UserModel.findOne({ _id });

    if (!user) {
      return res.status(404).json({ message: "User not found." });
    }

    // Cập nhật từng trường nếu có truyền vào
    user.name = name ?? user.name;
    user.citizen_id = citizen_id ?? user.citizen_id;
    user.birth = birth ?? user.birth;
    user.gender = gender ?? user.gender;
    user.address = address ?? user.address;
    user.email = email ?? user.email;
    user.phone = phone ?? user.phone;
    user.citizen_card_front = citizen_card_front ?? user.citizen_card_front;
    user.citizen_card_back = citizen_card_back ?? user.citizen_card_back;
    user.role = role ?? user.role;
    user.kyc_status = kyc_status ?? user.kyc_status;
    user.otp_token = otp_token ?? user.otp_token;
    user.updated_at = new Date();

    await user.save();

    res.status(200).json({ message: "User updated successfully", user });
  } catch (error) {
    console.error("Update error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
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
export const getUserByCitizenId = async (req, res) => {
  try {
    const { citizen_id } = req.params;
    const user = await UserModel.findOne({ citizen_id }, "-password");
    if (!user) {
      return res.status(404).json({
        message: "User not found",
        status: false,
      });
    }
    res.status(200).json({
      message: "User fetched successfully",
      data: {
        user,
      },
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

import { db } from "../server.js";
export const getUsersBySchoolName = async (req, res) => {
  const schoolName = req.params.schoolName;
  console.log(schoolName);
  try {
    const results = await db.then(async (db) => {
      const results = await db
        .collection("users")
        .aggregate([
          {
            $lookup: {
              from: "students",
              localField: "citizen_id",
              foreignField: "citizen_id",
              as: "student_info",
            },
          },
          { $unwind: "$student_info" },
          {
            $lookup: {
              from: "supportermodels",
              localField: "student_info.student_id", // hoặc "student_info._id" nếu dùng ObjectId
              foreignField: "student_id",
              as: "supporter_info",
            },
          },
          {
            $match: {
              "student_info.university": schoolName,
            },
          },
        ])
        .toArray();
      return results;
    });
    return res.status(200).json({
      message: "Fetch Users Successfully",
      status: true,
      data: {
        users: results,
      },
    });
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
