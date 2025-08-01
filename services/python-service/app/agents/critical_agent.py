from .base_agent import BaseAgent
from llama_index.llms.openai import OpenAI
import json

class CriticalAgent(BaseAgent):
    """Critical Agent - Phản biện và đánh giá quyết định của các agent khác"""
    
    def __init__(self, name="CriticalAgent", coordinator=None):
        super().__init__(name, coordinator)
        self.llm = OpenAI(model="gpt-4.1-nano")
        self.persona = "phản biện khách quan"
        
    def handle_message(self, message: dict):
        """Xử lý tin nhắn từ các agent khác"""
        sender = message.get("sender", "unknown")
        message_type = message.get("type", "unknown")
        print(f"[CriticalAgent] Nhận message từ {sender}: {message_type}")
        
        if message_type in ["scholarship_decision", "loan_decision"]:
            payload = message.get("payload", {})
            decision = payload.get("decision", "unknown")
            reason = payload.get("reason", "")
            memory = payload.get("memory", "")
            
            prompt = (
                f"Bạn là CHUYÊN GIA PHẢN BIỆN KHÁCH QUAN với 20 năm kinh nghiệm phân tích rủi ro tín dụng.\n"
                f"QUYẾT ĐỊNH ĐANG XEM XÉT: {decision}\n"
                f"LÝ DO ĐƯỢC ĐƯA RA: {reason}\n"
                f"HỒ SƠ GỐC: {memory}\n\n"
                f"FRAMEWORK PHẢN BIỆN KHÁCH QUAN:\n"
                f"1. LOGIC VÀ BẰNG CHỨNG:\n"
                f"   - Lý do có dựa trên dữ liệu cụ thể?\n"
                f"   - Có thiếu yếu tố quan trọng nào?\n"
                f"   - Tính toán có chính xác?\n\n"
                f"2. RỦI RO CHƯA XEM XÉT:\n"
                f"   - Yếu tố rủi ro bị bỏ qua\n"
                f"   - Giả định không thực tế\n"
                f"   - Hậu quả dài hạn\n\n"
                f"3. QUAN ĐIỂM ĐỐI LẬP:\n"
                f"   - Góc nhìn ngược lại có hợp lý?\n"
                f"   - Dữ liệu có thể giải thích khác?\n"
                f"   - Quyết định có quá lạc quan/thận trọng?\n\n"
                f"YÊU CẦU: Phản biện dựa trên LOGIC và SỐ LIỆU, không chung chung.\n\n"
                f"FORMAT:\n"
                f"PHẢN BIỆN: [Chỉ ra lỗ hổng cụ thể trong lập luận với dữ liệu]\n"
                f"KHUYẾN NGHỊ: APPROVE hoặc REJECT"
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_str = str(response_text).strip()
                print(f"[CriticalAgent] Response: {response_str}")
                
                # Simple parsing - just find APPROVE/REJECT
                if "APPROVE" in response_str.upper():
                    recommended_decision = "approve"
                elif "REJECT" in response_str.upper():
                    recommended_decision = "reject"
                else:
                    # Default: opposite of original decision
                    recommended_decision = "reject" if decision == "approve" else "approve"
                
                # Extract critique (first 100 chars)
                critique = response_str[:100] if response_str else f"Phản biện {decision}"
                
                response_data = {
                    "critical_response": critique,
                    "recommended_decision": recommended_decision,
                    "raw_response": response_str
                }
                
                print(f"[CriticalAgent] ✅ Critique: {recommended_decision}")
                self.send_message(sender, f"{message_type}_critical_response", response_data)
                
            except Exception as e:
                print(f"[CriticalAgent] ❌ Error: {e}")
                # Simple fallback
                fallback_response = {
                    "critical_response": f"Cần xem xét lại quyết định {decision}",
                    "recommended_decision": "reject" if decision == "approve" else "approve",
                    "raw_response": response_str if 'response_str' in locals() else "Error: No LLM response"
                }
                self.send_message(sender, f"{message_type}_critical_response", fallback_response)
        else:
            error_payload = {"error": f"Message type '{message_type}' not supported"}
            self.send_message(sender, "unsupported_message", error_payload)