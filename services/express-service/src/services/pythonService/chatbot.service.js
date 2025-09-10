import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class Chatbot {
  constructor() {
    this.client = null;
    this.connected = false;
    this.initClient();
  }

  initClient() {
    try {
      // Load protobuf
      const PROTO_PATH = path.join(__dirname, "chatbot.proto");
      const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
      });

      const chatbotProto =
        grpc.loadPackageDefinition(packageDefinition).chatbot;

      // Create client
      this.client = new chatbotProto.ChatbotService(
        "localhost:50051",
        grpc.credentials.createInsecure()
      );

      console.log("🔗 gRPC Chatbot Client initialized (localhost:50051)");
      this.connected = true;
    } catch (error) {
      console.error("❌ Failed to initialize gRPC client:", error);
      this.connected = false;
    }
  }

  async chat(message, conversationId = "web-chat") {
    return new Promise((resolve, reject) => {
      if (!this.connected || !this.client) {
        reject(new Error("gRPC client not connected"));
        return;
      }

      const request = {
        message: message,
        conversation_id: conversationId,
      };

      console.log(`📤 gRPC Request: ${message.substring(0, 50)}...`);

      this.client.chat(request, (error, response) => {
        if (error) {
          console.error("❌ gRPC Error:", error);
          reject(error);
          return;
        }

        console.log(`📥 gRPC Response: ${response.answer.substring(0, 50)}...`);
        resolve({
          question: response.question,
          answer: response.answer,
          sources: response.sources || [],
          processing_time: response.processing_time,
          success: response.success,
          error: response.error,
        });
      });
    });
  }

  async chat_v2(message, citizen_id) {
    const response = await fetch(
      "https://attacker-bankend-t6av.onrender.com/api/v1/chat",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          citizen_id: citizen_id,
          // conversation_id: conversationId,
        }),
      }
    );

    if (!response.ok) {
      console.error("❌ HTTP Error:", response.statusText);
      throw new Error("Failed to communicate with chat API");
    }

    const data = await response.json();
    return data;
  }

  // Health check method
  async healthCheck() {
    try {
      const response = await this.chat("health check", "system");
      return response.success;
    } catch (error) {
      console.error("❌ gRPC Health check failed:", error);
      return false;
    }
  }
}

// Singleton instance
const ChatbotService = new Chatbot();

export default ChatbotService;
