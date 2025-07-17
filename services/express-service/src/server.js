import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import routes from "./routes/index.js";
import setupSwagger from "./swagger.js";
import bodyParser from "body-parser";

import cookieParser from "cookie-parser";
dotenv.config();

const server = express();
// Parse application/json
server.use(bodyParser.json());

// Parse application/x-www-form-urlencoded
server.use(bodyParser.urlencoded({ extended: true }));
server.use(express.json());
server.use(
  cors({
    origin: "http://localhost:3000", // Frontend origin
    credentials: true, // Allow cookies and credentials
  })
);
server.use(cookieParser());

setupSwagger(server);
routes(server);

const PORT = process.env.PORT || 5000;
console.log("port", process.env.PORT);
server.listen(PORT, () => {
  console.log(`App listening at http://localhost:${PORT}`);

  // Open Swagger UI in the browser automatically
  // open("http://localhost:5000/api-docs");
});
