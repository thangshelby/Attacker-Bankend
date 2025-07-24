import json
from .base_agent import BaseAgent
from llama_index.llms.openai import OpenAI
import os


class DecisionAgent(BaseAgent):
    def __init__(self, name="DecisionAgent", coordinator=None):
        super().__init__(name, coordinator)
        self.responses = []  # Lưu các phản hồi từ các agent khác

    def handle_message(self, message: dict):
        """
        Nhận phản hồi từ các agent khác và tổng hợp để đưa ra quyết định cuối cùng.
        """
        message_type = message.get("type")
        sender = message.get("sender")
        payload = message.get("payload", {})

        # Nhận phản hồi từ các agent khác
        if message_type in ["loan_decision", "scholarship_decision", "loan_decision_critical_response", "scholarship_decision_critical_response"]:
            self.responses.append({"from": sender, "type": message_type, "payload": payload})
            print(f"[{self.name}] Đã nhận phản hồi từ {sender}: {payload}")
        elif message_type == "aggregate_and_decide":
            # Khi nhận lệnh tổng hợp, phân tích các phản hồi và đưa ra quyết định cuối cùng
            final_decision = self.aggregate_decisions()
            self.send_message(message.get("sender", "user"), "final_decision", final_decision)
        elif message_type == "aggregate_all":
            # Khi nhận tất cả phản hồi gộp, tổng hợp và ra quyết định
            final_decision = self.aggregate_all(payload)
            self.send_message(message.get("sender", "user"), "final_decision", final_decision)
        else:
            print(f"[{self.name}] Không hỗ trợ message type: {message_type}")
    def aggregate_all(self, merged_payload):
        """
        Tổng hợp tất cả các phản hồi (merged) và đưa ra quyết định cuối cùng bằng LLM (OpenAI).
        """
        dialogue = []
        for key, value in merged_payload.items():
            if value:
                if isinstance(value, dict):
                    decision = value.get("decision")
                    reason = value.get("reason") or value.get("critical_response")
                    dialogue.append(f"{key}: {decision.upper() if decision else ''} - {reason if reason else ''}")
                else:
                    dialogue.append(f"{key}: {value}")
        dialogue_text = "\n".join(dialogue)
        prompt = (
            "Bạn là moderator trung lập. Dưới đây là các ý kiến của các agent về một hồ sơ cho vay/học bổng. "
            "Hãy đọc kỹ, tổng hợp lại và đưa ra quyết định cuối cùng (approve hoặc reject) cùng lý do chi tiết, công tâm, logic.\n"
            f"Các ý kiến:\n{dialogue_text}\n"
            "QUAN TRỌNG: Chỉ trả lời dưới dạng một chuỗi JSON hợp lệ theo format: "
            '{"decision": "approve" hoặc "reject", "reason": "<lý do chi tiết>"}'
        )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[DecisionAgent] OPENAI_API_KEY không được tìm thấy trong môi trường.")
            return {"decision": "reject", "reason": "Không có API key cho LLM."}
        llm = OpenAI(api_key=api_key, model='gpt-4.1-nano')
        try:
            response_text = llm.complete(prompt, max_tokens=256)
            response_data = json.loads(str(response_text))
            print(f"[{self.name}] QUYẾT ĐỊNH CUỐI CÙNG (LLM): {response_data}")
            return response_data
        except Exception as e:
            print(f"[{self.name}] Lỗi khi tổng hợp quyết định bằng LLM: {e}")
            return {"decision": "reject", "reason": f"Lỗi tổng hợp quyết định bằng LLM: {e}"}

    def aggregate_decisions(self):
        """
        Tổng hợp các phản hồi và đưa ra quyết định cuối cùng bằng LLM (OpenAI).
        """

        # Gom hội thoại các agent
        dialogue = []
        for resp in self.responses:
            who = resp["from"]
            payload = resp["payload"]
            if isinstance(payload, dict):
                decision = payload.get("decision")
                reason = payload.get("reason") or payload.get("critical_response")
                if decision:
                    dialogue.append(f"{who}: {decision.upper()} - {reason if reason else ''}")
                elif reason:
                    dialogue.append(f"{who}: {reason}")
            elif isinstance(payload, str):
                dialogue.append(f"{who}: {payload}")

        dialogue_text = "\n".join(dialogue)
        prompt = (
            "Bạn là moderator trung lập. Dưới đây là các ý kiến của các agent về một hồ sơ cho vay/học bổng. "
            "Hãy đọc kỹ, tổng hợp lại và đưa ra quyết định cuối cùng (approve hoặc reject) cùng lý do chi tiết, công tâm, logic.\n"
            f"Các ý kiến:\n{dialogue_text}\n"
            "QUAN TRỌNG: Chỉ trả lời dưới dạng một chuỗi JSON hợp lệ theo format: "
            '{"decision": "approve" hoặc "reject", "reason": "<lý do chi tiết>"}'
        )
        # Lấy API key từ biến môi trường
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[DecisionAgent] OPENAI_API_KEY không được tìm thấy trong môi trường.")
            return {"decision": "reject", "reason": "Không có API key cho LLM."}
        llm = OpenAI(api_key=api_key, model='gpt-4.1-nano')
        try:
            response_text = llm.complete(prompt)
            response_data = json.loads(str(response_text))
            print(f"[{self.name}] QUYẾT ĐỊNH CUỐI CÙNG (LLM): {response_data}")
            return response_data
        except Exception as e:
            print(f"[{self.name}] Lỗi khi tổng hợp quyết định bằng LLM: {e}")
            return {"decision": "reject", "reason": f"Lỗi tổng hợp quyết định bằng LLM: {e}"}

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Tạo agent
    agent = DecisionAgent()
    # Test nhận các phản hồi mẫu
    agent.handle_message({
        "type": "loan_decision",
        "sender": "FinanceAgent",
        "payload": {"decision": "approve", "reason": "Khách hàng có thu nhập cao."}
    })
    agent.handle_message({
        "type": "loan_decision_critical_response",
        "sender": "CriticalAgent",
        "payload": {"critical_response": "Cần xem xét thêm lịch sử tín dụng."}
    })
    # Tổng hợp và đưa ra quyết định cuối cùng
    agent.handle_message({
        "type": "aggregate_and_decide",
        "sender": "tester"
    })
