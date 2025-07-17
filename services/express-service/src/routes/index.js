import userRouter from "../routes/userRoute.js";
import pythonRouter from "./pythonRoute.js";

export default function routes(server) {
  server.use("/api/v1/user", userRouter);
  server.use("/api/v1/python", pythonRouter);
}
