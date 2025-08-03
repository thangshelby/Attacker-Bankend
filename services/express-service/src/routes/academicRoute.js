import express from "express";
import * as academicController from "../controllers/academicController.js";
const academicRouter = express.Router();

academicRouter.get(
  "/get_record/:student_id",
  academicController.getAcademicRecords
);

export default academicRouter;
