import json
import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from .base_agent import BaseAgent

class AcademicAgent(BaseAgent):
    def __init__(self, name="AcademicAgent", coordinator=None):
        super().__init__(name, coordinator)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường.")
        self.llm = OpenAI(api_key=api_key, model='gpt-4.1-nano')

    def handle_message(self, message: dict):
        """
        Xử lý tin nhắn và gửi phản hồi lại cho người gửi ban đầu.
        """
        message_type = message.get("type")
        sender = message.get("sender")

        if message_type == "scholarship_application":
            profile = message.get("payload", {}).get("profile", "")
            if not profile:
                error_payload = {"error": "Hồ sơ học tập không được cung cấp."}
                self.send_message(sender, "scholarship_decision_error", error_payload)
                return

            prompt = (
                "Bạn là một chuyên gia học thuật. Hãy phân tích hồ sơ học tập sau và quyết định có cấp học bổng không, giải thích lý do một cách chi tiết và chuyên nghiệp:\n"
                f"Hồ sơ học tập:\n{profile}\n\n"
                "QUAN TRỌNG: Chỉ trả lời dưới dạng một chuỗi JSON hợp lệ theo format sau: "
                "{\"decision\": \"approve\" hoặc \"reject\", \"reason\": \"<lý do chi tiết>\"}"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_data = json.loads(str(response_text))
                self.send_message(sender, "scholarship_decision", response_data)
            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                self.send_message(sender, "scholarship_decision_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                self.send_message(sender, "scholarship_decision_error", error_payload)
        elif message_type == "repredict_scholarship":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            prompt = (
                "Bạn là chuyên gia học thuật. Dưới đây là lịch sử tranh luận và phản biện về hồ sơ học bổng. "
                "Hãy dựa vào toàn bộ lịch sử và phản biện để ra quyết định cuối cùng (approve/reject) và giải thích lý do chi tiết:\n"
                f"Lịch sử hội thoại: {memory}\n"
                f"Phản biện từ agent phản biện: {critical_response}\n"
                "QUAN TRỌNG: Chỉ trả lời dưới dạng một chuỗi JSON hợp lệ theo format: "
                "{\"decision\": \"approve\" hoặc \"reject\", \"reason\": \"<lý do chi tiết>\"}"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_data = json.loads(str(response_text))
                self.send_message(sender, "repredict_scholarship", response_data)
            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                # Fallback: luôn gửi một quyết định mặc định để không bị null
                self.send_message(sender, "repredict_scholarship", {
                    "decision": "reject",
                    "reason": "LLM trả về không hợp lệ."
                })
                self.send_message(sender, "repredict_scholarship_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                # Fallback: luôn gửi một quyết định mặc định để không bị null
                self.send_message(sender, "repredict_scholarship", {
                    "decision": "reject",
                    "reason": f"Lỗi xử lý: {str(e)}"
                })
                self.send_message(sender, "repredict_scholarship_error", error_payload)
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Tạo agent
    agent = AcademicAgent()
    # Hồ sơ học tập mẫu để test
    test_profile = "Sinh viên: Trần Thị B, GPA 3.9/4.0, đạt giải Nhất Olympic Toán, hoạt động ngoại khóa xuất sắc."
    # Message mẫu
    message = {
        "type": "scholarship_application",
        "sender": "tester",
        "payload": {"profile": test_profile}
    }
    # Gửi message và in kết quả
    agent.handle_message(message)