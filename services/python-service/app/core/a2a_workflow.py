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
        critical_data = critical_responses["AcademicAgent"]
        coordinator.route_message("coordinator", "AcademicAgent", "repredict_scholarship", {
            "memory": memory_data,
            "critical_response": critical_data.get("critical_response", ""),
            "recommended_decision": critical_data.get("recommended_decision", "")
        })
        repredict_done["AcademicAgent"] = True
    if critical_responses["FinanceAgent"]:
        critical_data = critical_responses["FinanceAgent"]
        coordinator.route_message("coordinator", "FinanceAgent", "repredict_loan", {
            "memory": memory_data,
            "critical_response": critical_data.get("critical_response", ""),
            "recommended_decision": critical_data.get("recommended_decision", "")
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
        # Thu thập 4 response chính theo yêu cầu
        academic_repredict = None
        finance_repredict = None
        critical_academic = None
        critical_finance = None
        
        print(f"[Workflow] 🔍 Collecting 4 responses from message log ({len(coordinator.message_log)} total messages)")
        
        # Duyệt message_log để collect responses
        for entry in coordinator.message_log:
            msg_type = entry["message"].get("type")
            sender = entry["from"]
            payload = entry["message"]["payload"]
            
            # Academic repredict response
            if sender == "AcademicAgent" and msg_type == "repredict_scholarship":
                academic_repredict = payload
                print(f"[Workflow] ✅ Found academic_repredict: {payload}")
            
            # Finance repredict response  
            elif sender == "FinanceAgent" and msg_type == "repredict_loan":
                finance_repredict = payload
                print(f"[Workflow] ✅ Found finance_repredict: {payload}")
                
            # Critical response to Academic
            elif sender == "CriticalAgent" and msg_type == "scholarship_decision_critical_response":
                critical_academic = payload
                print(f"[Workflow] ✅ Found critical_academic: {payload}")
                
            # Critical response to Finance
            elif sender == "CriticalAgent" and msg_type == "loan_decision_critical_response":
                critical_finance = payload
                print(f"[Workflow] ✅ Found critical_finance: {payload}")
        
        print(f"[Workflow] 📊 Collection summary:")
        print(f"  - academic_repredict: {'✅' if academic_repredict else '❌'}")
        print(f"  - finance_repredict: {'✅' if finance_repredict else '❌'}")
        print(f"  - critical_academic: {'✅' if critical_academic else '❌'}")
        print(f"  - critical_finance: {'✅' if critical_finance else '❌'}")
        
        # STRUCTURED OUTPUT theo yêu cầu
        if final_decision and isinstance(final_decision, dict):
            decision = final_decision.get("decision", "reject")
            reason = final_decision.get("reason", "Không có lý do từ DecisionAgent")
            detailed_analysis = final_decision.get("detailed_analysis", {})
            
            # Extract rule-based info từ detailed_analysis
            rule_based_info = detailed_analysis.get("rule_calculation", {})
            agent_consensus = detailed_analysis.get("agent_consensus", {})
            dual_condition = detailed_analysis.get("dual_condition_logic", {})
            
            # SAFE HANDLING: Ensure all responses have proper structure
            def safe_agent_response(response):
                if response and isinstance(response, dict):
                    return {
                        "decision": response.get("decision"),
                        "reason": response.get("reason")
                    }
                return None
            
            def safe_critical_response(response):
                if response and isinstance(response, dict):
                    return {
                        "critical_response": response.get("critical_response"),
                        "recommended_decision": response.get("recommended_decision")
                    }
                return None
            
            result = {
                # 4 RESPONSES CHÍNH
                "responses": {
                    "academic_repredict": safe_agent_response(academic_repredict),
                    "finance_repredict": safe_agent_response(finance_repredict), 
                    "critical_academic": safe_critical_response(critical_academic),
                    "critical_finance": safe_critical_response(critical_finance),
                    "final_decision": {
                        "decision": decision,
                        "reason": reason
                    }
                },
                
                # RULE-BASED INFORMATION
                "rule_based": {
                    "total_passed_count": rule_based_info.get("total_passed_count", 0),
                    "special_violations_count": rule_based_info.get("special_violations_count", 0),
                    "rule_based_decision": rule_based_info.get("rule_based_decision", "unknown"),
                    "rule_based_reason": rule_based_info.get("rule_based_reason", "N/A"),
                    "features_analysis": detailed_analysis.get("features_analysis", {})
                },
                
                # AGENT STATUS
                "agent_status": {
                    "academic_approve": agent_consensus.get("academic_approve", False),
                    "finance_approve": agent_consensus.get("finance_approve", False),
                    "at_least_one_agent_approve": agent_consensus.get("at_least_one_agent_approve", False),
                    "both_conditions_met": dual_condition.get("both_conditions_met", False)
                },
                
                # FINAL RESULT
                "final_result": {
                    "decision": decision,
                    "reason": reason,
                    "rule_based_pass": dual_condition.get("rule_based_pass", False),
                    "agent_support_available": dual_condition.get("agent_support_available", False),
                    "hybrid_approach": final_decision.get("hybrid_approach", "unknown")
                }
            }
            
            return result
        else:
            # Fallback nếu DecisionAgent hoàn toàn fail - use safe handling
            def safe_agent_response(response):
                if response and isinstance(response, dict):
                    return {
                        "decision": response.get("decision"),
                        "reason": response.get("reason")
                    }
                return None
            
            def safe_critical_response(response):
                if response and isinstance(response, dict):
                    return {
                        "critical_response": response.get("critical_response"),
                        "recommended_decision": response.get("recommended_decision")
                    }
                return None
            
            return {
                "responses": {
                    "academic_repredict": safe_agent_response(academic_repredict),
                    "finance_repredict": safe_agent_response(finance_repredict),
                    "critical_academic": safe_critical_response(critical_academic), 
                    "critical_finance": safe_critical_response(critical_finance),
                    "final_decision": {
                        "decision": "reject",
                        "reason": "Lỗi hệ thống: DecisionAgent không trả về kết quả hợp lệ"
                    }
                },
                "rule_based": {},
                "agent_status": {},
                "final_result": {
                    "decision": "reject",
                    "reason": "Lỗi hệ thống",
                    "error": "decision_agent_failed"
                }
            }
    else:
        for entry in session_memory.get_conversation():
            print(entry)

if __name__ == "__main__":
    # Test hybrid workflow
    profile = "Sinh viên: 21 tuổi, Nữ, tier 1, STEM, GPA: 0.85, Thu nhập gia đình: 8M VND/tháng, không nợ, vay: 45M VND học phí"
    debate_to_decide_workflow(profile)
