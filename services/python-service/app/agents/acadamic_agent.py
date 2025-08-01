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
                "YÊU CẦU: Trả lời theo format sau (không thêm gì khác):\n"
                "QUYẾT ĐỊNH: APPROVE\n"
                "LÝ DO: [lý do lạc quan chi tiết]"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
                response_str = str(response_text).strip()
                print(f"[AcademicAgent] LLM Response: {response_str}")
                
                # Parse structured text response
                import re
                # Extract QUYẾT ĐỊNH and LÝ DO from text
                decision_match = re.search(r'QUYẾT ĐỊNH:\s*(APPROVE|REJECT|CHẤP NHẬN|TỪ CHỐI)', response_str, re.IGNORECASE)
                reason_match = re.search(r'LÝ DO:\s*(.+)', response_str, re.DOTALL | re.IGNORECASE)
                
                if decision_match and reason_match:
                    decision_text = decision_match.group(1).upper()
                    reason_text = reason_match.group(1).strip()
                    
                    # Normalize decision
                    if decision_text in ['REJECT', 'TỪ CHỐI']:
                        decision = "reject"
                    else:
                        decision = "approve"  # Default optimistic
                    
                    response_data = {
                        "decision": decision,
                        "reason": reason_text[:300]  # Limit length
                    }
                    print(f"[AcademicAgent] 📝 Parsed structured response: {decision}")
                else:
                    # Keyword fallback
                    text_lower = response_str.lower()
                    if any(word in text_lower for word in ['reject', 'từ chối', 'không đồng ý']):
                        decision = "reject"
                    else:
                        decision = "approve"  # Default optimistic
                    
                    # Use first sentence as reason
                    sentences = [s.strip() for s in response_str.split('.') if len(s.strip()) > 10]
                    reason = sentences[0][:200] if sentences else "Đánh giá lạc quan về tiềm năng sinh viên"
                    
                    response_data = {
                        "decision": decision,
                        "reason": reason
                    }
                    print(f"[AcademicAgent] 🔄 Used keyword fallback: {decision}")
                    
                self.send_message(sender, "scholarship_decision", response_data)
                print(f"[AcademicAgent] ✅ Sent decision: {response_data['decision']}")
                
            except Exception as e:
                print(f"[AcademicAgent] ❌ Error parsing response: {e}")
                print(f"[AcademicAgent] Raw response: {response_str if 'response_str' in locals() else 'N/A'}")
                # Ultimate fallback
                fallback_response = {
                    "decision": "approve",  # Academic agent is optimistic by default
                    "reason": "Lỗi hệ thống - vẫn tin tưởng vào tiềm năng phát triển của sinh viên"
                }
                self.send_message(sender, "scholarship_decision", fallback_response)
                print(f"[AcademicAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                

                
        elif message_type == "repredict_scholarship":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            recommended_decision = message.get("payload", {}).get("recommended_decision", "")
            
            prompt = (
                f"TÁI ĐÁNH GIÁ học thuật sau phản biện từ Critical Agent:\n"
                f"Phản biện: {critical_response}\n"
                f"Khuyến nghị từ Critical Agent: {recommended_decision}\n\n"
                f"HƯỚNG DẪN:\n"
                f"- Xem xét kỹ phản biện và khuyến nghị của Critical Agent\n"
                f"- Điều chỉnh quyết định nếu phản biện có lý\n"
                f"- Giữ tinh thần lạc quan nhưng thực tế hơn\n"
                f"- Nếu Critical Agent khuyến nghị '{recommended_decision}', hãy cân nhắc nghiêm túc\n\n"
                'YÊU CẦU: Trả lời theo format sau:\n'
                'QUYẾT ĐỊNH: APPROVE/REJECT\n'
                'LÝ DO: [lý do tái đánh giá sau khi xem xét phản biện]'
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
                response_str = str(response_text).strip()
                
                # Parse structured response for repredict
                import re
                decision_match = re.search(r'QUYẾT ĐỊNH:\s*(APPROVE|REJECT|CHẤP NHẬN|TỪ CHỐI)', response_str, re.IGNORECASE)
                reason_match = re.search(r'LÝ DO:\s*(.+)', response_str, re.DOTALL | re.IGNORECASE)
                
                if decision_match and reason_match:
                    decision_text = decision_match.group(1).upper()
                    decision = "approve" if decision_text in ['APPROVE', 'CHẤP NHẬN'] else "reject"
                    reason = reason_match.group(1).strip()[:300]
                else:
                    decision = "approve"  # Optimistic default
                    reason = "Sau phản biện vẫn tin vào tiềm năng phát triển của sinh viên"
                
                response_data = {"decision": decision, "reason": reason}
                self.send_message(sender, "repredict_scholarship", response_data)
            except Exception as e:
                print(f"[AcademicAgent] ❌ Repredict error: {e}")
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