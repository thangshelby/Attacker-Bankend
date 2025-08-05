import { v2 as cloudinary } from "cloudinary";
import streamifier from "streamifier";

export async function uploadImage(req, res) {
  cloudinary.config({
    cloud_name: process.env.CLOUDINARY_CLOUD_NAME || "dty2fywoh",
    api_key: process.env.CLOUDINARY_API_KEY || "363384855436924",
    api_secret:
      process.env.CLOUDINARY_API_SECRET || "Bk5XQvlzRZEd7LYYxGyBuLR3Qj0",
  });
  if (!req.file) {
    return res.status(400).json({ message: "No file received" });
  }

  try {
    // Dùng upload_stream để upload từ buffer
    const streamUpload = (buffer) => {
      return new Promise((resolve, reject) => {
        const stream = cloudinary.uploader.upload_stream(
          {
            folder: "attacker", // tùy chỉnh
            resource_type: "image",
            public_id: req.file.originalname.split(".")[0], // tên file không có đuôi
            overwrite: true,
          },
          (error, result) => {
            if (error) return reject(error);
            resolve(result);
          }
        );
        streamifier.createReadStream(buffer).pipe(stream);
      });
    };

    const uploadResult = await streamUpload(req.file.buffer);
    const autoCropUrl = await cloudinary.url(uploadResult.public_id, {
      crop: "auto",
      gravity: "auto",
      width: 500,
      height: 300,
    });

    res.status(200).json({
      message: "Image uploaded successfully",
      url: autoCropUrl,
      info: uploadResult,
    });
  } catch (error) {
    console.error("Upload error:", error);
    res.status(500).json({
      message: "Image upload failed",
      error: error.message || error,
    });
  }
}
