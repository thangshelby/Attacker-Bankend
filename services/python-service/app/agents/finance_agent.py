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
                "Bạn là CHUYÊN GIA RỦI RO TÀI CHÍNH với 15 năm kinh nghiệm ngân hàng và cho vay sinh viên.\n"
                f"HỒ SƠ PHÂN TÍCH RỦI RO:\n{profile}\n\n"
                "FRAMEWORK ĐÁNH GIÁ RỦI RO TÀI CHÍNH:\n"
                "1. KHẢ NĂNG TRẢ NỢ:\n"
                "   - Tỷ lệ thu nhập/khoản vay: [thu nhập tháng] vs [số tiền vay]\n"
                "   - Debt-to-Income ratio hiện tại (nợ/thu nhập)\n"
                "   - Thời hạn vay vs khả năng sinh lời sau tốt nghiệp\n\n"
                "2. ỔN ĐỊNH TÀI CHÍNH:\n"
                "   - Nguồn thu nhập gia đình: ổn định vs biến động\n"
                "   - Nợ hiện tại: số tiền, lãi suất, thời hạn cụ thể\n"
                "   - Tài sản đảm bảo: bảo lãnh vs tài sản thế chấp\n\n"
                "3. RỦI RO VĨ MÔ:\n"
                "   - Triển vọng ngành: tỷ lệ có việc làm sau tốt nghiệp\n"
                "   - Mức lương dự kiến vs khả năng trả nợ\n"
                "   - Yếu tố kinh tế: lạm phát, lãi suất, thất nghiệp\n\n"
                "4. CHÍNH SÁCH CHO VAY:\n"
                "   - Mục đích vay: học phí (ưu tiên) vs sinh hoạt (rủi ro)\n"
                "   - Lịch sử tín dụng cá nhân/gia đình\n"
                "   - Tuổi và giai đoạn học tập\n\n"
                "NGUYÊN TẮC: Tính toán tỷ lệ, phần trăm cụ thể. Đưa ra số liệu thực tế.\n"
                "YÊU CẦU: Phân tích từng rủi ro với con số, không đánh giá mơ hồ.\n\n"
                "FORMAT TRẢ LỜI:\n"
                "QUYẾT ĐỊNH: APPROVE/REJECT\n"
                "LÝ DO: [Phân tích rủi ro chi tiết với tỷ lệ, con số cụ thể từ hồ sơ]"
            )
            
            try:
                response_text = self.llm.complete(prompt, max_tokens=512)
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
                        "reason": reason_text[:300],  # Limit length
                        "raw_response": response_str
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
                        "reason": reason,
                        "raw_response": response_str
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
                    "reason": "Lỗi hệ thống - áp dụng nguyên tắc thận trọng từ chối để tránh rủi ro",
                    "raw_response": response_str if 'response_str' in locals() else "Error: No LLM response"
                }
                self.send_message(sender, "loan_decision", fallback_response)
                print(f"[FinanceAgent] ✅ Sent error fallback: {fallback_response['decision']}")
                

                
        elif message_type == "repredict_loan":
            memory = message.get("payload", {}).get("memory", "")
            critical_response = message.get("payload", {}).get("critical_response", "")
            recommended_decision = message.get("payload", {}).get("recommended_decision", "")
            
            prompt = (
                f"TÁI ĐÁNH GIÁ RỦI RO TÀI CHÍNH - Bạn là chuyên gia ngân hàng sau khi nhận phản biện.\n"
                f"HỒ SƠ KHÁCH HÀNG: {memory}\n"
                f"PHẢN BIỆN NHẬN ĐƯỢC: {critical_response}\n"
                f"KHUYẾN NGHỊ TỪ CHUYÊN GIA PHẢN BIỆN: {recommended_decision}\n\n"
                f"FRAMEWORK TÁI ĐÁNH GIÁ RỦI RO:\n"
                f"1. KIỂM TRA LẠI PHÂN TÍCH:\n"
                f"   - Tính toán nào trong phản biện chính xác?\n"
                f"   - Rủi ro nào tôi đã đánh giá quá cao/thấp?\n"
                f"   - Yếu tố tích cực nào bị bỏ qua?\n\n"
                f"2. TÁI TÍNH TOÁN RỦI RO:\n"
                f"   - Debt-to-Income ratio: có thực sự nguy hiểm?\n"
                f"   - Khả năng trả nợ: nguồn thu có ổn định?\n"
                f"   - Tài sản đảm bảo: mức độ bảo vệ thực tế\n\n"
                f"3. CÂN BẰNG RỦI RO - LỢI ÍCH:\n"
                f"   - Lợi ích kinh tế từ cho vay này\n"
                f"   - Rủi ro so với các khoản vay tương tự\n"
                f"   - Chiến lược ngân hàng (thận trọng vs tăng trưởng)\n\n"
                f"4. QUYẾT ĐỊNH SAU PHẢN BIỆN:\n"
                f"   - Khuyến nghị '{recommended_decision}' có phù hợp?\n"
                f"   - Điều kiện bổ sung nào có thể giảm rủi ro?\n\n"
                f"YÊU CẦU: Quyết định dựa trên phân tích số liệu, không cảm tính.\n\n"
                f"FORMAT:\n"
                f"QUYẾT ĐỊNH: APPROVE/REJECT\n"
                f"LÝ DO: [Phân tích chi tiết tại sao thay đổi/giữ nguyên quyết định]"
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
                    decision = "reject"  # Cautious default
                    reason = "Sau phản biện vẫn giữ thái độ thận trọng về rủi ro tài chính"
                
                response_data = {"decision": decision, "reason": reason, "raw_response": response_str}
                self.send_message(sender, "repredict_loan", response_data)
            except Exception as e:
                print(f"[FinanceAgent] ❌ Error in repredict_loan: {str(e)}")
                fallback_response = {
                    "decision": "reject",
                    "reason": "Sau phản biện vẫn giữ thái độ thận trọng về rủi ro tài chính",
                    "raw_response": response_str if 'response_str' in locals() else "Error: No LLM response"
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