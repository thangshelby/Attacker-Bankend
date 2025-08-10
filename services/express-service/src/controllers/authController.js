import bcrypt from "bcryptjs";
import UserModel from "../models/userModel.js";
import StudentModel from "../models/studentModel.js";

import {
  sendOtpEmail,
  sendOtpToCreateContract,
  generateAccessToken,
  generateRefreshToken,
} from "../services/auth/auth.service.js";

// [POST] /register
export const register = async (req, res) => {
  try {
    const existingUser = await UserModel.findOne({ email: req.body.email });

    // Nếu email đã tồn tại nhưng chưa xác minh, gửi lại OTP và cho phép tiếp tục
    if (existingUser) {
      if (existingUser.kyc_status !== "Verified") {
        const otpToken = await sendOtpEmail(req.body.email);
        existingUser.otp_token = otpToken;
        await existingUser.save();

        const accessToken = generateAccessToken(existingUser);
        const refreshToken = generateRefreshToken(existingUser);

        res.cookie("refreshToken", refreshToken, {
          httpOnly: true,
          secure: true,
          sameSite: "strict",
          maxAge: 7 * 24 * 60 * 60 * 1000,
        });

        return res.status(200).json({
          message: "User exists, resend OTP and continue verification",
          status: true,
          data: {
            user: existingUser,
            accessToken,
          },
        });
      }

      return res.status(400).json({
        message: "Email already exists",
        status: false,
      });
    }

    const isPasswordValid = req.body.password && req.body.password.length >= 6;
    if (!isPasswordValid) {
      return res.status(400).json({
        message: "Password must be at least 6 characters long",
        status: false,
      });
    }

    const hashPassword = await bcrypt.hash(req.body.password, 10);
    const otpToken = await sendOtpEmail(req.body.email);

    const user = new UserModel({
      name: req.body.name,
      email: req.body.email,
      password: hashPassword,
      otp_token: otpToken,
      kyc_status:'Verified',
      // citizen_id: `CCCD${Date.now()}`, // Generate unique citizen ID
      // phone: req.body.phone || "",
      // birth: req.body.birth || new Date(),
      // gender: req.body.gender || "Nam",
      address: req.body.address || "",
    });
    const result = await user.save();

    const accessToken = generateAccessToken(result);
    const refreshToken = generateRefreshToken(result);

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.status(200).json({
      message: "User created successfully",
      status: true,
      data: {
        user: result,
        accessToken,
      },
    });
  } catch (err) {
    console.error("Error creating user:", err);
    res.status(500).json({
      message: "Failed to create user",
      error: err.message,
    });
  }
};
export const sendOtp = async (req, res) => {
  const email = req.params.email;
  try {
    const user = await UserModel.findOne({ email });
    const otpToken = await sendOtpToCreateContract(email);
    user.otp_token = otpToken;
    await user.save();
    res.status(200).json({
      message: "OTP sent successfully",
      status: true,
      data: {
        otp_token: otpToken,
      },
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to send OTP",
      status: false,
      error: error.message,
    });
  }
};
// [POST] /login
export const login = async (req, res) => {
  try {
    const isUserExist = await UserModel.findOne({ email: req.body.email });
    if (!isUserExist) {
      return res.status(401).json({
        message: {
          email: "Your email is not registered",
          password: null,
        },
        status: false,
      });
    }

    const isPasswordValid = await bcrypt.compare(
      req.body.password,
      isUserExist.password
    );
    if (!isPasswordValid) {
      return res.status(401).json({
        message: {
          email: null,
          password: "Your password is incorrect",
        },
        status: false,
      });
    }

    const user = await UserModel.findById(isUserExist._id, "-password");

    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user);

    res.cookie("refreshToken", refreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    res.status(200).json({
      message: "Login Successfully!",
      status: true,
      data: {
        user,
        accessToken,
      },
    });
  } catch (err) {
    res.status(500).json({
      message: "Something went wrong!",
      status: false,
      error: err.message,
    });
  }
};

export const verifyEmail = async (req, res) => {
  const { email, otp_token } = req.body;
  try {
    // Find user by email only (bypass OTP validation)
    const user = await UserModel.findOne({ email });
    if (!user) {
      return res.status(400).json({
        message: {
          emal: "User not found",
          password: null,
          otp_token: null,
        },
        status: false,
      });
    }

    // Accept any OTP token (bypass validation)
    console.log(
      `Bypassing OTP validation for email: ${email}, provided token: ${otp_token}`
    );

    user.kyc_status = "Verified";
    user.otp_token = "";
    await user.save();

    // Create student record if it doesn't exist
    let student = await StudentModel.findOne({ citizen_id: user.citizen_id });
    if (!student && user.citizen_id) {
      student = new StudentModel({
        citizen_id: user.citizen_id,
        student_id: `SV${Date.now()}`, // Generate unique student ID
        name: user.name,
        email: user.email,
        university: "Đại học Bách Khoa",
        major_name: "Công nghệ thông tin",
        birth: user.birth || new Date(),
        gender: user.gender || "Nam",
        address: user.address || "",
        phone: user.phone || "",
      });
      await student.save();
      console.log("Created student record for user:", student.student_id);
    }
    res.status(200).json({
      message: "Email verified successfully",
      status: true,
      data: {
        user,
      },
    });
  } catch (error) {
    res.status(500).json({
      message: "Failed to verify email",
      status: false,
      error: error.message,
    });
  }
};

// [DELETE] /delete_account/:id
export const deleteAccount = async (req, res) => {
  try {
    const result = await UserModel.findOneAndDelete({ _id: req.params.id });
    if (!result) {
      return res.status(404).json({
        message: "User not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "Successfully deleted account",
      status: true,
    });
  } catch (error) {
    res.status(500).json({
      message: "Internal Server Error",
      status: false,
    });
  }
};

// [PUT] /users/:id
export const updateUser = async (req, res) => {
  try {
    const updateData = { ...req.body };
    if (updateData.password) {
      updateData.password = await bcrypt.hash(updateData.password, 10);
    }

    const updatedUser = await UserModel.findByIdAndUpdate(
      req.params.id,
      updateData,
      { new: true, select: "-password" }
    );

    if (!updatedUser) {
      return res.status(404).json({
        message: "User not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "User updated successfully",
      data: updatedUser,
      status: true,
    });
  } catch (err) {
    res.status(500).json({
      message: "Failed to update user",
      error: err.message,
      status: false,
    });
  }
};

export const getAllUsers = async (req, res) => {
  try {
    const users = await UserModel.find({}, "-password"); // ẩn password
    res.status(200).json({
      message: "Fetched all users",
      data: users,
      status: true,
    });
  } catch (err) {
    res.status(500).json({
      message: "Failed to fetch users",
      error: err.message,
      status: false,
    });
  }
};

export const getMe = async (req, res) => {
  try {
    const userId = req.userId; // Lấy ID người dùng từ token đã giải mã
    const user = await UserModel.findById(userId, "-password"); // ẩn password
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
export const logout = async (req, res) => {
  try {
    res.clearCookie("refreshToken", {
      httpOnly: true,
      secure: true,
      sameSite: "strict",
    });
    return res.status(200).json({
      message: "Logout successfully",
      status: true,
    });
  } catch (error) {
    res.status(500).json({
      message: "Internal Server Error",
      status: false,
    });
  }
};
// [GET] /users/:id
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
