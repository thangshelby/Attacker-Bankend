import { GoogleGenerativeAI } from "@google/generative-ai";
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Gemini AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Test Gemini API using official library
async function testGeminiAPI() {
  try {
    // Get the model
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
    
    // Test with a sample image URL
    const imageUrl = 'https://example.com/sample-cccd.jpg';
    
    // Convert image URL to base64
    const imageResponse = await fetch(imageUrl);
    const imageBuffer = await imageResponse.arrayBuffer();
    const base64Image = Buffer.from(imageBuffer).toString('base64');
    
    // Create image part
    const imagePart = {
      inlineData: {
        data: base64Image,
        mimeType: "image/jpeg"
      }
    };
    
    // Generate content
    const result = await model.generateContent([
      "Extract Vietnamese citizen ID information from this image. Return only JSON format with these fields: name, citizen_id, birth_date, gender, address.",
      imagePart
    ]);
    
    const response = await result.response;
    const text = response.text();
    
    console.log('Gemini Response:', text);
    
    // Try to parse as JSON
    try {
      const ocrData = JSON.parse(text);
      console.log('Parsed OCR Data:', ocrData);
    } catch (parseError) {
      console.log('Response is not valid JSON:', text);
    }
    
  } catch (error) {
    console.error('Test Error:', error.message);
  }
}

// Run test
testGeminiAPI();
