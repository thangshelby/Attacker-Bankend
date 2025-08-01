import express from "express";
import * as studentController from "../controllers/studentController.js";

const studentRouter = express.Router();


studentRouter.get('/:citizen_id', studentController.getStudent);
studentRouter.put("/update_student", studentController.updateStudent);

export default studentRouter;
