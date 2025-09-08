import StudentModel from "../models/studentModel.js";

export const getStudent = async (req, res) => {
  const { citizen_id } = req.params;
  try {
    const student = await StudentModel.findOne({ citizen_id });
    if (!student) {
      return res.status(404).json({
        message: "Student not found",
        status: false,
      });
    }
    res.status(200).json({
      message: "Student fetched successfully",
      data: {
        student,
      },
      status: true,
    });
  } catch (error) {
    console.error("Get Student Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};

export const updateStudent = async (req, res) => {
  console.log('🚀 Student Controller - Update request received');
  console.log('📊 Request body:', req.body);
  
  const {
    student_id,
    citizen_id,
    university,
    faculty_name,
    major_name,
    year_of_study,
    class_id,
    student_card_front, 
    student_card_back,
  } = req.body;

  try {
    if (!citizen_id) {
      console.log('❌ Missing citizen_id');
      return res.status(400).json({ message: "citizen_id is required" });
    }

    console.log('🔍 Looking for student with citizen_id:', citizen_id);
    let student = await StudentModel.findOne({ citizen_id });

    if (!student) {
      console.log('➕ Creating new student');
      student = new StudentModel({ citizen_id }); // Khởi tạo luôn với citizen_id
    } else {
      console.log('✅ Found existing student:', student._id);
    }

    // ✅ Extract URL from Cloudinary response object
    const extractImageUrl = (imageData) => {
      if (!imageData) return null;
      if (typeof imageData === 'string') return imageData; // Already a URL
      if (typeof imageData === 'object' && imageData.url) return imageData.url; // Extract URL from object
      return null;
    };

    // Cập nhật chỉ khi có giá trị (đảm bảo không override field đang có với undefined/null)
    if (student_id !== undefined && student_id != student.student_id) {
      student.student_id = student_id;
    }
    if (university !== undefined) student.university = university;
    if (faculty_name !== undefined) student.faculty_name = faculty_name;
    if (major_name !== undefined) student.major_name = major_name;
    if (year_of_study !== undefined) student.year_of_study = year_of_study;
    if (class_id !== undefined) student.class_id = class_id;
    
    // ✅ Extract URLs for student cards
    if (student_card_front !== undefined) {
      const frontUrl = extractImageUrl(student_card_front);
      student.student_card_front = frontUrl ?? student.student_card_front;
    }
    if (student_card_back !== undefined) {
      const backUrl = extractImageUrl(student_card_back);  
      student.student_card_back = backUrl ?? student.student_card_back;
    }  
    // if (web3_address !== undefined) student.web3_address = web3_address;
    // if (did !== undefined) student.did = did;

    student.updated_at = new Date();

    console.log('💾 Saving student data...');
    console.log('📊 Student data to save:', {
      student_id: student.student_id,
      university: student.university,
      student_card_front: student.student_card_front,
      student_card_back: student.student_card_back
    });
    await student.save();
    console.log('✅ Student saved successfully');

    res.status(200).json({ message: "Student updated successfully", student });
  } catch (error) {
    console.error("❌ Update Student Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
export const updateStudentDIDById = async (req, res) => {
  const { id } = req.params;
  const { did } = req.body;

  try {
    const student = await StudentModel.findById(id);
    if (!student) {
      return res.status(404).json({ message: "Student not found" });
    }

    student.did = did;
    await student.save();

    res
      .status(200)
      .json({ message: "Student DID updated successfully", student });
  } catch (error) {
    console.error("Update Student DID Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
