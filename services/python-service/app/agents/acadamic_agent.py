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
                "Bạn là CHUYÊN GIA HỌC THUẬT với 15 năm kinh nghiệm đánh giá tiềm năng sinh viên.\n"
                f"HỒ SƠ PHÂN TÍCH:\n{profile}\n\n"
                "FRAMEWORK ĐÁNH GIÁ TIỀM NĂNG HỌC THUẬT:\n"
                "1. NĂNG LỰC HỌC TẬP:\n"
                "   - GPA hiện tại vs xu hướng cải thiện\n"
                "   - Độ khó ngành học (STEM/Y khoa = thách thức cao)\n"
                "   - Ranking trường (tier 1/2/3 vs chất lượng giảng dạy)\n\n"
                "2. ĐỘNG LỰC & THÁI ĐỘ:\n"
                "   - Hoạt động ngoại khóa chuyên môn (CLB IT, nghiên cứu)\n"
                "   - Việc làm thêm (thể hiện trách nhiệm vs ảnh hưởng học tập)\n"
                "   - Năm học hiện tại (thời gian còn lại để cải thiện)\n\n"
                "3. BỐI CẢNH XÃ HỘI:\n"
                "   - Thu nhập gia đình (áp lực tài chính vs hỗ trợ học tập)\n"
                "   - Bảo lãnh (cam kết gia đình vs độc lập tài chính)\n"
                "   - Khu vực (cơ hội việc làm sau tốt nghiệp)\n\n"
                "NGUYÊN TẮC: Đưa ra con số, dữ liệu cụ thể. Tránh nói chung chung.\n"
                "YÊU CẦU: Phân tích từng yếu tố với dữ liệu thực tế từ hồ sơ.\n\n"
                "FORMAT TRẢ LỜI:\n"
                "QUYẾT ĐỊNH: APPROVE/REJECT\n"
                "LÝ DO: [Phân tích cụ thể từng yếu tố với số liệu, không chung chung]"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
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
                        "reason": reason_text[:300],  # Limit length
                        "raw_response": response_str
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
                        "reason": reason,
                        "raw_response": response_str
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
                    "reason": "Lỗi hệ thống - vẫn tin tưởng vào tiềm năng phát triển của sinh viên",
                    "raw_response": response_str if 'response_str' in locals() else "Error: No LLM response"
                }
                self.send_message(sender, "scholarship_decision", fallback_response)
                print(f"[AcademicAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                

                
        elif message_type == "repredict_scholarship":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            recommended_decision = message.get("payload", {}).get("recommended_decision", "")
            
            prompt = (
                f"TÁI ĐÁNH GIÁ CHUYÊN MÔN - Bạn là chuyên gia học thuật sau khi nhận phản biện.\n"
                f"HỒ SƠ GỐC: {memory}\n"
                f"PHẢN BIỆN NHẬN ĐƯỢC: {critical_response}\n"
                f"KHUYẾN NGHỊ TỪ CHUYÊN GIA PHẢN BIỆN: {recommended_decision}\n\n"
                f"FRAMEWORK TÁI ĐÁNH GIÁ:\n"
                f"1. PHÂN TÍCH PHẢN BIỆN:\n"
                f"   - Điểm nào trong phản biện có căn cứ?\n"
                f"   - Yếu tố nào tôi đã bỏ qua trong đánh giá ban đầu?\n"
                f"   - Dữ liệu nào cần xem xét lại?\n\n"
                f"2. CÂN NHẮC LẠI CÁC YẾU TỐ:\n"
                f"   - GPA: tác động thực tế vs tiềm năng cải thiện\n"
                f"   - Ngành học: độ khó vs triển vọng nghề nghiệp\n"
                f"   - Hoàn cảnh: hỗ trợ gia đình vs áp lực tài chính\n\n"
                f"3. QUYẾT ĐỊNH SAU PHẢN BIỆN:\n"
                f"   - Giữ nguyên quan điểm với lý do mạnh mẽ hơn\n"
                f"   - Hoặc thay đổi dựa trên bằng chứng mới\n"
                f"   - Xem xét khuyến nghị '{recommended_decision}' có hợp lý?\n\n"
                f"YÊU CẦU: Đưa ra quyết định có căn cứ sau khi phân tích phản biện.\n\n"
                f"FORMAT:\n"
                f"QUYẾT ĐỊNH: APPROVE/REJECT\n"
                f"LÝ DO: [Giải thích cụ thể tại sao giữ nguyên/thay đổi sau phản biện]"
            )
            try:
                response_text = self.llm.complete(prompt, max_tokens=400)
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
                
                response_data = {"decision": decision, "reason": reason, "raw_response": response_str}
                self.send_message(sender, "repredict_scholarship", response_data)
            except Exception as e:
                print(f"[AcademicAgent] ❌ Repredict error: {e}")
                fallback_response = {
                    "decision": "approve",
                    "reason": "Sau phản biện vẫn tin vào tiềm năng phát triển của sinh viên",
                    "raw_response": response_str if 'response_str' in locals() else "Error: No LLM response"
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