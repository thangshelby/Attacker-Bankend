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
        self.llm = OpenAI(api_key=api_key, model='gpt-4o-mini')

    def handle_message(self, message: dict):
        """
        Nhận quyết định từ agent khác và phản biện lại việc áp dụng quy định 2025.
        """
        message_type = message.get("type")
        sender = message.get("sender")
        payload = message.get("payload", {})

        if message_type in ["loan_decision", "scholarship_decision"]:
            # Xác định loại agent và focus phản biện
            if sender == "AcademicAgent":
                prompt = self._create_academic_critique_prompt(payload)
            elif sender == "FinanceAgent":
                prompt = self._create_finance_critique_prompt(payload)
            else:
                prompt = self._create_general_critique_prompt(sender, payload)
                
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                self.send_message(sender, f"{message_type}_critical_response", {"critical_response": str(response_text)})
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình phản biện: {str(e)}"}
                self.send_message(sender, f"{message_type}_critical_error", error_payload)
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ cho CriticalAgent."}
            self.send_message(sender, "unsupported_message", error_payload)

    def _create_academic_critique_prompt(self, payload):
        """Tạo prompt phản biện cho Academic Agent - kiểm tra rule compliance"""
        feature_2 = payload.get("feature_2_hoc_luc", "MISSING")
        feature_3 = payload.get("feature_3_truong_hoc", "MISSING")
        feature_4 = payload.get("feature_4_nganh_uu_tien", "MISSING")
        passed_count = payload.get("academic_passed_count", "MISSING")
        special_violation = payload.get("has_special_violation", "MISSING")
        reason = payload.get("reason", "")
        
        return (
            "Bạn là COMPLIANCE AUDITOR - chuyên gia kiểm tra việc áp dụng QUY ĐỊNH 2025.\n"
            "NHIỆM VỤ: Phản biện đánh giá Academic Agent về tính chính xác rule-based.\n\n"
            f"ĐÁNH GIÁ CẦN KIỂM TRA:\n"
            f"- Feature 2 (Học lực): {feature_2}\n"
            f"- Feature 3 (Trường học): {feature_3}\n"
            f"- Feature 4 (Ngành ưu tiên): {feature_4}\n"
            f"- Academic passed count: {passed_count}\n"
            f"- Special violation (Feature 2): {special_violation}\n"
            f"- Lý do: {reason}\n\n"
            "=== KIỂM TRA COMPLIANCE 2025 ===\n\n"
            "1. FEATURE 2 - HỌC LỰC (SPECIAL):\n"
            "   ✓ ĐÚNG: GPA >= 0.7 → True, GPA < 0.7 → False\n"
            "   ✗ SAI: Không áp dụng ngưỡng 0.7 chính xác\n"
            "   ⚠️ CHÚ Ý: Đây là special feature\n\n"
            "2. FEATURE 3 - TRƯỜNG HỌC:\n"
            "   ✓ ĐÚNG: Tier 1-3 → True, Tier 4-5 → False\n"
            "   ✗ SAI: Không phân biệt công lập/tư thục\n\n"
            "3. FEATURE 4 - NGÀNH ƯU TIÊN:\n"
            "   ✓ ĐÚNG: STEM/Y khoa/IT/Sư phạm → True, khác → False\n"
            "   ✗ SAI: Không theo danh mục quy định\n\n"
            "4. LOGIC TÍNH TOÁN:\n"
            "   ✓ academic_passed_count = tổng số True trong 3 features\n"
            "   ✓ special_violation = Feature 2 có False không\n\n"
            "PHẢN BIỆN CẦN TẬP TRUNG:\n"
            "- Có áp dụng đúng ngưỡng theo quy định?\n"
            "- Có nhầm lẫn trong việc tính toán?\n"
            "- Có bỏ sót logic special feature?\n"
            "- Có bias cảm tính thay vì tuân thủ rule?\n\n"
            "ĐƯA RA 2-3 ĐIỂM PHẢN BIỆN CỤ THỂ về compliance và đề xuất sửa lỗi (nếu có)."
        )

    def _create_finance_critique_prompt(self, payload):
        """Tạo prompt phản biện cho Finance Agent - kiểm tra rule compliance"""
        feature_1 = payload.get("feature_1_thu_nhap", "MISSING")
        feature_5 = payload.get("feature_5_bao_lanh", "MISSING")
        feature_6 = payload.get("feature_6_khoan_vay", "MISSING")
        feature_7 = payload.get("feature_7_cam_ket_no", "MISSING")
        passed_count = payload.get("financial_passed_count", "MISSING")
        special_violations = payload.get("special_violations_count", "MISSING")
        reason = payload.get("reason", "")
        
        return (
            "Bạn là COMPLIANCE AUDITOR - chuyên gia kiểm tra việc áp dụng QUY ĐỊNH 2025.\n"
            "NHIỆM VỤ: Phản biện đánh giá Finance Agent về tính chính xác rule-based.\n\n"
            f"ĐÁNH GIÁ CẦN KIỂM TRA:\n"
            f"- Feature 1 (Thu nhập): {feature_1}\n"
            f"- Feature 5 (Bảo lãnh): {feature_5} (SPECIAL)\n"
            f"- Feature 6 (Khoản vay): {feature_6}\n"
            f"- Feature 7 (Cam kết nợ): {feature_7} (SPECIAL)\n"
            f"- Financial passed count: {passed_count}\n"
            f"- Special violations count: {special_violations}\n"
            f"- Lý do: {reason}\n\n"
            "=== KIỂM TRA COMPLIANCE 2025 ===\n\n"
            "1. FEATURE 1 - THU NHẬP:\n"
            "   ✓ ĐÚNG: ≤ 10M → True, > 10M → False\n"
            "   ✗ SAI: Không áp dụng ngưỡng 10M chính xác\n\n"
            "2. FEATURE 5 - BẢO LÃNH (SPECIAL):\n"
            "   ✓ ĐÚNG: Có bảo lãnh VÀ income > 0 → True\n"
            "   ✗ SAI: Không kiểm tra điều kiện income > 0\n"
            "   ⚠️ CHÚ Ý: Đây là special feature\n\n"
            "3. FEATURE 6 - KHOẢN VAY:\n"
            "   ✓ ĐÚNG: ≤ 60M HOẶC ≤ 3M/tháng → True\n"
            "   ✗ SAI: Không hiểu logic OR (chỉ cần 1 điều kiện)\n\n"
            "4. FEATURE 7 - CAM KẾT NỢ (SPECIAL):\n"
            "   ✓ ĐÚNG: Có cam kết VÀ existing_debt = False → True\n"
            "   ✗ SAI: Không kiểm tra existing_debt\n"
            "   ⚠️ CHÚ Ý: Đây là special feature\n\n"
            "5. LOGIC TÍNH TOÁN:\n"
            "   ✓ financial_passed_count = tổng số True\n"
            "   ✓ special_violations_count = số False trong Features 5,7\n\n"
            "PHẢN BIỆN CẦN TẬP TRUNG:\n"
            "- Có áp dụng đúng ngưỡng 10M cho thu nhập?\n"
            "- Có hiểu đúng logic OR cho khoản vay?\n"
            "- Có đếm đúng special violations?\n"
            "- Có nhầm lẫn trong việc đánh giá existing_debt?\n\n"
            "ĐƯA RA 2-3 ĐIỂM PHẢN BIỆN CỤ THỂ về compliance và đề xuất sửa lỗi (nếu có)."
        )

    def _create_general_critique_prompt(self, sender, payload):
        """Tạo prompt phản biện chung cho rule-based system"""
        return (
            f"Bạn là COMPLIANCE AUDITOR kiểm tra việc áp dụng QUY ĐỊNH 2025.\n\n"
            f"ĐÁNH GIÁ TỪ {sender}:\n{payload}\n\n"
            "KIỂM TRA TỔNG QUÁT:\n"
            "- Có tuân thủ format JSON yêu cầu?\n"
            "- Có áp dụng đúng rule-based logic?\n"
            "- Có thiếu thông tin bắt buộc?\n"
            "- Có logic mâu thuẫn?\n\n"
            "Đưa ra phản biện về tính chính xác và compliance."
        )

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Tạo agent
    agent = CriticalAgent()
    # Test với rule-based system
    decision_payload = {
        "feature_1_thu_nhap": True,
        "feature_5_bao_lanh": True,
        "feature_6_khoan_vay": True,
        "feature_7_cam_ket_no": True,
        "financial_passed_count": 4,
        "special_violations_count": 0,
        "reason": "Thu nhập 8M < 10M (pass), có bảo lãnh + income > 0 (pass), vay 45M < 60M (pass), không nợ (pass)"
    }
    message = {
        "type": "loan_decision",
        "sender": "FinanceAgent",
        "payload": decision_payload
    }
    agent.handle_message(message)
