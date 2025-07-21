class CoordinatorAgent:
    def __init__(self):
        self.agents = {}
        self.message_log = []

    def register_agent(self, agent):
        self.agents[agent.name] = agent
        agent.coordinator = self
        print(f"[Coordinator] Đã đăng ký agent: {agent.name}")

    def route_message(self, sender, recipient, message_type, payload):
        message = {
            "type": message_type,
            "sender": sender,
            "payload": payload
        }
        self.message_log.append({"from": sender, "to": recipient, "message": message})
        if recipient in self.agents:
            print(f"[Coordinator] Chuyển message từ {sender} tới {recipient} | type: {message_type}")
            self.agents[recipient].handle_message(message)
        elif recipient == "coordinator":
            # Chỉ log, không báo lỗi khi recipient là coordinator
            return
        else:
            print(f"[Coordinator] Agent '{recipient}' không tồn tại!")

    def broadcast(self, sender, message_type, payload):
        for name, agent in self.agents.items():
            if name != sender:
                self.route_message(sender, name, message_type, payload)

    def print_log(self):
        print("\n[Coordinator] Message Log:")
        for entry in self.message_log:
            print(entry)
