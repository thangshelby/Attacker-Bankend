import exporess from "express";
import * as supporterController from "../controllers/supporterController.js";

const supporterRouter = exporess.Router();

supporterRouter.put(
  "/update_supporter",
  supporterController.updateSupporterByStudentId
);

export default supporterRouter;
