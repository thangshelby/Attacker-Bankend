import StudentModel from "../models/studentModel.js";
import SupporterModel from "../models/supporterModel.js";

export const updateStudentById = async (req, res) => {
  const {
    student_id,
    citizen_id,
    university,
    faculty_name,
    major_name,
    year_of_study,
    class_id,
    web3_address,
    did,
  } = req.body;

  try {
    if (!citizen_id) {
      return res.status(400).json({ message: "citizen_id is required" });
    }

    let student = await StudentModel.findOne({ citizen_id });

    if (!student) {
      student = new StudentModel({ citizen_id }); // Khởi tạo luôn với citizen_id
    }

    // Cập nhật chỉ khi có giá trị (đảm bảo không override field đang có với undefined/null)
    if (student_id !== undefined) student.student_id = student_id;
    if (university !== undefined) student.university = university;
    if (faculty_name !== undefined) student.faculty_name = faculty_name;
    if (major_name !== undefined) student.major_name = major_name;
    if (year_of_study !== undefined) student.year_of_study = year_of_study;
    if (class_id !== undefined) student.class_id = class_id;
    if (web3_address !== undefined) student.web3_address = web3_address;
    if (did !== undefined) student.did = did;

    student.updated_at = new Date();

    await student.save();

    res.status(200).json({ message: "Student updated successfully", student });
  } catch (error) {
    console.error("Update Student Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
