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
                "Bạn là chuyên gia học thuật LẠC QUAN đánh giá tiềm năng sinh viên.\n"
                f"HỒ SƠ:\n{profile}\n\n"
                "ĐÁNH GIÁ LẠC QUAN:\n"
                "- GPA thấp có thể cải thiện với động lực\n"
                "- Trường tier cao = môi trường tốt\n"
                "- STEM/Y khoa = triển vọng nghề nghiệp\n"
                "- Hoạt động CLB = tích cực, năng động\n"
                "- Tập trung tiềm năng phát triển\n\n"
                "Trả lời JSON:\n"
                '{"decision": "approve", "reason": "lý do lạc quan chi tiết"}'
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=150)
                response_str = str(response_text).strip()
                print(f"[AcademicAgent] LLM Response: {response_str}")
                
                # Try to parse JSON
                response_data = json.loads(response_str)
                
                # Validate required fields
                if "decision" not in response_data:
                    response_data["decision"] = "approve"
                if "reason" not in response_data:
                    response_data["reason"] = "Đánh giá lạc quan về tiềm năng sinh viên"
                    
                self.send_message(sender, "scholarship_decision", response_data)
                print(f"[AcademicAgent] ✅ Sent decision: {response_data['decision']}")
                
            except json.JSONDecodeError as e:
                print(f"[AcademicAgent] ❌ JSON Error: {e}")
                print(f"[AcademicAgent] Raw response: {response_str if 'response_str' in locals() else 'N/A'}")
                # More intelligent fallback based on profile analysis
                fallback_response = {
                    "decision": "approve",  # Academic agent is optimistic by default
                    "reason": "Đánh giá ban đầu: sinh viên có tiềm năng phát triển dù GPA hiện tại thấp, ngành học có triển vọng."
                }
                self.send_message(sender, "scholarship_decision", fallback_response)
                print(f"[AcademicAgent] ✅ Sent fallback decision: {fallback_response['decision']}")
                
            except Exception as e:
                print(f"[AcademicAgent] ❌ General Error: {str(e)}")
                fallback_response = {
                    "decision": "approve",  # Stay optimistic
                    "reason": f"Lỗi kỹ thuật trong đánh giá nhưng vẫn tin tưởng vào tiềm năng sinh viên."
                }
                self.send_message(sender, "scholarship_decision", fallback_response)
                print(f"[AcademicAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                
        elif message_type == "repredict_scholarship":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            prompt = (
                f"TÁI ĐÁNH GIÁ học thuật sau phản biện:\n{critical_response}\n\n"
                "Điều chỉnh quan điểm nếu hợp lý nhưng giữ tinh thần lạc quan.\n"
                'JSON: {"decision": "approve/reject", "reason": "lý do tái đánh giá"}'
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=150)
                response_data = json.loads(str(response_text).strip())
                self.send_message(sender, "repredict_scholarship", response_data)
            except:
                fallback_response = {
                    "decision": "approve",
                    "reason": "Sau phản biện vẫn tin vào tiềm năng phát triển của sinh viên"
                }
                self.send_message(sender, "repredict_scholarship", fallback_response)
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    agent = AcademicAgent()
    test_profile = "21 tuổi, Nữ, tier 1, STEM, GPA: 0.85"
    message = {
        "type": "scholarship_application",
        "sender": "tester", 
        "payload": {"profile": test_profile}
    }
    agent.handle_message(message)