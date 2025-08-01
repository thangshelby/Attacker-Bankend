from .base_agent import BaseAgent
from llama_index.llms.openai import OpenAI
import json

class CriticalAgent(BaseAgent):
    """Critical Agent - Phản biện và đánh giá quyết định của các agent khác"""
    
    def __init__(self, name="CriticalAgent", coordinator=None):
        super().__init__(name, coordinator)
        self.llm = OpenAI(model="gpt-4o-mini", temperature=0.3)
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
            
            # Simple prompt - no complex examples
            prompt = (
                f"Phản biện quyết định {decision}.\n"
                f"Lý do: {reason}\n\n"
                f"Trả lời ngắn gọn:\n"
                f"PHẢN BIỆN: [1 câu phản biện]\n"
                f"KHUYẾN NGHỊ: APPROVE hoặc REJECT"
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
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
                    "recommended_decision": recommended_decision
                }
                
                print(f"[CriticalAgent] ✅ Critique: {recommended_decision}")
                self.send_message(sender, f"{message_type}_critical_response", response_data)
                
            except Exception as e:
                print(f"[CriticalAgent] ❌ Error: {e}")
                # Simple fallback
                fallback_response = {
                    "critical_response": f"Cần xem xét lại quyết định {decision}",
                    "recommended_decision": "reject" if decision == "approve" else "approve"
                }
                self.send_message(sender, f"{message_type}_critical_response", fallback_response)
        else:
            error_payload = {"error": f"Message type '{message_type}' not supported"}
            self.send_message(sender, "unsupported_message", error_payload)