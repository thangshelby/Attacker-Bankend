import express from "express";
import * as studentController from "../controllers/studentController.js";

const studentRouter = express.Router();

studentRouter.put("/update_student", studentController.updateStudentById);

export default studentRouter;
