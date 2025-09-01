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

// Create new academic record
export const createAcademicRecord = async (req, res) => {
  try {
    const {
      student_id,
      gpa = 0,
      current_gpa = 0,
      total_credits_earned = 0,
      failed_course_count = 0,
      achievement_award_count = 0,
      has_scholarship = false,
      scholarship_count = 0,
      club = "",
      extracurricular_activity_count = 0,
      has_leadership_role = false,
      study_year,
      term,
      transcripts = []
    } = req.body;

    // Validate required fields
    if (!student_id || !study_year || term === undefined) {
      return res.status(400).json({
        message: "student_id, study_year, and term are required fields"
      });
    }

    // Check if academic record already exists
    const existingRecord = await AcademicModel.findOne({ student_id });
    if (existingRecord) {
      return res.status(409).json({
        message: "Academic record already exists for this student"
      });
    }

    // Create new academic record
    const newAcademicRecord = new AcademicModel({
      student_id,
      gpa,
      current_gpa,
      total_credits_earned,
      failed_course_count,
      achievement_award_count,
      has_scholarship,
      scholarship_count,
      club,
      extracurricular_activity_count,
      has_leadership_role,
      study_year,
      term,
      transcripts
    });

    const savedRecord = await newAcademicRecord.save();

    res.status(201).json({
      message: "Academic record created successfully",
      data: {
        academic: savedRecord
      }
    });
  } catch (error) {
    console.error("Error creating academic record:", error);
    if (error.name === 'ValidationError') {
      return res.status(400).json({
        message: "Validation error",
        errors: Object.values(error.errors).map(err => err.message)
      });
    }
    res.status(500).json({ message: "Internal server error" });
  }
};

// Update existing academic record
export const updateAcademicRecord = async (req, res) => {
  try {
    const studentId = req.params.student_id;
    const updateData = req.body;

    // Remove fields that shouldn't be updated
    delete updateData.student_id;
    delete updateData.created_at;
    delete updateData._id;

    // Update timestamp
    updateData.updated_at = new Date();

    const updatedRecord = await AcademicModel.findOneAndUpdate(
      { student_id: studentId },
      updateData,
      { 
        new: true, 
        runValidators: true,
        upsert: false 
      }
    );

    if (!updatedRecord) {
      return res.status(404).json({
        message: "Academic record not found for this student"
      });
    }

    res.status(200).json({
      message: "Academic record updated successfully",
      data: {
        academic: updatedRecord
      }
    });
  } catch (error) {
    console.error("Error updating academic record:", error);
    if (error.name === 'ValidationError') {
      return res.status(400).json({
        message: "Validation error",
        errors: Object.values(error.errors).map(err => err.message)
      });
    }
    res.status(500).json({ message: "Internal server error" });
  }
};

// Upload transcripts
export const uploadTranscripts = async (req, res) => {
  try {
    const studentId = req.params.student_id;
    const { transcripts } = req.body;

    if (!transcripts || !Array.isArray(transcripts) || transcripts.length === 0) {
      return res.status(400).json({
        message: "Transcripts array is required and must not be empty"
      });
    }

    // Validate each transcript
    for (const transcript of transcripts) {
      if (!transcript.file_url || !transcript.file_name || !transcript.file_type) {
        return res.status(400).json({
          message: "Each transcript must have file_url, file_name, and file_type"
        });
      }
    }

    const academicRecord = await AcademicModel.findOne({ student_id: studentId });
    
    if (!academicRecord) {
      return res.status(404).json({
        message: "Academic record not found for this student"
      });
    }

    // Add new transcripts
    academicRecord.transcripts.push(...transcripts);
    await academicRecord.save();

    res.status(200).json({
      message: "Transcripts uploaded successfully",
      data: {
        transcripts: academicRecord.transcripts
      }
    });
  } catch (error) {
    console.error("Error uploading transcripts:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
