from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.acadamic_agent import AcademicAgent
from app.agents.critical_agent import CriticalAgent
from app.agents.decision import DecisionAgent
from app.core.decision_workflow import get_persona_prompt

def debate_to_decide_workflow(profile, return_log: bool = False):
    # Khởi tạo coordinator và các agent với persona
    coordinator = CoordinatorAgent()
    academic = AcademicAgent(name="AcademicAgent")
    finance = FinanceAgent(name="FinanceAgent")
    critic = CriticalAgent(name="CriticalAgent")
    decision = DecisionAgent(name="DecisionAgent")

    # Đăng ký agent
    for agent in [academic, finance, critic, decision]:
        coordinator.register_agent(agent)

    # Vòng 1: Initial Arguments
    print("\n=== Vòng 1: Initial Arguments ===")
    academic_prompt = get_persona_prompt("optimist", profile)
    finance_prompt = get_persona_prompt("realist", profile)
    coordinator.route_message("coordinator", "AcademicAgent", "scholarship_application", {"profile": academic_prompt})
    coordinator.route_message("coordinator", "FinanceAgent", "loan_application", {"profile": finance_prompt})

    # Vòng 2: Critique & Rebuttal
    print("\n=== Vòng 2: Critique & Rebuttal ===")
    # Gửi các quyết định cho CriticAgent phản biện và chuyển luôn phản hồi của CriticAgent cho DecisionAgent
    for entry in coordinator.message_log:
        if entry["to"] in ["AcademicAgent", "FinanceAgent"] and entry["message"]["type"] in ["scholarship_decision", "loan_decision"]:
            # Gửi cho CriticalAgent phản biện
            coordinator.route_message("coordinator", "CriticalAgent", entry["message"]["type"], entry["message"]["payload"])

    # Sau khi CriticalAgent phản biện, chuyển tất cả phản hồi critical_response cho DecisionAgent tổng hợp
    for entry in coordinator.message_log:
        if entry["from"] == "CriticalAgent" and entry["message"]["type"] in ["scholarship_decision_critical_response", "loan_decision_critical_response"]:
            # Gửi cho DecisionAgent
            coordinator.route_message("coordinator", "DecisionAgent", entry["message"]["type"], entry["message"]["payload"])

    # Ngoài ra, chuyển luôn phản hồi của AcademicAgent và FinanceAgent cho DecisionAgent (nếu chưa có)
    for entry in coordinator.message_log:
        if entry["from"] in ["AcademicAgent", "FinanceAgent"] and entry["message"]["type"] in ["scholarship_decision", "loan_decision"]:
            coordinator.route_message("coordinator", "DecisionAgent", entry["message"]["type"], entry["message"]["payload"])

    # Vòng 3: Synthesis & Final Recommendation
    print("\n=== Vòng 3: Synthesis & Final Recommendation ===")
    coordinator.route_message("coordinator", "DecisionAgent", "aggregate_and_decide", {})

    # Tìm quyết định cuối cùng từ DecisionAgent
    final_decision = None
    for entry in coordinator.message_log[::-1]:
        if entry["from"] == "DecisionAgent" and entry["message"]["type"] == "final_decision":
            final_decision = entry["message"]["payload"]
            break

    if return_log:
        return {
            "decision": final_decision["decision"] if final_decision else None,
            "reason": final_decision["reason"] if final_decision else None,
            "logs": coordinator.message_log
        }
    else:
        coordinator.print_log()

if __name__ == "__main__":
    # Hồ sơ mẫu
    profile = "Sinh viên: Trần Thị B, GPA 3.9/4.0, đạt giải Nhất Olympic Toán, hoạt động ngoại khóa xuất sắc. Thu nhập gia đình 20 triệu/tháng, không có nợ xấu."
    debate_to_decide_workflow(profile)
