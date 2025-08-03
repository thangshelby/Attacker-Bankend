import express from "express";
import * as identityController from "../controllers/identityController.js";
import jwtMiddleware from "../middleware/middleware.js";

const identityRouter = express.Router();

identityRouter.post(
  "/create_identity",
  // jwtMiddleware,
  identityController.createIdentityProfile
);

identityRouter.put(
  "/update/:id",
  jwtMiddleware,
  identityController.updateIdentityProfile
);

identityRouter.get(
  "/method/:method",
  jwtMiddleware,
  identityController.getIdentityProfilesByMethod
);

identityRouter.get(
  "/search",
  jwtMiddleware,
  identityController.searchIdentityProfiles
);

export default identityRouter;
