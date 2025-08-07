# MAS Conversation Storage - MongoDB Integration

## Thay đổi chính:

### 1. **Simplified Express Communication**
- Thay vì gửi toàn bộ result và request_data
- Chỉ gửi thông báo đơn giản với request_id và decision
- Endpoint Express: `/api/v1/python/notification`

### 2. **MongoDB Storage Implementation**
- Lưu toàn bộ MAS conversation result dưới dạng stringify
- Collection: `masconversation` trong database `attacker_backend`
- Sử dụng Motor (async MongoDB driver)

## Cấu trúc Document MongoDB:

```json
{
  "_id": "ObjectId",
  "request_id": "uuid-string",
  "request_data": { /* Original request data */ },
  "result_stringify": "/* JSON string of full result */",
  "decision": "approve|reject",
  "processing_time": 2.45,
  "loan_amount": 50000000,
  "loan_purpose": "Học phí",
  "gpa_normalized": 0.85,
  "university_tier": 1,
  "timestamp": "ISODate",
  "created_at": "ISODate"
}
```

## Cài đặt Dependencies:

```bash
pip install motor pymongo fastapi uvicorn
```

## Cấu hình MongoDB:

1. Copy `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa `.env`:
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=attacker_backend
```

## Sử dụng:

### 1. Khởi động MongoDB:
```bash
# Ubuntu/Debian
sudo systemctl start mongod

# Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Khởi động FastAPI:
```bash
python3 -m uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
```

### 3. Test MongoDB:
```bash
python3 test_mongodb.py
```

## API Endpoints mới:

### `/api/v1/health`
- Kiểm tra trạng thái MongoDB connection

### `/api/v1/mas-conversations?limit=10`
- Lấy danh sách conversations gần nhất

### `/api/v1/mas-statistics`
- Thống kê: tổng số conversations, tỷ lệ approve/reject, thời gian xử lý trung bình

## Test API:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get conversations
curl http://localhost:8000/api/v1/mas-conversations?limit=5

# Get statistics
curl http://localhost:8000/api/v1/mas-statistics
```

## Express Service Integration:

Express service cần tạo endpoint để nhận notification:

```javascript
// POST /api/v1/python/notification
app.post('/api/v1/python/notification', (req, res) => {
  const { message, request_id, decision, timestamp } = req.body;
  console.log(`MAS Decision: ${decision} for request ${request_id}`);
  res.json({ status: 'ok', message: 'Notification received' });
});
```

## Lưu ý:

1. **Non-blocking Storage**: Lỗi MongoDB không làm fail API request chính
2. **Async Operations**: Sử dụng Motor cho async MongoDB operations
3. **Error Handling**: Có error handling cho tất cả MongoDB operations
4. **Statistics**: Có thể query thống kê approval rate, processing time
5. **Scalability**: Dễ dàng thêm indexes, sharding sau này
