import express from "express";
import * as authController from "../controllers/authController.js";

const userRouter = express.Router();

userRouter.post("/login", authController.login);
userRouter.post("/sign-up", authController.signUp);
userRouter.delete("/delete_account/:id", authController.deleteAccount);
userRouter.get("/", authController.getAllUsers);
userRouter.get("/:id", authController.getUserById);
userRouter.put("/:id", authController.updateUser);
userRouter.delete("/:id", authController.deleteUser);

export default userRouter;
