from queue import Queue
from threading import Thread
import time

class BaseAgent(Thread):
    def __init__(self, name, coordinator=None):
        super().__init__()
        self.name = name
        self.message_queue = Queue()
        self.coordinator = coordinator
        self.is_running = True

    def handle_message(self, message: dict):
        """
        Xử lý một tin nhắn. Lớp con phải triển khai phương thức này.
        """
        raise NotImplementedError

    def send_message(self, recipient: str, message_type: str, payload: dict):
        """
        Gửi một tin nhắn đến một agent khác thông qua Coordinator.
        """
        if self.coordinator:
            full_message = {
                "sender": self.name,
                "recipient": recipient,
                "type": message_type,
                "payload": payload
            }
            self.coordinator.route_message(full_message)
        else:
            print(f"[{self.name}] Lỗi: Không có coordinator để gửi tin nhắn.")

    def run(self):
        """
        Vòng lặp chính của agent, liên tục kiểm tra và xử lý tin nhắn.
        """
        print(f"[{self.name}] bắt đầu hoạt động.")
        while self.is_running:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                print(f"[{self.name}] đã nhận được tin nhắn: {message}")
                self.handle_message(message)
            time.sleep(0.1) # Ngủ một chút để tránh lãng phí CPU

    def stop(self):
        """Dừng agent."""
        self.is_running = False
        print(f"[{self.name}] đã dừng.")