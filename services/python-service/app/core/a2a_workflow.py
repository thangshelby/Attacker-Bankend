from app.core.memory import SessionMemory
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.acadamic_agent import AcademicAgent  
from app.agents.critical_agent import CriticalAgent
from app.agents.decision import DecisionAgent
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

    # Vòng 1: Initial Arguments
    print("\n=== Vòng 1: Initial Arguments ===")
    academic_prompt = get_persona_prompt("optimist", profile)
    finance_prompt = get_persona_prompt("realist", profile)
    coordinator.route_message("coordinator", "AcademicAgent", "scholarship_application", {"profile": academic_prompt})
    coordinator.route_message("coordinator", "FinanceAgent", "loan_application", {"profile": finance_prompt})

    # Đợi một chút để agents xử lý (nếu cần, tùy thuộc vào thread-based implementation)
    time.sleep(1)  # Delay nhỏ để message_log cập nhật

    # Vòng 2: Critique & Rebuttal - FIXED VERSION
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

    # Vòng 3: Gộp tất cả response và gửi 1 lần cho DecisionAgent
    print("\n=== Vòng 3: Synthesis & Final Recommendation ===")
    merged_payload = {
        "scholarship_decision": academic_decision,
        "loan_decision": finance_decision,
        "scholarship_decision_critical_response": critical_responses["AcademicAgent"],
        "loan_decision_critical_response": critical_responses["FinanceAgent"],
        "repredict_scholarship": None,
        "repredict_loan": None
    }
    # Thu thập repredict từ message_log
    for entry in list(coordinator.message_log):
        msg_type = entry["message"].get("type")
        if entry["from"] == "AcademicAgent" and msg_type == "repredict_scholarship":
            merged_payload["repredict_scholarship"] = entry["message"]["payload"]
        elif entry["from"] == "FinanceAgent" and msg_type == "repredict_loan":
            merged_payload["repredict_loan"] = entry["message"]["payload"]

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
        return {
            "decision": final_decision.get("decision") if final_decision else None,
            "reason": final_decision.get("reason") if final_decision else None,
            "logs": session_memory.get_conversation()
        }
    else:
        for entry in session_memory.get_conversation():
            print(entry)

if __name__ == "__main__":
    # Hồ sơ mẫu
    profile = "Sinh viên: Trần Thị B, GPA 3.9/4.0, đạt giải Nhất Olympic Toán, hoạt động ngoại khóa xuất sắc. Thu nhập gia đình 20 triệu/tháng, không có nợ xấu."
    debate_to_decide_workflow(profile)
