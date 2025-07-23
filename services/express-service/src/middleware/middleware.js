import { verifyAccessToken } from "../services/jwt.service.js";

const jwtMiddleware = (req, res, next) => {
  try {
    const authHeader = req.headers.authorization; // ✅ đúng là "authorization", không phải "authentication"

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return res
        .status(401)
        .json({ message: "No or invalid authorization header" });
    }   

    const token = authHeader.split(" ")[1]; // Lấy token từ header

    const decoded = verifyAccessToken(token); // Verify token

    if (!decoded) {
      return res.status(401).json({ message: "Expired Token " });
    }
    
    req.userId = decoded.userId ; 
    next()
  } catch (error) {
    console.error(error)
    return res.status(401).json({ message: "Unauthorized" });
  }
};

export default jwtMiddleware;
