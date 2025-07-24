from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.memory import Memory

class SessionMemory:
    """
    Bộ nhớ dùng Memory mới nhất cho mỗi phiên làm việc giữa các agent.
    """
    def __init__(self, session_id="default_session", token_limit=40000):
        self.memory = Memory.from_defaults(session_id=session_id, token_limit=token_limit)
        self._conversation = []  # Thêm dòng này để khởi tạo conversation list

    def add_message(self, sender, recipient, message_type, payload):
        # Map agent names to valid ChatMessage roles
        agent_role_map = {
            "coordinator": "system",
            "AcademicAgent": "user",
            "FinanceAgent": "user", 
            "CriticalAgent": "assistant",
            "DecisionAgent": "assistant"
        }
        role = agent_role_map.get(sender, "user")
        
        # Add to LlamaIndex memory
        msg = ChatMessage(
            role=role,
            content=f"{message_type}: {payload}",
        )
        self.memory.put(msg)
        
        # Add to our custom conversation log
        self._conversation.append({
            "from": sender,
            "to": recipient,
            "message": {
                "type": message_type,
                "payload": payload
            }
        })

    def get_conversation(self):
        # Trả về conversation log thay vì memory (vì memory trả về ChatMessage objects)
        return self._conversation

    def get_llm_memory(self):
        # Phương thức mới để lấy LlamaIndex memory nếu cần
        return list(self.memory)

    def clear(self):
        self.memory.clear()
        self._conversation.clear()  # Clear cả conversation log
