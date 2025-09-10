import express from "express";
import * as authController from "../controllers/authController.js";
import * as userController from "../controllers/userController.js";
import jwtMiddleware from "../middleware/middleware.js";
const userRouter = express.Router();


userRouter.get('/send_otp/:email', authController.sendOtp);
userRouter.get("/get-me", jwtMiddleware, authController.getMe);
userRouter.get("/:citizen_id",  userController.getAllUsers);
userRouter.post("/login", authController.login);
userRouter.post("/register", authController.register);
userRouter.post("/verify-email", authController.verifyEmail);
userRouter.post('/resend-otp', authController.resendOtp);
userRouter.post("/logout", jwtMiddleware, authController.logout);
userRouter.put("/update_user", userController.updateUser);
userRouter.post("/verify-otp-loan", authController.verifyOtpLoan);


// userRouter.get("/all_users", userController.getAllUsers);
// userRouter.get("/user/:id", userController.getUserById);
// userRouter.get("/school/:schoolName", userController.getUsersBySchoolName);
// userRouter.get("/school_id/:schoolId", userController.getUsersBySchoolId);
// userRouter.get("/role/:role", userController.getUsersByRole);
// userRouter.delete("/delete_user/:id", userController.deleteUserById);

export default userRouter;
    