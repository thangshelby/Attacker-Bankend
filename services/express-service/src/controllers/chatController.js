import ChatbotService from "../services/pythonService/chatbot.service.js";

// Chat with RAG bot via gRPC
export const chatWithBot = async (req, res) => {
  const startTime = Date.now();

  try {
    const { message, citizen_id} = req.body;

    // Validate input
    if (
      !message ||
      typeof message !== "string" ||
      message.trim().length === 0
    ) {
      return res.status(400).json({
        success: false,
        error: "Tin nhắn không được để trống",
      });
    }

    // Call Python service via gRPC
    const response = await ChatbotService.chat_v2(
      message,
      citizen_id,
    );
    // const response = await ChatbotService.chat(message, conversation_id);

    const responseTime = Date.now() - startTime;

    // Return successful response
    res.json({
      success: true,
      question: response.question,
      response: response.answer,
      sources: response.sources,
      processing_time: response.processing_time,
      response_time: responseTime,
    //   conversation_id: conversation_id,
    });
  } catch (error) {
    const responseTime = Date.now() - startTime;
    console.error("❌ Chat error:", error);

    // Return error response
    res.status(500).json({
      success: false,
      error: "Xin lỗi, tôi không thể trả lời lúc này. Vui lòng thử lại sau.",
      details: error.message,
      response_time: responseTime,
    });
  }
};

// Health check for chatbot service
export const chatHealthCheck = async (req, res) => {
  try {
    const isHealthy = await ChatbotService.healthCheck();

    res.json({
      success: true,
      chatbot_service: isHealthy ? "healthy" : "unhealthy",
      grpc_connection: ChatbotService.connected,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Chatbot health check error:", error);

    res.status(500).json({
      success: false,
      chatbot_service: "unhealthy",
      grpc_connection: false,
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
};
