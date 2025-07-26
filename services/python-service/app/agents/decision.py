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
        Tổng hợp tất cả các phản hồi và áp dụng CHÍNH XÁC QUY ĐỊNH 2025.
        """
        # Extract feature results từ Academic Agent
        academic_data = merged_payload.get("scholarship_decision", {})
        feature_2_hoc_luc = academic_data.get("feature_2_hoc_luc", False)
        feature_3_truong_hoc = academic_data.get("feature_3_truong_hoc", False)
        feature_4_nganh_uu_tien = academic_data.get("feature_4_nganh_uu_tien", False)
        
        # Extract feature results từ Finance Agent
        finance_data = merged_payload.get("loan_decision", {})
        feature_1_thu_nhap = finance_data.get("feature_1_thu_nhap", False)
        feature_5_bao_lanh = finance_data.get("feature_5_bao_lanh", False)
        feature_6_khoan_vay = finance_data.get("feature_6_khoan_vay", False)
        feature_7_cam_ket_no = finance_data.get("feature_7_cam_ket_no", False)
        
        # Check reanalysis results (ưu tiên nếu có)
        academic_reanalysis = merged_payload.get("repredict_scholarship", {})
        if academic_reanalysis:
            feature_2_hoc_luc = academic_reanalysis.get("feature_2_hoc_luc", feature_2_hoc_luc)
            feature_3_truong_hoc = academic_reanalysis.get("feature_3_truong_hoc", feature_3_truong_hoc)
            feature_4_nganh_uu_tien = academic_reanalysis.get("feature_4_nganh_uu_tien", feature_4_nganh_uu_tien)
        
        finance_reanalysis = merged_payload.get("repredict_loan", {})
        if finance_reanalysis:
            feature_1_thu_nhap = finance_reanalysis.get("feature_1_thu_nhap", feature_1_thu_nhap)
            feature_5_bao_lanh = finance_reanalysis.get("feature_5_bao_lanh", feature_5_bao_lanh)
            feature_6_khoan_vay = finance_reanalysis.get("feature_6_khoan_vay", feature_6_khoan_vay)
            feature_7_cam_ket_no = finance_reanalysis.get("feature_7_cam_ket_no", feature_7_cam_ket_no)
        
        # ÁP DỤNG CHÍNH XÁC QUY ĐỊNH 2025
        all_features = [
            feature_1_thu_nhap,    # Feature 1
            feature_2_hoc_luc,     # Feature 2 (SPECIAL)
            feature_3_truong_hoc,  # Feature 3
            feature_4_nganh_uu_tien, # Feature 4
            feature_5_bao_lanh,    # Feature 5 (SPECIAL)
            feature_6_khoan_vay,   # Feature 6
            feature_7_cam_ket_no   # Feature 7 (SPECIAL)
        ]
        
        # Tính passed_count = số feature passed (True)
        passed_count = sum(all_features)
        
        # Tính special_violations = số failed (False) trong [2,5,7]
        special_features = [feature_2_hoc_luc, feature_5_bao_lanh, feature_7_cam_ket_no]
        special_violations = sum(1 for f in special_features if not f)
        
        # LOGIC QUYẾT ĐỊNH THEO QUY ĐỊNH 2025
        if special_violations > 1:
            decision = "reject"
            reason = f"Vi phạm {special_violations} special features (Features 2,5,7) - TỰ ĐỘNG TỪ CHỐI theo quy định."
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
            "features_analysis": {
                "feature_1_thu_nhap": feature_1_thu_nhap,
                "feature_2_hoc_luc": feature_2_hoc_luc,
                "feature_3_truong_hoc": feature_3_truong_hoc,
                "feature_4_nganh_uu_tien": feature_4_nganh_uu_tien,
                "feature_5_bao_lanh": feature_5_bao_lanh,
                "feature_6_khoan_vay": feature_6_khoan_vay,
                "feature_7_cam_ket_no": feature_7_cam_ket_no
            },
            "rule_calculation": {
                "total_passed_count": passed_count,
                "special_violations_count": special_violations,
                "special_features_status": {
                    "feature_2": feature_2_hoc_luc,
                    "feature_5": feature_5_bao_lanh,
                    "feature_7": feature_7_cam_ket_no
                }
            },
            "regulation_compliance": "Nghị định 07/2021/NĐ-CP, Quyết định 05/2022/QĐ-TTg, Thông tư 19/2023/TT-BGDĐT (cập nhật 2025)"
        }
        
        result = {
            "decision": decision,
            "reason": reason,
            "detailed_analysis": detailed_analysis,
            "rule_based_system": True
        }
        
        print(f"[{self.name}] QUYẾT ĐỊNH CUỐI CÙNG (Rule-Based 2025): {result}")
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
                # Try to extract rule-based info if available
                features_info = []
                for key, value in payload.items():
                    if key.startswith("feature_"):
                        features_info.append(f"{key}: {value}")
                
                reason = payload.get("reason", "")
                if features_info:
                    line = f"{who}: {', '.join(features_info)} - {reason}"
                else:
                    line = f"{who}: {reason}"
                dialogue.append(line)
            elif isinstance(payload, str):
                dialogue.append(f"{who}: {payload}")

        dialogue_text = "\n".join(dialogue)
        prompt = (
            "Bạn là DECISION MAKER áp dụng QUY ĐỊNH 2025 về vay vốn sinh viên.\n"
            "Dựa trên phân tích rule-based từ các agents, đưa ra quyết định cuối cùng:\n\n"
            f"Phân tích từ agents:\n{dialogue_text}\n\n"
            "HƯỚNG DẪN QUYẾT ĐỊNH:\n"
            "- Ưu tiên rule-based evaluation nếu có\n"
            "- Áp dụng ngưỡng cứng theo quy định 2025\n"
            "- Xem xét special features (2,5,7) nghiêm trọng\n"
            "- Quyết định dựa trên passed_count và special_violations\n\n"
            "QUAN TRỌNG: Chỉ trả lời JSON hợp lệ:\n"
            '{"decision": "approve" hoặc "reject", "reason": "<lý do chi tiết theo quy định>"}'
        )
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[DecisionAgent] OPENAI_API_KEY không được tìm thấy trong môi trường.")
            return {"decision": "reject", "reason": "Không có API key cho LLM."}
            
        llm = OpenAI(api_key=api_key, model='gpt-4o-mini')
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
    # Tạo agent
    agent = DecisionAgent()
    # Test với rule-based system
    test_payload = {
        "scholarship_decision": {
            "feature_2_hoc_luc": True,
            "feature_3_truong_hoc": True,
            "feature_4_nganh_uu_tien": True,
            "academic_passed_count": 3,
            "has_special_violation": False
        },
        "loan_decision": {
            "feature_1_thu_nhap": True,
            "feature_5_bao_lanh": True,
            "feature_6_khoan_vay": True,
            "feature_7_cam_ket_no": False,  # Vi phạm 1 special
            "financial_passed_count": 3,
            "special_violations_count": 1
        }
    }
    
    agent.handle_message({
        "type": "aggregate_all",
        "sender": "tester",
        "payload": test_payload
    })
