import IdentityProfileModel from "../models/identityProfileModel.js";

// [POST] /create - Tạo identity profile mới
export const createIdentityProfile = async (req, res) => {
  try {
    const {
      student_id,
      name,
      description,
      image,
      method,
      status,
      did,
    //   verifiable_credential,
    } = req.body;

    // Kiểm tra student_id đã tồn tại chưa
    const existingProfile = await IdentityProfileModel.findOne({ student_id });
    if (existingProfile) {
      return res.status(400).json({
        message: "Student ID already exists",
        status: false,
      });
    }

    // Tạo identity profile mới
    const identityProfile = new IdentityProfileModel({
      student_id,
      name,
      description,
      image,
      method: method || "did",
      did,
    //   verifiable_credential,
    });

    const result = await identityProfile.save();

    return res.status(201).json({
      message: "Identity profile created successfully",
      status: true,
      data: result,
    });
  } catch (error) {
    console.error("Error creating identity profile:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [GET] /all - Lấy tất cả identity profiles
export const getAllIdentityProfiles = async (req, res) => {
  try {
    const profiles = await IdentityProfileModel.find().sort({ created_at: -1 });

    return res.status(200).json({
      message: "Identity profiles retrieved successfully",
      status: true,
      data: profiles,
      count: profiles.length,
    });
  } catch (error) {
    console.error("Error getting identity profiles:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [GET] /:id - Lấy identity profile theo ID
export const getIdentityProfileById = async (req, res) => {
  try {
    const { id } = req.params;
    const profile = await IdentityProfileModel.findById(id);

    if (!profile) {
      return res.status(404).json({
        message: "Identity profile not found",
        status: false,
      });
    }

    return res.status(200).json({
      message: "Identity profile retrieved successfully",
      status: true,
      data: profile,
    });
  } catch (error) {
    console.error("Error getting identity profile:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [GET] /student/:student_id - Lấy identity profile theo student_id
export const getIdentityProfileByStudentId = async (req, res) => {
  try {
    const { student_id } = req.params;
    const profile = await IdentityProfileModel.findOne({ student_id });

    if (!profile) {
      return res.status(404).json({
        message: "Identity profile not found",
        status: false,
      });
    }

    return res.status(200).json({
      message: "Identity profile retrieved successfully",
      status: true,
      data: profile,
    });
  } catch (error) {
    console.error("Error getting identity profile:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [PUT] /:id - Cập nhật identity profile
export const updateIdentityProfile = async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = { ...req.body, updated_at: new Date() };

    // Nếu có student_id trong update data, kiểm tra duplicate
    if (updateData.student_id) {
      const existingProfile = await IdentityProfileModel.findOne({
        student_id: updateData.student_id,
        _id: { $ne: id },
      });

      if (existingProfile) {
        return res.status(400).json({
          message: "Student ID already exists",
          status: false,
        });
      }
    }

    const updatedProfile = await IdentityProfileModel.findByIdAndUpdate(
      id,
      updateData,
      { new: true, runValidators: true }
    );

    if (!updatedProfile) {
      return res.status(404).json({
        message: "Identity profile not found",
        status: false,
      });
    }

    return res.status(200).json({
      message: "Identity profile updated successfully",
      status: true,
      data: updatedProfile,
    });
  } catch (error) {
    console.error("Error updating identity profile:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [DELETE] /:id - Xóa identity profile
export const deleteIdentityProfile = async (req, res) => {
  try {
    const { id } = req.params;
    const deletedProfile = await IdentityProfileModel.findByIdAndDelete(id);

    if (!deletedProfile) {
      return res.status(404).json({
        message: "Identity profile not found",
        status: false,
      });
    }

    return res.status(200).json({
      message: "Identity profile deleted successfully",
      status: true,
      data: deletedProfile,
    });
  } catch (error) {
    console.error("Error deleting identity profile:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [GET] /method/:method - Lấy identity profiles theo method
export const getIdentityProfilesByMethod = async (req, res) => {
  try {
    const { method } = req.params;
    
    if (!["did", "web3"].includes(method)) {
      return res.status(400).json({
        message: "Invalid method. Must be 'did' or 'web3'",
        status: false,
      });
    }

    const profiles = await IdentityProfileModel.find({ method }).sort({ created_at: -1 });

    return res.status(200).json({
      message: `Identity profiles with method '${method}' retrieved successfully`,
      status: true,
      data: profiles,
      count: profiles.length,
    });
  } catch (error) {
    console.error("Error getting identity profiles by method:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};

// [GET] /search - Tìm kiếm identity profiles
export const searchIdentityProfiles = async (req, res) => {
  try {
    const { q, method } = req.query;
    
    let query = {};
    
    if (q) {
      query.$or = [
        { name: { $regex: q, $options: "i" } },
        { description: { $regex: q, $options: "i" } },
        { student_id: { $regex: q, $options: "i" } },
      ];
    }
    
    if (method && ["did", "web3"].includes(method)) {
      query.method = method;
    }

    const profiles = await IdentityProfileModel.find(query).sort({ created_at: -1 });

    return res.status(200).json({
      message: "Search completed successfully",
      status: true,
      data: profiles,
      count: profiles.length,
      query: { q, method },
    });
  } catch (error) {
    console.error("Error searching identity profiles:", error);
    return res.status(500).json({
      message: "Internal server error",
      status: false,
      error: error.message,
    });
  }
};
