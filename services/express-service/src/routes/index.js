import userRouter from "../routes/userRoute.js";
import studentRouter from "./studentRoute.js";
import loanRouter from "./loanRoute.js";
import identityRouter from "./identityRoute.js";
import academicRouter from "./academicRoute.js";
import chatRouter from "./chatRoute.js";
import { uploadImage } from "../services/cloudinary.service.js";
import { upload } from "../server.js"; // Import the multer upload instance

export default function routes(server) {
  server.use("/api/v1/users", userRouter);
  server.use("/api/v1/students", studentRouter);
  server.use("/api/v1/identity", identityRouter);
  server.use("/api/v1/academic", academicRouter);
  server.use("/api/v1/loans", loanRouter);
  server.use("/api/v1", chatRouter); // Chat routes
  server.use("/api/v1/images/upload_image", upload.single("image"), uploadImage);
}
