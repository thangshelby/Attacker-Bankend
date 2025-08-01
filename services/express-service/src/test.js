import { MongoClient } from "mongodb";

const client = new MongoClient(
  "mongodb+srv://thangnnd22414:S3HfhztmwyyYL2G3@cluster0.cnqmsmh.mongodb.net/Attacker_Database"
);
await client.connect();

const db = client.db("Attacker_Database");
console.log(db);

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

// console.log(results);
