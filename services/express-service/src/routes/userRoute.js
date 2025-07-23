import express from "express";
import * as authController from "../controllers/authController.js";
import jwtMiddleware from "../middleware/middleware.js";
const userRouter = express.Router();

userRouter.post("/login", authController.login);
userRouter.post("/register", authController.register);
userRouter.post("/verify-email", authController.verifyEmail);
userRouter.get('/get-me', jwtMiddleware, authController.getMe);
userRouter.post('/logout', jwtMiddleware, authController.logout);

// userRouter.delete("/delete_account/:id",jwtMiddleware,authController.deleteAccount);
// userRouter.get("/", authController.getAllUsers);
// userRouter.get("/:id", authController.getUserById);
// userRouter.put("/:id", authController.updateUser);
// userRouter.delete("/:id", authController.deleteUser);

export default userRouter;
