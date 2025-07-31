import json
import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from .base_agent import BaseAgent

class CriticalAgent(BaseAgent):
    def __init__(self, name="CriticalAgent", coordinator=None):
        super().__init__(name, coordinator)
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được tìm thấy trong môi trường.")
        self.llm = OpenAI(api_key=api_key, model='gpt-4.1-nano')

    def handle_message(self, message: dict):
        """
        Nhận quyết định từ agent khác và phản biện lại.
        """
        message_type = message.get("type")
        sender = message.get("sender")
        payload = message.get("payload", {})

        if message_type in ["loan_decision", "scholarship_decision"]:
            decision = payload.get("decision", "")
            reason = payload.get("reason", "")
            risk_level = payload.get("risk_level", "")
            
            # Tạo critique dựa trên agent type
            if sender == "AcademicAgent":
                prompt = (
                    f"PHẢN BIỆN quyết định Academic Agent:\n"
                    f"Quyết định: {decision}\n"
                    f"Lý do: {reason}\n\n"
                    f"CÂU HỎI CHẤT VẤN:\n"
                    f"- GPA hiện tại có thực sự phản ánh hết năng lực?\n"
                    f"- Ngành STEM có đảm bảo việc làm tương lai?\n"
                    f"- Tier 1 có bù đắp được GPA thấp?\n"
                    f"- Có quá lạc quan với thành tích yếu?\n"
                    f"Đưa ra 2-3 điểm phản biện sắc bén."
                )
            elif sender == "FinanceAgent":
                prompt = (
                    f"PHẢN BIỆN quyết định Finance Agent:\n"
                    f"Quyết định: {decision}\n"
                    f"Lý do: {reason}\n"
                    f"Risk level: {risk_level}\n\n"
                    f"CÂU HỎI CHẤT VẤN:\n"
                    f"- Thu nhập 8M có thực sự quá thấp?\n"
                    f"- Nợ hiện tại có nghiêm trọng thế nào?\n"
                    f"- Có quá thận trọng với mục đích học phí?\n"
                    f"- Việc làm thêm có giảm rủi ro?\n"
                    f"Đưa ra 2-3 điểm phản biện cân bằng."
                )
            else:
                prompt = f"Phản biện quyết định của {sender}: {decision} - {reason}. Có logic không? Có thiếu sót gì?"
                
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
                response_str = str(response_text).strip()
                print(f"[CriticalAgent] ✅ Generated critique for {sender}")
                self.send_message(sender, f"{message_type}_critical_response", {"critical_response": response_str})
            except Exception as e:
                print(f"[CriticalAgent] ❌ Error generating critique: {str(e)}")
                fallback_critique = f"Quyết định {decision} của {sender} cần xem xét thêm các yếu tố và cân nhắc kỹ hơn."
                self.send_message(sender, f"{message_type}_critical_response", {"critical_response": fallback_critique})
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ cho CriticalAgent."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    agent = CriticalAgent()
    decision_payload = {
        "decision": "approve",
        "reason": "Thu nhập ổn định, ngành STEM có triển vọng",
        "risk_level": "low"
    }
    message = {
        "type": "loan_decision",
        "sender": "FinanceAgent",
        "payload": decision_payload
    }
    agent.handle_message(message)
