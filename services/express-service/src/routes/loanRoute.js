import express from "express";
import * as loanController from "../controllers/loanController.js";
// import client from "../grpcClient.js"; // Adjust the path as necessary

const loanRouter = express.Router();

loanRouter.get("/hello", (req, res) => {
  return res.status(200).json({ message: "Hello, world!" });
});

loanRouter.post("/loan_request", async (req, res) => {
  const response = await fetch(`${process.env.SERVICE_2_API}/debate-loan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req.body),
  });
  const ress = await response.json();
  loanController.storeMASConversation(ress);

//   console.log(ress);
  return res.status(response.status).json(ress);
});

export default loanRouter;
