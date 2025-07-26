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
        self.llm = OpenAI(api_key=api_key, model='gpt-4o-mini')

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
                "Bạn là ACADEMIC EVALUATOR - chuyên gia áp dụng QUY ĐỊNH CHÍNH PHỦ 2025 về học bổng/vay vốn sinh viên.\n"
                "NHIỆM VỤ: Đánh giá CHÍNH XÁC 3 tiêu chí học thuật theo rule-based system.\n\n"
                f"HỒ SƠ SINH VIÊN:\n{profile}\n\n"
                "=== QUY ĐỊNH ĐÁNH GIÁ 2025 (Features 2,3,4) ===\n\n"
                "FEATURE 2 - HỌC LỰC (SPECIAL FEATURE ⚠️):\n"
                "- PASSED: GPA chuẩn hóa >= 0.7 (tương đương 7.0/10)\n"
                "- FAILED: GPA chuẩn hóa < 0.7\n"
                "- Cơ sở: Thông tư 19/2023/TT-BGDĐT\n"
                "- LƯU Ý: Đây là special feature, vi phạm sẽ ảnh hưởng nghiêm trọng\n\n"
                "FEATURE 3 - TRƯỜNG HỌC:\n"
                "- PASSED: University tier 1-3 (công lập/được công nhận)\n"
                "- FAILED: University tier 4-5 (tư thục chưa được công nhận đầy đủ)\n"
                "- Cơ sở: Quyết định 157/2007/QĐ-TTg cập nhật 2024\n\n"
                "FEATURE 4 - NGÀNH HỌC ƯU TIÊN:\n"
                "- PASSED: STEM, Y khoa, Điều dưỡng, Sư phạm, IT, Nông nghiệp công nghệ cao\n"
                "- FAILED: Business, Liberal Arts, các ngành khác\n"
                "- Cơ sở: Quyết định 1036/QĐ-TTg 2021 và 645/QĐ-TTg 2024\n\n"
                "HƯỚNG DẪN ĐÁNH GIÁ:\n"
                "1. Trích xuất thông tin chính xác từ hồ sơ\n"
                "2. Áp dụng ngưỡng cứng theo quy định\n"
                "3. Không được 'linh hoạt' hay 'cảm tính'\n"
                "4. Mỗi feature chỉ có 2 trạng thái: True/False\n\n"
                "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
                "{\n"
                "  \"feature_2_hoc_luc\": true/false,\n"
                "  \"feature_3_truong_hoc\": true/false,\n"
                "  \"feature_4_nganh_uu_tien\": true/false,\n"
                "  \"academic_passed_count\": 0-3,\n"
                "  \"has_special_violation\": true/false,\n"
                "  \"reason\": \"<phân tích từng feature theo quy định>\"\n"
                "}"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_data = json.loads(str(response_text))
                self.send_message(sender, "scholarship_decision", response_data)
            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                self.send_message(sender, "scholarship_decision_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                self.send_message(sender, "scholarship_decision_error", error_payload)
        elif message_type == "repredict_scholarship":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            prompt = (
                "Bạn là ACADEMIC EVALUATOR - TÁI ĐÁNH GIÁ sau phản biện.\n"
                "ÁP DỤNG CHÍNH XÁC QUY ĐỊNH 2025, KHÔNG THAY ĐỔI NGƯỠNG.\n\n"
                f"Lịch sử đánh giá: {memory}\n"
                f"Phản biện: {critical_response}\n\n"
                "NHIỆM VỤ:\n"
                "1. Xem lại việc áp dụng Features 2,3,4\n"
                "2. Sửa lại NẾU có sai sót trong việc áp dụng quy định\n"
                "3. KHÔNG thay đổi nếu đã đúng quy định (dù có phản biện)\n"
                "4. Giải thích rõ tại sao giữ nguyên hoặc thay đổi\n\n"
                "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
                "{\n"
                "  \"feature_2_hoc_luc\": true/false,\n"
                "  \"feature_3_truong_hoc\": true/false,\n"
                "  \"feature_4_nganh_uu_tien\": true/false,\n"
                "  \"academic_passed_count\": 0-3,\n"
                "  \"has_special_violation\": true/false,\n"
                "  \"reason\": \"<giải thích tái đánh giá>\"\n"
                "}"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_data = json.loads(str(response_text))
                self.send_message(sender, "repredict_scholarship", response_data)
            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                # Fallback: conservative evaluation
                self.send_message(sender, "repredict_scholarship", {
                    "feature_2_hoc_luc": False,
                    "feature_3_truong_hoc": False,
                    "feature_4_nganh_uu_tien": False,
                    "academic_passed_count": 0,
                    "has_special_violation": True,
                    "reason": "LLM trả về không hợp lệ - áp dụng đánh giá conservative."
                })
                self.send_message(sender, "repredict_scholarship_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                # Fallback: conservative evaluation
                self.send_message(sender, "repredict_scholarship", {
                    "feature_2_hoc_luc": False,
                    "feature_3_truong_hoc": False,
                    "feature_4_nganh_uu_tien": False,
                    "academic_passed_count": 0,
                    "has_special_violation": True,
                    "reason": f"Lỗi xử lý: {str(e)} - áp dụng đánh giá conservative."
                })
                self.send_message(sender, "repredict_scholarship_error", error_payload)
        else:
            error_payload = {"error": f"Loại tin nhắn '{message_type}' không được hỗ trợ."}
            self.send_message(sender, "unsupported_message", error_payload)

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Tạo agent
    agent = AcademicAgent()
    # Test với rule-based system
    test_profile = "Sinh viên: 21 tuổi, Nữ, Đại học tier 1, ngành STEM, năm 4, GPA chuẩn hóa: 0.85/1.0, tham gia Câu lạc bộ Nghiên cứu Khoa học"
    message = {
        "type": "scholarship_application",
        "sender": "tester",
        "payload": {"profile": test_profile}
    }
    agent.handle_message(message)