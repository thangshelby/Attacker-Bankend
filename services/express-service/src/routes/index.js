import userRouter from "../routes/userRoute.js";
import studentRouter from "./studentRoute.js";
import supporterRouter from "./supporterRoute.js";
import pythonRouter from "./pythonRoute.js";
import identityRouter from "./identityRoute.js";

export default function routes(server) {
  server.use("/api/v1/users", userRouter);
  server.use("/api/v1/students", studentRouter);
  server.use("/api/v1/identity_profile", identityRouter);
  server.use("/api/v1/supporters", supporterRouter);
  server.use("/api/v1/python", pythonRouter);
}
