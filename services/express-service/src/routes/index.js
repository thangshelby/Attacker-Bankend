import userRouter from "../routes/userRoute.js";

export default function routes(server) {
  server.use("/api/v1/user", userRouter);
}
