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
                "YÊU CẦU: Trả lời theo format sau (không thêm gì khác):\n"
                "QUYẾT ĐỊNH: REJECT\n"
                "LÝ DO: [lý do thận trọng chi tiết]"
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
                response_str = str(response_text).strip()
                print(f"[FinanceAgent] LLM Response: {response_str}")
                
                # Parse structured text response
                
                import re
                # Extract QUYẾT ĐỊNH and LÝ DO from text
                decision_match = re.search(r'QUYẾT ĐỊNH:\s*(APPROVE|REJECT|CHẤP NHẬN|TỪ CHỐI)', response_str, re.IGNORECASE)
                reason_match = re.search(r'LÝ DO:\s*(.+)', response_str, re.DOTALL | re.IGNORECASE)
                
                if decision_match and reason_match:
                    decision_text = decision_match.group(1).upper()
                    reason_text = reason_match.group(1).strip()
                    
                    # Normalize decision
                    if decision_text in ['APPROVE', 'CHẤP NHẬN']:
                        decision = "approve"
                    else:
                        decision = "reject"
                    
                    response_data = {
                        "decision": decision,
                        "reason": reason_text[:300]  # Limit length
                    }
                    print(f"[FinanceAgent] 📝 Parsed structured response: {decision}")
                else:
                    # Keyword fallback
                    text_lower = response_str.lower()
                    if any(word in text_lower for word in ['approve', 'chấp nhận', 'đồng ý']):
                        decision = "approve"
                    else:
                        decision = "reject"  # Default cautious
                    
                    # Use first sentence as reason
                    sentences = [s.strip() for s in response_str.split('.') if len(s.strip()) > 10]
                    reason = sentences[0][:200] if sentences else "Đánh giá thận trọng về rủi ro tài chính"
                    
                    response_data = {
                        "decision": decision,
                        "reason": reason
                    }
                    print(f"[FinanceAgent] 🔄 Used keyword fallback: {decision}")
                    
                self.send_message(sender, "loan_decision", response_data)
                print(f"[FinanceAgent] ✅ Sent decision: {response_data['decision']}")
                
            except Exception as e:
                print(f"[FinanceAgent] ❌ Error parsing response: {e}")
                print(f"[FinanceAgent] Raw response: {response_str if 'response_str' in locals() else 'N/A'}")
                # Ultimate fallback
                fallback_response = {
                    "decision": "reject",  # Finance agent is cautious by default
                    "reason": "Lỗi hệ thống - áp dụng nguyên tắc thận trọng từ chối để tránh rủi ro"
                }
                self.send_message(sender, "loan_decision", fallback_response)
                print(f"[FinanceAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                

                
        elif message_type == "repredict_loan":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            recommended_decision = message.get("payload", {}).get("recommended_decision", "")
            
            prompt = (
                f"TÁI ĐÁNH GIÁ tài chính sau phản biện từ Critical Agent:\n"
                f"Phản biện: {critical_response}\n"
                f"Khuyến nghị từ Critical Agent: {recommended_decision}\n\n"
                f"HƯỚNG DẪN:\n"
                f"- Xem xét kỹ phản biện và khuyến nghị của Critical Agent\n"
                f"- Điều chỉnh quyết định nếu phản biện có cơ sở\n"
                f"- Giữ thái độ thận trọng nhưng công bằng hơn\n"
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
                    decision = "reject"  # Cautious default
                    reason = "Sau phản biện vẫn giữ thái độ thận trọng về rủi ro tài chính"
                
                response_data = {"decision": decision, "reason": reason}
                self.send_message(sender, "repredict_loan", response_data)
            except Exception as e:
                print(f"[FinanceAgent] ❌ Error in repredict_loan: {str(e)}")
                fallback_response = {
                    "decision": "reject",
                    "reason": "Sau phản biện vẫn giữ thái độ thận trọng về rủi ro tài chính"
                }
                print(f"[FinanceAgent] 🔄 Using fallback response: {fallback_response}")
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