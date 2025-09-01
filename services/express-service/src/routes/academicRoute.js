import express from "express";
import * as academicController from "../controllers/academicController.js";
const academicRouter = express.Router();

// GET - Lấy thông tin học tập
academicRouter.get(
  "/get_record/:student_id",
  academicController.getAcademicRecords
);

// POST - Tạo thông tin học tập mới
academicRouter.post(
  "/create",
  academicController.createAcademicRecord
);

// PUT - Cập nhật thông tin học tập
academicRouter.put(
  "/update/:student_id",
  academicController.updateAcademicRecord
);

// POST - Upload bảng điểm
academicRouter.post(
  "/upload_transcripts/:student_id",
  academicController.uploadTranscripts
);

export default academicRouter;
