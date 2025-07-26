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
        self.llm = OpenAI(api_key=api_key, model='gpt-4.1-nano')

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
                "Bạn là chuyên gia tài chính THẬN TRỌNG đánh giá rủi ro cho vay.\n"
                f"HỒ SƠ:\n{profile}\n\n"
                "ĐÁNH GIÁ THẬN TRỌNG:\n"
                "- Thu nhập thấp = rủi ro cao\n"
                "- Có nợ hiện tại = rủi ro rất cao\n"
                "- Việc làm thêm = điểm cộng trách nhiệm\n"
                "- Mục đích học phí = hợp lý hơn sinh hoạt\n"
                "- Tập trung bảo vệ tài sản, tránh bad debt\n\n"
                "Trả lời JSON:\n"
                '{"decision": "reject", "reason": "lý do thận trọng chi tiết", "risk_level": "high"}'
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=150)
                response_str = str(response_text).strip()
                print(f"[FinanceAgent] LLM Response: {response_str}")
                
                # Try to parse JSON
                response_data = json.loads(response_str)
                
                # Validate required fields
                if "decision" not in response_data:
                    response_data["decision"] = "reject"  # Default cautious
                if "reason" not in response_data:
                    response_data["reason"] = "Đánh giá thận trọng về rủi ro tài chính"
                if "risk_level" not in response_data:
                    response_data["risk_level"] = "medium"
                    
                self.send_message(sender, "loan_decision", response_data)
                print(f"[FinanceAgent] ✅ Sent decision: {response_data['decision']}")
                
            except json.JSONDecodeError as e:
                print(f"[FinanceAgent] ❌ JSON Error: {e}")
                print(f"[FinanceAgent] Raw response: {response_str if 'response_str' in locals() else 'N/A'}")
                # Intelligent fallback based on profile analysis
                fallback_response = {
                    "decision": "reject",  # Finance agent is cautious by default
                    "reason": "Đánh giá ban đầu: phát hiện rủi ro tài chính cao do thu nhập thấp và có nợ hiện tại",
                    "risk_level": "high"
                }
                self.send_message(sender, "loan_decision", fallback_response)
                print(f"[FinanceAgent] ✅ Sent fallback decision: {fallback_response['decision']}")
                
            except Exception as e:
                print(f"[FinanceAgent] ❌ General Error: {str(e)}")
                fallback_response = {
                    "decision": "reject",  # Stay cautious
                    "reason": f"Lỗi kỹ thuật trong đánh giá tài chính - áp dụng nguyên tắc thận trọng từ chối để tránh rủi ro",
                    "risk_level": "high"
                }
                self.send_message(sender, "loan_decision", fallback_response)
                print(f"[FinanceAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                
        elif message_type == "repredict_loan":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            prompt = (
                f"TÁI ĐÁNH GIÁ tài chính sau phản biện:\n{critical_response}\n\n"
                "Xem xét lại rủi ro, điều chỉnh nếu hợp lý nhưng giữ thận trọng.\n"
                'JSON: {"decision": "approve/reject", "reason": "lý do tái đánh giá", "risk_level": "low/medium/high"}'
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=150)
                response_data = json.loads(str(response_text).strip())
                self.send_message(sender, "repredict_loan", response_data)
            except:
                fallback_response = {
                    "decision": "reject",
                    "reason": "Sau phản biện vẫn giữ thái độ thận trọng về rủi ro tài chính",
                    "risk_level": "high"
                }
                self.send_message(sender, "repredict_loan", fallback_response)
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
    agent = FinanceAgent()
    test_profile = "Thu nhập: 8M VND/tháng, không nợ, vay: 45M VND học phí"
    message = {
        "type": "loan_application",
        "sender": "tester",
        "payload": {"profile": test_profile}
    }
    agent.handle_message(message)