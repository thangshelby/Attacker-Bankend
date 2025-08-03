import AcademicModel from "../models/academicModel.js";

export const getAcademicRecords = async (req, res) => {
  try {
    const studentId = req.params.student_id;
    const academicRecords = await AcademicModel.find({ student_id: studentId });

    if (academicRecords.length === 0) {
      return res
        .status(404)
        .json({ message: "No academic records found for this student." });
    }

    res.status(200).json({
      message: "Academic records retrieved successfully.",
      data: {
        academic: academicRecords[0],
      },
    });
  } catch (error) {
    console.error("Error fetching academic records:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
