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
        self.llm = OpenAI(api_key=api_key, model='gpt-4o-mini')

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
                "Bạn là FINANCE EVALUATOR - chuyên gia áp dụng QUY ĐỊNH CHÍNH PHỦ 2025 về vay vốn sinh viên.\n"
                "NHIỆM VỤ: Đánh giá CHÍNH XÁC 4 tiêu chí tài chính theo rule-based system.\n\n"
                f"HỒ SƠ TÀI CHÍNH:\n{profile}\n\n"
                "=== QUY ĐỊNH ĐÁNH GIÁ 2025 (Features 1,5,6,7) ===\n\n"
                "FEATURE 1 - THU NHẬP GIA ĐÌNH:\n"
                "- PASSED: <= 10.000.000 VNĐ/tháng\n"
                "- FAILED: > 10.000.000 VNĐ/tháng\n"
                "- Cơ sở: Nghị định 07/2021/NĐ-CP cập nhật 2025\n"
                "- Lý do: Chỉ hỗ trợ hộ gia đình có thu nhập thấp\n\n"
                "FEATURE 5 - NGƯỜI BẢO LÃNH (SPECIAL FEATURE ⚠️):\n"
                "- PASSED: Có bảo lãnh (giả định: có) VÀ family_income > 0\n"
                "- FAILED: Không có bảo lãnh HOẶC family_income = 0\n"
                "- Cơ sở: Mẫu NHCSXH bắt buộc\n"
                "- LƯU Ý: Đây là special feature, vi phạm sẽ ảnh hưởng nghiêm trọng\n\n"
                "FEATURE 6 - TỔNG KHOẢN VAY:\n"
                "- PASSED: <= 60.000.000 VNĐ/toàn khóa HOẶC <= 3.000.000 VNĐ/tháng\n"
                "- FAILED: > 60.000.000 VNĐ VÀ > 3.000.000 VNĐ/tháng\n"
                "- Cơ sở: Quyết định 05/2022/QĐ-TTg cập nhật 2025\n"
                "- Lưu ý: Chỉ cần 1 trong 2 điều kiện là đủ\n\n"
                "FEATURE 7 - CAM KẾT TRẢ NỢ & KHÔNG NỢ XẤU (SPECIAL FEATURE ⚠️):\n"
                "- PASSED: Có cam kết (giả định: có) VÀ existing_debt = false\n"
                "- FAILED: Không có cam kết HOẶC existing_debt = true\n"
                "- Cơ sở: NHCSXH bắt buộc\n"
                "- LƯU Ý: Đây là special feature, vi phạm sẽ ảnh hưởng nghiêm trọng\n\n"
                "HƯỚNG DẪN ĐÁNH GIÁ:\n"
                "1. Trích xuất số liệu chính xác từ hồ sơ\n"
                "2. Áp dụng ngưỡng cứng theo quy định (không làm tròn)\n"
                "3. Đếm chính xác số special violations (Features 5,7)\n"
                "4. Mỗi feature chỉ có 2 trạng thái: True/False\n\n"
                "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
                "{\n"
                "  \"feature_1_thu_nhap\": true/false,\n"
                "  \"feature_5_bao_lanh\": true/false,\n"
                "  \"feature_6_khoan_vay\": true/false,\n"
                "  \"feature_7_cam_ket_no\": true/false,\n"
                "  \"financial_passed_count\": 0-4,\n"
                "  \"special_violations_count\": 0-2,\n"
                "  \"reason\": \"<phân tích từng feature theo quy định>\"\n"
                "}"
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
                response_data = json.loads(str(response_text))
                
                # Gửi tin nhắn phản hồi có cấu trúc
                self.send_message(sender, "loan_decision", response_data)

            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                self.send_message(sender, "loan_decision_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                self.send_message(sender, "loan_decision_error", error_payload)
        elif message_type == "repredict_loan":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            prompt = (
                "Bạn là FINANCE EVALUATOR - TÁI ĐÁNH GIÁ sau phản biện.\n"
                "ÁP DỤNG CHÍNH XÁC QUY ĐỊNH 2025, KHÔNG THAY ĐỔI NGƯỠNG.\n\n"
                f"Lịch sử đánh giá: {memory}\n"
                f"Phản biện: {critical_response}\n\n"
                "NHIỆM VỤ:\n"
                "1. Xem lại việc áp dụng Features 1,5,6,7\n"
                "2. Sửa lại NẾU có sai sót trong việc áp dụng quy định\n"
                "3. KHÔNG thay đổi nếu đã đúng quy định (dù có phản biện)\n"
                "4. Đặc biệt chú ý Features 5,7 (special features)\n"
                "5. Giải thích rõ tại sao giữ nguyên hoặc thay đổi\n\n"
                "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
                "{\n"
                "  \"feature_1_thu_nhap\": true/false,\n"
                "  \"feature_5_bao_lanh\": true/false,\n"
                "  \"feature_6_khoan_vay\": true/false,\n"
                "  \"feature_7_cam_ket_no\": true/false,\n"
                "  \"financial_passed_count\": 0-4,\n"
                "  \"special_violations_count\": 0-2,\n"
                "  \"reason\": \"<giải thích tái đánh giá>\"\n"
                "}"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=256)
                response_data = json.loads(str(response_text))
                self.send_message(sender, "repredict_loan", response_data)
            except json.JSONDecodeError:
                error_payload = {
                    "error": "Phản hồi từ LLM không phải là JSON hợp lệ.",
                    "raw_response": str(response_text)
                }
                # Fallback: conservative evaluation
                self.send_message(sender, "repredict_loan", {
                    "feature_1_thu_nhap": False,
                    "feature_5_bao_lanh": False,
                    "feature_6_khoan_vay": False,
                    "feature_7_cam_ket_no": False,
                    "financial_passed_count": 0,
                    "special_violations_count": 2,
                    "reason": "LLM trả về không hợp lệ - áp dụng đánh giá conservative."
                })
                self.send_message(sender, "repredict_loan_error", error_payload)
            except Exception as e:
                error_payload = {"error": f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"}
                # Fallback: conservative evaluation
                self.send_message(sender, "repredict_loan", {
                    "feature_1_thu_nhap": False,
                    "feature_5_bao_lanh": False,
                    "feature_6_khoan_vay": False,
                    "feature_7_cam_ket_no": False,
                    "financial_passed_count": 0,
                    "special_violations_count": 2,
                    "reason": f"Lỗi xử lý: {str(e)} - áp dụng đánh giá conservative."
                })
                self.send_message(sender, "repredict_loan_error", error_payload)
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
    # Tạo agent
    agent = FinanceAgent()
    # Test với rule-based system
    test_profile = "Thu nhập gia đình: 8,000,000 VND/tháng, có việc làm thêm, không có nợ hiện tại, yêu cầu vay: 45,000,000 VND cho mục đích 'Học phí'"
    message = {
        "type": "loan_application",
        "sender": "tester",
        "payload": {"profile": test_profile}
    }
    agent.handle_message(message)