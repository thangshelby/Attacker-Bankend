import UserModel from "../models/userModel.js";
import StudentModel from "../models/studentModel.js";

export const updateUser = async (req, res) => {
  console.log('🚀 User Controller - Update user request received');
  console.log('📊 Request body:', req.body);
  
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
    if (!_id) {
      console.log('❌ Missing _id in request');
      return res.status(400).json({ message: "User ID is required" });
    }
    
    console.log('🔍 Looking for user with _id:', _id);
    const user = await UserModel.findOne({ _id });

    if (!user) {
      console.log('❌ User not found with _id:', _id);
      return res.status(404).json({ message: "User not found." });
    }
    
    console.log('✅ User found:', user.email);

    // ✅ Convert and validate data types
    const parsedBirth = birth ? new Date(birth) : user.birth;
    const validGender = gender && ["male", "female", "others"].includes(gender) ? gender : user.gender;
    
    // ✅ Extract URL from Cloudinary response object
    const extractImageUrl = (imageData) => {
      if (!imageData) return null;
      if (typeof imageData === 'string') return imageData; // Already a URL
      if (typeof imageData === 'object' && imageData.url) return imageData.url; // Extract URL from object
      return null;
    };
    
    const citizenCardFrontUrl = extractImageUrl(citizen_card_front) ?? user.citizen_card_front;
    const citizenCardBackUrl = extractImageUrl(citizen_card_back) ?? user.citizen_card_back;

    // Cập nhật từng trường nếu có truyền vào
    user.name = name ?? user.name;
    user.citizen_id = citizen_id ?? user.citizen_id;
    user.birth = parsedBirth;
    user.gender = validGender;
    user.address = address ?? user.address;
    user.email = email ?? user.email;
    user.phone = phone ?? user.phone;
    user.citizen_card_front = citizenCardFrontUrl;
    user.citizen_card_back = citizenCardBackUrl;
    user.role = role ?? user.role;
    user.kyc_status = kyc_status ?? user.kyc_status;
    user.otp_token = otp_token ?? user.otp_token;
    user.updated_at = new Date();

    console.log('💾 Saving user updates...');
    console.log('📊 Data to save:', {
      name: user.name,
      birth: user.birth,
      gender: user.gender,
      email: user.email,
      citizen_card_front: user.citizen_card_front,
      citizen_card_back: user.citizen_card_back
    });
    
    // ✅ Check if citizen_id is being updated (before saving)
    const oldCitizenId = user.citizen_id;
    const newCitizenId = citizen_id;
    
    await user.save();
    console.log('✅ User updated successfully');
    
    // ✅ If citizen_id changed, update student record too
    if (newCitizenId && newCitizenId !== oldCitizenId) {
      console.log('🔄 Citizen ID changed, updating student record...');
      console.log('📝 Old citizen_id:', oldCitizenId);
      console.log('📝 New citizen_id:', newCitizenId);
      
      try {
        const student = await StudentModel.findOne({ citizen_id: oldCitizenId });
        if (student) {
          student.citizen_id = newCitizenId;
          await student.save();
          console.log('✅ Student record updated with new citizen_id');
        } else {
          console.log('📭 No student record found with old citizen_id');
        }
      } catch (studentError) {
        console.error('❌ Error updating student record:', studentError);
        // Don't fail the user update if student update fails
      }
    }

    res.status(200).json({ message: "User updated successfully", user });
  } catch (error) {
    console.error("❌ Update user error:", error);
    
    // ✅ Better error handling
    if (error.name === 'ValidationError') {
      return res.status(400).json({ 
        message: "Validation error", 
        details: error.message 
      });
    }
    
    if (error.code === 11000) {
      return res.status(400).json({ 
        message: "Duplicate data error", 
        details: "Email or Citizen ID already exists" 
      });
    }
    
    res.status(500).json({ 
      message: "Internal server error",
      details: error.message 
    });
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

// ✅ Temporary endpoint to sync citizen_id between user and student
export const syncCitizenId = async (req, res) => {
  try {
    console.log('🔄 Starting citizen_id sync...');
    
    // Get all users with real citizen_id (not TEMP_)
    const users = await UserModel.find({
      citizen_id: { $not: /^TEMP_/ }
    });
    
    console.log(`📊 Found ${users.length} users with real citizen_id`);
    
    let syncedCount = 0;
    
    for (const user of users) {
      // Find student record with old citizen_id
      const student = await StudentModel.findOne({
        citizen_id: { $regex: /^TEMP_/ }
      });
      
      if (student) {
        // Check if this student belongs to this user by checking if they have the same email or other identifier
        // For now, we'll update the first TEMP_ student we find
        // In production, you might want to add more sophisticated matching logic
        
        console.log(`🔄 Updating student ${student._id} citizen_id from ${student.citizen_id} to ${user.citizen_id}`);
        student.citizen_id = user.citizen_id;
        await student.save();
        syncedCount++;
        break; // Only update one for now
      }
    }
    
    res.status(200).json({
      message: "Citizen ID sync completed",
      syncedCount,
      totalUsers: users.length
    });
    
  } catch (error) {
    console.error("❌ Sync citizen_id error:", error);
    res.status(500).json({
      message: "Sync failed",
      error: error.message
    });
  }
};
