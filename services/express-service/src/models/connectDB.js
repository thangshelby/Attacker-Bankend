import { MongoClient } from "mongodb";
import dotenv from "dotenv";
import mongoose from "mongoose";
dotenv.config();

export const connectDatabase = async () => {
  await mongoose.connect(process.env.CONNECTION_STRING).catch(() => {
    console.log("Not able to connect to database");
  });

  const client = new MongoClient(process.env.CONNECTION_STRING);
  await client.connect();

  const db = client.db(process.env.DATABASE_NAME);
  //   console.log(db);
  const results = await db
    .collection("users")
    .aggregate([
      {
        $lookup: {
          from: "students",
          localField: "citizen_id",
          foreignField: "citizen_id",
          as: "student_info",
        },
      },
      { $unwind: "$student_info" },
      {
        $match: {
          "student_info.university": "UEL",
        },
      },
    ])
    .toArray();

  //   console.log(results);

  return db;
};
