from app.core.memory import SessionMemory
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.acadamic_agent import AcademicAgent  
from app.agents.critical_agent import CriticalAgent
from app.agents.decision_agent import DecisionAgent
from app.core.decision_workflow import get_persona_prompt
import time  # Để thêm delay nhỏ nếu cần polling

def debate_to_decide_workflow(profile, return_log: bool = False):
    # Khởi tạo bộ nhớ phiên làm việc
    session_memory = SessionMemory()

    # Khởi tạo coordinator và các agent
    coordinator = CoordinatorAgent()
    academic = AcademicAgent(name="AcademicAgent")
    finance = FinanceAgent(name="FinanceAgent")
    critic = CriticalAgent(name="CriticalAgent")
    decision = DecisionAgent(name="DecisionAgent")

    # Đăng ký agent
    for agent in [academic, finance, critic, decision]:
        coordinator.register_agent(agent)

    # Monkey patch: Ghi lại mọi message vào session_memory khi route_message
    orig_route_message = coordinator.route_message
    def route_message_with_memory(sender, recipient, message_type, payload):
        # Ghi lại tất cả message, không chỉ của coordinator
        session_memory.add_message(sender, recipient, message_type, payload)
        return orig_route_message(sender, recipient, message_type, payload)
    coordinator.route_message = route_message_with_memory

    # Vòng 1: Initial Arguments - SUBJECTIVE DEBATE
    print("\n=== Vòng 1: Subjective Arguments ===")
    academic_prompt = get_persona_prompt("optimist", profile)
    finance_prompt = get_persona_prompt("realist", profile)
    coordinator.route_message("coordinator", "AcademicAgent", "scholarship_application", {"profile": academic_prompt})
    coordinator.route_message("coordinator", "FinanceAgent", "loan_application", {"profile": finance_prompt})

    # Đợi một chút để agents xử lý
    time.sleep(1)

    # Vòng 2: Critique & Rebuttal - SUBJECTIVE CRITIQUE
    print("\n=== Vòng 2: Critique & Rebuttal ===")

    # Thu thập decisions từ Vòng 1
    academic_decision = None
    finance_decision = None

    for entry in list(coordinator.message_log):
        msg_type = entry["message"].get("type")
        # Đúng: Tìm message TỪ agents response lại
        if entry["from"] == "AcademicAgent" and msg_type == "scholarship_decision":
            academic_decision = entry["message"]["payload"]
        elif entry["from"] == "FinanceAgent" and msg_type == "loan_decision":
            finance_decision = entry["message"]["payload"]

    # Gửi tuần tự từng decision cho CriticalAgent và nhận phản biện riêng
    critical_responses = {"AcademicAgent": None, "FinanceAgent": None}
    if academic_decision:
        critic_prompt = get_persona_prompt("critic", profile=None, argument=str(academic_decision))
        coordinator.route_message("coordinator", "CriticalAgent", "scholarship_decision", {"argument": critic_prompt, "decision": academic_decision})
    if finance_decision:
        critic_prompt = get_persona_prompt("critic", profile=None, argument=str(finance_decision))
        coordinator.route_message("coordinator", "CriticalAgent", "loan_decision", {"argument": critic_prompt, "decision": finance_decision})
    if not academic_decision or not finance_decision:
        print("⚠️ Warning: Không tìm thấy đủ decisions từ cả 2 agents")
        print(f"Academic decision: {'✅' if academic_decision else '❌'}")
        print(f"Finance decision: {'✅' if finance_decision else '❌'}")

    # Đợi critical responses
    time.sleep(5)

    # Thu thập phản biện cho từng agent
    for entry in list(coordinator.message_log):
        msg_type = entry["message"].get("type")
        if entry["from"] == "CriticalAgent" and msg_type == "scholarship_decision_critical_response":
            critical_responses["AcademicAgent"] = entry["message"]["payload"]
        elif entry["from"] == "CriticalAgent" and msg_type == "loan_decision_critical_response":
            critical_responses["FinanceAgent"] = entry["message"]["payload"]

    # Cơ chế repredict: AcademicAgent và FinanceAgent dự đoán lại dựa trên phản biện (chỉ 1 lần)
    def simplify_memory(memory_data):
        result = []
        for item in memory_data:
            if hasattr(item, 'dict'):
                result.append(item.dict())
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(str(item))
        return result

    repredict_done = {"AcademicAgent": False, "FinanceAgent": False}
    memory_data = simplify_memory(session_memory.get_conversation())
    if critical_responses["AcademicAgent"]:
        coordinator.route_message("coordinator", "AcademicAgent", "repredict_scholarship", {
            "memory": memory_data,
            "critical_response": critical_responses["AcademicAgent"]
        })
        repredict_done["AcademicAgent"] = True
    if critical_responses["FinanceAgent"]:
        coordinator.route_message("coordinator", "FinanceAgent", "repredict_loan", {
            "memory": memory_data,
            "critical_response": critical_responses["FinanceAgent"]
        })
        repredict_done["FinanceAgent"] = True

    # Đợi repredict hoàn thành
    time.sleep(5)

    # Vòng 3: HYBRID DECISION - Subjective → Objective
    print("\n=== Vòng 3: Hybrid Decision (Subjective → Rule-Based) ===")
    
    # SAFETY: Đảm bảo luôn gửi dict thay vì None để tránh crash
    merged_payload = {
        "scholarship_decision": academic_decision if academic_decision else {},
        "loan_decision": finance_decision if finance_decision else {},
        "scholarship_decision_critical_response": critical_responses["AcademicAgent"] if critical_responses["AcademicAgent"] else {},
        "loan_decision_critical_response": critical_responses["FinanceAgent"] if critical_responses["FinanceAgent"] else {},
        "repredict_scholarship": {},
        "repredict_loan": {},
        "original_profile": profile  # ⭐ PASS PROFILE FOR RULE EXTRACTION ⭐
    }
    # Thu thập repredict từ message_log với safety check
    for entry in list(coordinator.message_log):
        msg_type = entry["message"].get("type")
        if entry["from"] == "AcademicAgent" and msg_type == "repredict_scholarship":
            payload = entry["message"]["payload"]
            merged_payload["repredict_scholarship"] = payload if payload else {}
        elif entry["from"] == "FinanceAgent" and msg_type == "repredict_loan":
            payload = entry["message"]["payload"]
            merged_payload["repredict_loan"] = payload if payload else {}

    print(f"[Coordinator] HYBRID: Subjective debate → Objective rule-based decision")
    print(f"[Debug] Original profile available: {bool(profile)}")
    print(f"[Debug] Academic data valid: {bool(merged_payload['scholarship_decision'])}")
    print(f"[Debug] Finance data valid: {bool(merged_payload['loan_decision'])}")
    
    coordinator.route_message("coordinator", "DecisionAgent", "aggregate_all", merged_payload)

    # Đợi final decision
    time.sleep(1)

    # Tìm quyết định cuối cùng từ DecisionAgent
    final_decision = None
    for entry in reversed(coordinator.message_log):  # Duyệt ngược để lấy mới nhất
        if entry["from"] == "DecisionAgent" and entry["message"].get("type") == "final_decision":
            final_decision = entry["message"]["payload"]
            break

    if return_log:
        # SAFETY: Đảm bảo luôn có decision và reason
        if final_decision and isinstance(final_decision, dict):
            decision = final_decision.get("decision", "reject")
            reason = final_decision.get("reason", "Không có lý do từ DecisionAgent")
            # Thêm detailed_analysis nếu có
            result = {
                "decision": decision,
                "reason": reason,
                "logs": session_memory.get_conversation()
            }
            if "detailed_analysis" in final_decision:
                result["detailed_analysis"] = final_decision["detailed_analysis"]
            if "rule_based_system" in final_decision:
                result["rule_based_system"] = final_decision["rule_based_system"]
            if "hybrid_approach" in final_decision:
                result["hybrid_approach"] = final_decision["hybrid_approach"]
            return result
        else:
            # Fallback nếu DecisionAgent hoàn toàn fail
            return {
                "decision": "reject", 
                "reason": "Lỗi hệ thống: DecisionAgent không trả về kết quả hợp lệ",
                "logs": session_memory.get_conversation(),
                "error": "decision_agent_failed"
            }
    else:
        for entry in session_memory.get_conversation():
            print(entry)

if __name__ == "__main__":
    # Test hybrid workflow
    profile = "Sinh viên: 21 tuổi, Nữ, tier 1, STEM, GPA: 0.85, Thu nhập gia đình: 8M VND/tháng, không nợ, vay: 45M VND học phí"
    debate_to_decide_workflow(profile)
