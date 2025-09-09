import express from "express";
import * as studentController from "../controllers/studentController.js";

const studentRouter = express.Router();


studentRouter.get('/:citizen_id', studentController.getStudent);
studentRouter.put("/update_student", studentController.updateStudent);
studentRouter.post("/fix-citizen-id", studentController.fixStudentCitizenId); // Temporary fix endpoint

export default studentRouter;
