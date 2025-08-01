import SupporterModel from "../models/supporterModel.js";

export const updateSupporterByStudentId = async (req, res) => {
  const {
    student_id,
    supporter_occupation,
    supporter_income_range,
    supporter_job,
    support_relationship,
  } = req.body;

  try {
    if (!student_id) {
      return res.status(400).json({ message: "student_id is required" });
    }

    let supporter = await SupporterModel.findOne({ student_id });

    if (!supporter) {
      supporter = new SupporterModel({ student_id });
    }

    // Chỉ cập nhật nếu có dữ liệu truyền vào
    if (supporter_occupation !== undefined) {
      supporter.supporter_occupation = supporter_occupation;
    }
    if (supporter_income_range !== undefined) {
      supporter.supporter_income_range = supporter_income_range;
    }
    if (supporter_job !== undefined) {
      supporter.supporter_job = supporter_job;
    }
    if (support_relationship !== undefined) {
      supporter.support_relationship = support_relationship;
    }

    supporter.updated_at = new Date();

    await supporter.save();

    res.status(200).json({
      message: "Supporter updated successfully",
      supporter,
    });
  } catch (error) {
    console.error("Update Supporter Error:", error);
    res.status(500).json({ message: "Internal server error" });
  }
};
