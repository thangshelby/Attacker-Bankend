# Socket.IO Configuration Documentation

## Tổng quan

Đã tách cấu hình Socket.IO ra file riêng `src/config/socket.js` để dễ quản lý và mở rộng.

## Cấu trúc Files

```
src/
├── config/
│   └── socket.js           # Socket.IO configuration & event handlers
├── controllers/
│   └── socketController.js # API endpoints for Socket operations
├── routes/
│   └── socketRoute.js      # Socket.IO API routes
└── server.js              # Main server (simplified)
```

## Socket.IO Features

### 🔌 **Connection Management**
- User authentication via `user_join` event
- Track connected users and their rooms
- Automatic cleanup on disconnect

### 💬 **Chat System**
- Join/leave chat rooms
- Send/receive messages
- Typing indicators
- System messages

### 🔔 **Notification System**
- Send notifications to specific users
- Broadcast to all users
- Loan status updates
- MAS workflow notifications

### 📊 **Real-time Updates**
- User online/offline status
- Loan application status changes
- System announcements

## Socket Events

### Client → Server Events

| Event | Description | Data |
|-------|-------------|------|
| `user_join` | User authentication | `{userId, username, role}` |
| `join_room` | Join chat room | `roomId` |
| `leave_room` | Leave chat room | `roomId` |
| `send_message` | Send chat message | `{roomId, message, messageType}` |
| `typing_start` | Start typing indicator | `{roomId}` |
| `typing_stop` | Stop typing indicator | `{roomId}` |
| `loan_status_update` | Update loan status | `{targetUserId, loanId, status, message}` |

### Server → Client Events

| Event | Description | Data |
|-------|-------------|------|
| `user_joined` | User connection success | `{success, message, socketId}` |
| `new_message` | New chat message | `{id, userId, username, message, timestamp, roomId}` |
| `notification` | User-specific notification | `{type, title, message, data, timestamp}` |
| `broadcast_notification` | Global notification | `{type, title, message, timestamp}` |
| `loan_notification` | Loan status update | `{loanId, status, message, timestamp}` |
| `user_status_update` | User online/offline | `{userId, status, timestamp}` |

## API Endpoints

### 📡 **Socket.IO Management APIs**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/socket/notify-user` | Send notification to user | ✅ |
| POST | `/api/v1/socket/broadcast` | Broadcast to all users | ✅ |
| POST | `/api/v1/socket/loan-status` | Send loan status update | ✅ |
| GET | `/api/v1/socket/stats` | Get connection statistics | ✅ |
| POST | `/api/v1/socket/python-notification` | Handle Python service notifications | ❌ |
| POST | `/api/v1/socket/system-message` | Send system message | ✅ |

## Integration với Python Service

Python service sẽ gửi notifications đến Express qua endpoint:
```
POST /api/v1/socket/python-notification
```

**Request body:**
```json
{
  "message": "MAS conversation completed",
  "request_id": "uuid-12345",
  "decision": "approve",
  "timestamp": 1691234567.89
}
```

## Frontend Integration

### 1. **Connect to Socket.IO**
```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000', {
  withCredentials: true
});
```

### 2. **User Authentication**
```javascript
socket.emit('user_join', {
  userId: 'user123',
  username: 'John Doe',
  role: 'student'
});

socket.on('user_joined', (data) => {
  console.log('Connected:', data);
});
```

### 3. **Listen for Notifications**
```javascript
socket.on('notification', (notification) => {
  console.log('New notification:', notification);
  // Show toast/popup notification
});

socket.on('loan_notification', (loanData) => {
  console.log('Loan update:', loanData);
  // Update UI with loan status
});
```

### 4. **Chat Functionality**
```javascript
// Join room
socket.emit('join_room', 'room_123');

// Send message
socket.emit('send_message', {
  roomId: 'room_123',
  message: 'Hello everyone!',
  messageType: 'text'
});

// Listen for messages
socket.on('new_message', (message) => {
  console.log('New message:', message);
  // Add to chat UI
});
```

## Environment Variables

```env
# Express service
PORT=5000
NODE_ENV=development

# Socket.IO
SOCKET_CORS_ORIGIN=http://localhost:5173

# Python service integration
PYTHON_SERVICE_URL=http://localhost:8000
```

## Sử dụng trong Controllers

```javascript
import { socketConfig } from '../server.js';

// Send notification to user
export const someController = (req, res) => {
  const notification = {
    type: 'info',
    title: 'Update',
    message: 'Your profile has been updated'
  };
  
  socketConfig.sendNotificationToUser('user123', notification);
  
  res.json({ success: true });
};
```

## Error Handling

- Tất cả Socket events đều có error handling
- Connection failures không crash server
- Invalid data được validate trước khi xử lý
- Error logs chi tiết cho debugging

## Security Features

- CORS configuration cho frontend origin
- JWT middleware cho Socket API endpoints
- User authentication required cho protected events
- Input validation cho tất cả socket events

## Monitoring & Debugging

### Get Connection Stats:
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:5000/api/v1/socket/stats
```

### Test Notification:
```bash
curl -X POST \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"userId": "123", "notification": {"type": "test", "message": "Hello"}}' \
  http://localhost:5000/api/v1/socket/notify-user
```

## Performance Considerations

- Connection pooling được manage tự động
- Memory cleanup khi user disconnect
- Event listeners được remove properly
- Efficient room management

## Future Enhancements

- [ ] Message persistence to database
- [ ] Private messaging between users
- [ ] File sharing in chat
- [ ] Voice/video call integration
- [ ] Push notifications for mobile
- [ ] Rate limiting for messages
- [ ] Message encryption
