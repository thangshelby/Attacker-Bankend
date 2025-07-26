import json
from .base_agent import BaseAgent
from llama_index.llms.openai import OpenAI
import os
import re


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
            
    def extract_rule_features_from_profile(self, profile_text):
        """
        Trích xuất rule-based features từ profile text.
        TRICK: Convert subjective data thành objective rule compliance!
        """
        if not profile_text:
            return self._get_default_features()
            
        # Extract GPA với nhiều pattern khác nhau
        gpa_patterns = [
            r'GPA[:\s]*chuẩn[:\s]*hóa[:\s]*([0-9]+\.?[0-9]*)',  # "GPA chuẩn hóa: 0.72"
            r'GPA[:\s]*([0-9]+\.?[0-9]*)',                     # "GPA: 7.25" hoặc "GPA 0.717"
            r'điểm[:\s]*trung[:\s]*bình[:\s]*([0-9]+\.?[0-9]*)', # "điểm trung bình"
        ]
        
        gpa_raw = 5.0  # Default 5.0/10
        gpa_found_pattern = None
        
        for i, pattern in enumerate(gpa_patterns):
            gpa_match = re.search(pattern, profile_text, re.IGNORECASE)
            if gpa_match:
                gpa_raw = float(gpa_match.group(1))
                gpa_found_pattern = f"pattern_{i+1}"
                break
        
        # Convert thang 10 → thang 1
        if gpa_raw > 1:  # Thang 10 (like 7.25, 6.42, 8.5)
            gpa_normalized = gpa_raw / 10.0
        else:  # Đã là thang 1 (like 0.725, 0.85)
            gpa_normalized = gpa_raw
            

            
        # Extract University Tier
        tier_match = re.search(r'tier[:\s]*([1-5])', profile_text, re.IGNORECASE)
        university_tier = int(tier_match.group(1)) if tier_match else 3
        
        # Extract Major
        major_keywords = ['STEM', 'Y khoa', 'IT', 'Sư phạm', 'Computer', 'Engineering', 'Medicine', 'Science']
        major_priority = any(keyword.lower() in profile_text.lower() for keyword in major_keywords)
        
        # Extract Income (in VND)
        income_patterns = [
            r'thu nhập[:\s]*([0-9,\.]+)\s*(?:triệu|M|VND)',
            r'([0-9,\.]+)\s*(?:triệu|M)\s*VND',
            r'([0-9,\.]+)\s*VND'
        ]
        family_income = 15000000  # Default
        for pattern in income_patterns:
            income_match = re.search(pattern, profile_text, re.IGNORECASE)
            if income_match:
                income_str = income_match.group(1).replace(',', '').replace('.', '')
                income_val = float(income_str)
                if income_val < 1000:  # Likely in millions
                    income_val *= 1000000
                family_income = income_val
                break
                
        # Extract Debt Status - cần phân biệt "Đang có nợ" vs "Không có nợ"
        debt_positive_keywords = ['đang có nợ', 'hiện có nợ', 'có nợ hiện tại']
        debt_negative_keywords = ['không có nợ', 'không có nợ nần', 'chưa có nợ']
        
        profile_lower = profile_text.lower()
        has_positive_debt = any(keyword in profile_lower for keyword in debt_positive_keywords)
        has_negative_debt = any(keyword in profile_lower for keyword in debt_negative_keywords)
        
        if has_positive_debt:
            has_debt = True
        elif has_negative_debt:
            has_debt = False
        else:
            # Fallback: check for general debt keywords
            has_debt = any(keyword in profile_lower for keyword in ['debt', 'nợ']) and not any(neg in profile_lower for neg in ['không', 'chưa'])
        
        # Extract Loan Amount
        loan_patterns = [
            r'vay[:\s]*([0-9,\.]+)\s*(?:triệu|M|VND)',
            r'([0-9,\.]+)\s*(?:triệu|M)\s*VND.*(?:vay|loan)'
        ]
        loan_amount = 50000000  # Default
        for pattern in loan_patterns:
            loan_match = re.search(pattern, profile_text, re.IGNORECASE)
            if loan_match:
                loan_str = loan_match.group(1).replace(',', '').replace('.', '')
                loan_val = float(loan_str)
                if loan_val < 1000:  # Likely in millions
                    loan_val *= 1000000
                loan_amount = loan_val
                break
        
        # Apply RULE-BASED LOGIC (QUY ĐỊNH 2025)
        feature_1_thu_nhap = family_income <= 10000000
        feature_2_hoc_luc = gpa_normalized >= 0.7  # SPECIAL
        feature_3_truong_hoc = university_tier <= 3
        feature_4_nganh_uu_tien = major_priority
        feature_5_bao_lanh = family_income > 0  # SPECIAL (assume có bảo lãnh)
        feature_6_khoan_vay = loan_amount <= 60000000 or loan_amount <= 3000000 * 12  # per year
        feature_7_no_existing_debt = not has_debt  # SPECIAL - existing_debt=false (không có nợ) = PASS
        
        return {
            'feature_1_thu_nhap': feature_1_thu_nhap,
            'feature_2_hoc_luc': feature_2_hoc_luc,
            'feature_3_truong_hoc': feature_3_truong_hoc,
            'feature_4_nganh_uu_tien': feature_4_nganh_uu_tien,
            'feature_5_bao_lanh': feature_5_bao_lanh,
            'feature_6_khoan_vay': feature_6_khoan_vay,
            'feature_7_no_existing_debt': feature_7_no_existing_debt
        }
    
    def _get_default_features(self):
        """Default conservative features when profile parsing fails"""
        return {
            'feature_1_thu_nhap': False,
            'feature_2_hoc_luc': False,
            'feature_3_truong_hoc': False,
            'feature_4_nganh_uu_tien': False,
            'feature_5_bao_lanh': False,
            'feature_6_khoan_vay': False,
            'feature_7_no_existing_debt': False  # Assume có nợ (conservative)
        }

    def aggregate_all(self, merged_payload):
        """
        HYBRID APPROACH: Subjective debate → Objective rule-based decision
        """
        # SAFETY CHECK
        if not merged_payload or not isinstance(merged_payload, dict):
            return {
                "decision": "reject",
                "reason": "Lỗi hệ thống: Không nhận được dữ liệu từ agents",
                "rule_based_system": True,
                "error": "invalid_payload"
            }
        
        print(f"[DecisionAgent] HYBRID DECISION: Converting subjective → objective rules")
        
        # Get original profile for accurate rule-based feature extraction
        original_profile = merged_payload.get("original_profile", "")
        academic_data = merged_payload.get("scholarship_decision") or {}
        finance_data = merged_payload.get("loan_decision") or {}
        
        # ALWAYS use original profile for rule extraction (ignore agent reasoning)
        if original_profile:
            profile_for_extraction = original_profile
            print(f"[DecisionAgent] ✅ Using ORIGINAL profile for rule extraction")
        else:
            # EMERGENCY: original_profile missing - reject by default
            print(f"[DecisionAgent] ❌ MISSING original_profile - using conservative defaults")
            return {
                "decision": "reject",
                "reason": "Lỗi hệ thống: Thiếu thông tin profile gốc để áp dụng quy định",
                "rule_based_system": True,
                "error": "missing_original_profile"
            }
        
        # CONVERT SUBJECTIVE TO OBJECTIVE RULES
        features = self.extract_rule_features_from_profile(profile_for_extraction)
        
        # ÁP DỤNG CHÍNH XÁC QUY ĐỊNH 2025
        all_features = [
            features['feature_1_thu_nhap'],    # Feature 1
            features['feature_2_hoc_luc'],     # Feature 2 (SPECIAL)
            features['feature_3_truong_hoc'],  # Feature 3
            features['feature_4_nganh_uu_tien'], # Feature 4
            features['feature_5_bao_lanh'],    # Feature 5 (SPECIAL)
            features['feature_6_khoan_vay'],   # Feature 6
            features['feature_7_no_existing_debt'] # Feature 7 (SPECIAL) - Không có nợ
        ]
        
        # Tính passed_count = số feature passed (True)
        passed_count = sum(all_features)
        
        # Tính special_violations = số failed (False) trong [2,5,7]
        special_features = [features['feature_2_hoc_luc'], features['feature_5_bao_lanh'], features['feature_7_no_existing_debt']]
        special_violations = sum(1 for f in special_features if not f)
        
        # LOGIC QUYẾT ĐỊNH THEO QUY ĐỊNH 2025
        if special_violations > 1:
            decision = "reject"
            reason = f"Vi phạm {special_violations} special features (F2,F5,F7) - TỰ ĐỘNG TỪ CHỐI theo quy định."
        elif special_violations == 1:
            if passed_count >= 6:
                decision = "approve"
                reason = f"Vi phạm 1 special feature nhưng passed_count = {passed_count} >= 6 - CHẤP NHẬN có điều kiện."
            else:
                decision = "reject"
                reason = f"Vi phạm 1 special feature và passed_count = {passed_count} < 6 - TỪ CHỐI."
        else:  # special_violations == 0
            if passed_count >= 6:
                decision = "approve"
                reason = f"Không vi phạm special features và passed_count = {passed_count} >= 6 - CHẤP NHẬN."
            else:
                decision = "reject"
                reason = f"Không vi phạm special features nhưng passed_count = {passed_count} < 6 - TỪ CHỐI."
        
        # Thêm thông tin chi tiết
        detailed_analysis = {
            "features_analysis": features,
            "rule_calculation": {
                "total_passed_count": passed_count,
                "special_violations_count": special_violations,
                "special_features_status": {
                    "feature_2": features['feature_2_hoc_luc'],
                    "feature_5": features['feature_5_bao_lanh'],
                    "feature_7": features['feature_7_no_existing_debt']
                }
            },
            "regulation_compliance": "Nghị định 07/2021/NĐ-CP, Quyết định 05/2022/QĐ-TTg, Thông tư 19/2023/TT-BGDĐT (cập nhật 2025)",
            "subjective_inputs": {
                "academic_decision": academic_data.get("decision") if academic_data else None,
                "finance_decision": finance_data.get("decision") if finance_data else None,
                "academic_reason": academic_data.get("reason") if academic_data else None,
                "finance_reason": finance_data.get("reason") if finance_data else None
            }
        }
        
        result = {
            "decision": decision,
            "reason": reason,
            "detailed_analysis": detailed_analysis,
            "rule_based_system": True,
            "hybrid_approach": "subjective_debate_to_objective_rules"
        }
        
        print(f"[{self.name}] HYBRID QUYẾT ĐỊNH: {result}")
        return result

    def aggregate_decisions(self):
        """
        Legacy method - giữ lại để tương thích với workflow cũ
        """
        # Gom hội thoại các agent
        dialogue = []
        for resp in self.responses:
            who = resp["from"]
            payload = resp["payload"]
            if isinstance(payload, dict):
                decision = payload.get("decision", "")
                reason = payload.get("reason", "")
                risk_level = payload.get("risk_level", "")
                
                line = f"{who}: {decision.upper()}"
                if risk_level:
                    line += f" (risk: {risk_level})"
                line += f" - {reason}"
                dialogue.append(line)
            elif isinstance(payload, str):
                dialogue.append(f"{who}: {payload}")

        dialogue_text = "\n".join(dialogue)
        prompt = (
            "Bạn là DECISION MAKER áp dụng QUY ĐỊNH 2025 về vay vốn sinh viên.\n"
            "Dựa trên phân tích subjective từ các agents, đưa ra quyết định cuối cùng:\n\n"
            f"Phân tích từ agents:\n{dialogue_text}\n\n"
            "HƯỚNG DẪN QUYẾT ĐỊNH:\n"
            "- Tổng hợp ý kiến subjective\n"
            "- Cân bằng academic potential vs financial risk\n"
            "- Xem xét critiques có hợp lý không\n"
            "- Quyết định công bằng và có lý\n\n"
            "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
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
            print(f"[{self.name}] QUYẾT ĐỊNH CUỐI CÙNG (Legacy): {response_data}")
            return response_data
        except Exception as e:
            print(f"[{self.name}] Lỗi khi tổng hợp quyết định: {e}")
            return {"decision": "reject", "reason": f"Lỗi tổng hợp quyết định: {e}"}

    def send_message(self, recipient, message_type, payload):
        if self.coordinator:
            self.coordinator.route_message(self.name, recipient, message_type, payload)
        else:
            print(f"[{self.name}] (Test) Gửi tới {recipient} | type: {message_type} | payload: {payload}")

if __name__ == "__main__":
    # Test hybrid approach
    agent = DecisionAgent()
    test_payload = {
        "scholarship_decision": {
            "decision": "approve",
            "reason": "GPA 0.85 xuất sắc, STEM tier 1, có CLB"
        },
        "loan_decision": {
            "decision": "approve", 
            "reason": "Thu nhập 8M VND/tháng, không nợ, vay 45M học phí",
            "risk_level": "low"
        }
    }
    
    agent.handle_message({
        "type": "aggregate_all",
        "sender": "tester",
        "payload": test_payload
    })
