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
        Nhận quyết định từ agent khác và phản biện lại lý do.
        """
        message_type = message.get("type")
        sender = message.get("sender")
        payload = message.get("payload", {})

        if message_type in ["loan_decision", "scholarship_decision"]:
            decision = payload.get("decision", "")
            reason = payload.get("reason", "")
            # Prompt phản biện lại quyết định
            prompt = (
                f"Bạn là một agent phản biện. Hãy phân tích quyết định sau của agent '{sender}' và đưa ra phản biện hoặc góc nhìn khác nếu có.\n"
                f"Quyết định: {decision}\nLý do: {reason}\n"
                "Nếu đồng ý thì giải thích vì sao, nếu không thì hãy nêu ra các điểm cần xem xét lại."
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                self.send_message(sender, f"{message_type}_critical_response", {"critical_response": str(response_text)})
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình phản biện: {str(e)}"}
                self.send_message(sender, f"{message_type}_critical_error", error_payload)
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ cho CriticalAgent."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Tạo agent
    agent = CriticalAgent()
    # Message mẫu phản biện quyết định tài chính
    decision_payload = {"decision": "approve", "reason": "Khách hàng có thu nhập cao, không có nợ xấu."}
    message = {
        "type": "loan_decision",
        "sender": "FinanceAgent",
        "payload": decision_payload
    }
    agent.handle_message(message)
