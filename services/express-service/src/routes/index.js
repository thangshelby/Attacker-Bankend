import userRouter from "../routes/userRoute.js";
import studentRouter from "./studentRoute.js";
import loanRouter from "./loanRoute.js";
import identityRouter from "./identityRoute.js";
import academicRouter from "./academicRoute.js";

export default function routes(server) {
  server.use("/api/v1/users", userRouter);
  server.use("/api/v1/students", studentRouter);
  server.use("/api/v1/identity", identityRouter);
  server.use("/api/v1/academic", academicRouter);
  server.use("/api/v1/loans", loanRouter);
  // server.use("/api/v1/supporters", supporterRouter);
}
