import json
import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from .base_agent import BaseAgent

class FinanceAgent(BaseAgent):
    def __init__(self, name="FinanceAgent", coordinator=None):
        super().__init__(name, coordinator)
        load_dotenv()
        # Đảm bảo API key được load chính xác
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường.")
        self.llm = OpenAI(api_key=api_key, model='gpt-4.1-mini')

    def handle_message(self, message: dict):
        """
        Xử lý tin nhắn và gửi phản hồi lại cho người gửi ban đầu.
        """
        message_type = message.get("type")
        sender = message.get("sender")

        if message_type == "loan_application":
            profile = message.get("payload", {}).get("profile", "")
            if not profile:
                error_payload = {"error": "Hồ sơ không được cung cấp."}
                self.send_message(sender, "loan_decision_error", error_payload)
                return

            prompt = (
                "Bạn là một chuyên gia tài chính cực kỳ cẩn trọng. Hãy phân tích hồ sơ sau và quyết định có duyệt vay không, giải thích lý do một cách chi tiết và chuyên nghiệp:\n"
                f"Hồ sơ khách hàng:\n{profile}\n\n"
                "QUAN TRỌNG: Chỉ trả lời dưới dạng một chuỗi JSON hợp lệ theo format sau: "
                "{\"decision\": \"approve\" hoặc \"reject\", \"reason\": \"<lý do chi tiết>\"}"
            )
            
            try:
                response_text = self.llm.complete(prompt)
                response_data = json.loads(str(response_text))
                
                # Gửi tin nhắn phản hồi có cấu trúc
                self.send_message(sender, "loan_decision", response_data)

            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                self.send_message(sender, "loan_decision_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                self.send_message(sender, "loan_decision_error", error_payload)
        else:
            # Gửi lại tin nhắn lỗi nếu không xử lý được
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")


if __name__ == "__main__":
    # Tạo agent
    agent = FinanceAgent()
    # Hồ sơ mẫu để test
    test_profile = "Khách hàng: Nguyễn Văn A, thu nhập 20 triệu/tháng, không có nợ xấu, lịch sử tín dụng tốt."
    # Message mẫu
    message = {
        "type": "loan_application",
        "sender": "tester",
        "payload": {"profile": test_profile}
    }
    # Gửi message và in kết quả
    agent.handle_message(message)