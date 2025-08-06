import express from 'express';
import { chatWithBot, chatHealthCheck } from '../controllers/chatController.js';

const router = express.Router();

// POST /api/v1/chat - Chat with RAG bot
router.post('/chat', chatWithBot);

// GET /api/v1/chat/health - Health check for chatbot service
router.get('/chat/health', chatHealthCheck);

export default router;