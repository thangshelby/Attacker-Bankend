import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import UserModel from "../models/userModel.js";

// [POST] /signup
export const signUp = async (req, res) => {
  try {
    const hash = await bcrypt.hash(req.body.password, 10);
    const user = new UserModel({
      name: req.body.name,
      username: req.body.username,
      gmail: req.body.gmail,
      password: hash,
      userFirstSignUp: req.body.userFirstSignUp,
      category: [],
    });

    const result = await user.save();

    const token = jwt.sign(
      { gmail: req.body.gmail, userId: result._id },
      "jwt_key",
      { expiresIn: "1h" }
    );

    res.status(200).json({
      message: "Account Created",
      status: true,
      data: {
        UserSince: result.userFirstSignUp,
        username: result.username,
        name: result.name,
        token: token,
        expiredToken: 3600,
        userId: result._id,
      },
    });
  } catch (err) {
    res.status(500).json({
      message: "Failed to create user",
      error: err.message,
    });
  }
};

// [POST] /login
export const login = async (req, res) => {
  try {
    const user = await UserModel.findOne({ gmail: req.body.gmail });
    if (!user) {
      return res.status(401).json({
        message: "Invalid Email Address",
        status: false,
      });
    }

    const isValid = await bcrypt.compare(req.body.password, user.password);
    if (!isValid) {
      return res.status(401).json({
        message: "Invalid Email Address or Password",
        status: false,
      });
    }

    const token = jwt.sign(
      { gmail: user.gmail, userId: user._id },
      "raghav_garg_first_mean_project_this_can_be_anything",
      { expiresIn: "1h" }
    );

    res.status(200).json({
      message: "Login Successfully!",
      data: {
        token: token,
        latestLoginDate: new Date(),
        userId: user._id,
        expiredToken: 3600,
      },
      status: true,
    });
  } catch (err) {
    res.status(500).json({
      message: "Something went wrong!",
      status: false,
      error: err.message,
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

// [DELETE] /users/:id
export const deleteUser = async (req, res) => {
  try {
    const result = await UserModel.findByIdAndDelete(req.params.id);
    if (!result) {
      return res.status(404).json({
        message: "User not found",
        status: false,
      });
    }

    res.status(200).json({
      message: "User deleted successfully",
      status: true,
    });
  } catch (err) {
    res.status(500).json({
      message: "Failed to delete user",
      error: err.message,
      status: false,
    });
  }
};
