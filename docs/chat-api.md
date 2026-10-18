# Chat API – Nhắn tin riêng

## 1. Tạo cuộc trò chuyện

**Endpoint:** `POST /conversations`

**Mô tả:** Tạo cuộc trò chuyện giữa người đăng bài và người yêu cầu nhận lại đồ sau khi xác minh thành công.

**Request Body:**
```json
{
  "post_id": 1,
  "other_user_id": 2
}
```

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ tạo cuộc trò chuyện khi yêu cầu xác minh liên quan đã được `APPROVED`.
- Chỉ người đăng bài và người được chấp nhận mới được tham gia.
- Không tạo cuộc trò chuyện trùng lặp cho cùng bài đăng và hai người dùng.
- Máy chủ phải xác định danh tính người dùng từ token xác thực.

**Response – 201 Created:**
```json
{
  "message": "Tạo cuộc trò chuyện thành công",
  "conversation_id": 1
}
```

## 2. Lấy danh sách cuộc trò chuyện

**Endpoint:** `GET /conversations`

**Mô tả:** Lấy danh sách cuộc trò chuyện của người dùng đang đăng nhập.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ trả về các cuộc trò chuyện mà người dùng là thành viên.

**Response – 200 OK:** Trả về danh sách cuộc trò chuyện, mã bài đăng liên quan và thông tin người trò chuyện cùng.

## 3. Xem lịch sử tin nhắn

**Endpoint:** `GET /conversations/{conversation_id}/messages`

**Mô tả:** Lấy danh sách tin nhắn trong một cuộc trò chuyện.

**Query Parameters:**
- `limit`: Số tin nhắn tối đa trả về.
- `before_id`: Lấy các tin nhắn cũ hơn mã tin nhắn được chỉ định (không bắt buộc).

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ thành viên của cuộc trò chuyện mới được xem tin nhắn.

**Response – 200 OK:** Trả về danh sách tin nhắn theo thứ tự thời gian.

## 4. Gửi tin nhắn

**Endpoint:** `POST /conversations/{conversation_id}/messages`

**Mô tả:** Gửi tin nhắn vào cuộc trò chuyện.

**Request Body:**
```json
{
  "content": "Mình muốn xác nhận thêm về món đồ."
}
```

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ thành viên của cuộc trò chuyện mới được gửi tin nhắn.
- `content` không được để trống.
- `sender_id` được lấy từ token xác thực, không nhận trực tiếp từ request body.

**Response – 201 Created:**
```json
{
  "message": "Gửi tin nhắn thành công",
  "message_id": 1
}
```

## 5. Quy tắc chung

- Các API cuộc trò chuyện yêu cầu xác thực.
- Máy chủ phải kiểm tra quyền truy cập trước khi đọc hoặc gửi tin nhắn.
- Không cho phép người ngoài cuộc trò chuyện xem nội dung trao đổi.
- Không công khai số điện thoại hoặc thông tin liên hệ riêng tư.
- Chỉ cho phép tạo cuộc trò chuyện sau khi yêu cầu xác minh được chấp nhận.
- Tin nhắn được lưu trong cơ sở dữ liệu để có thể xem lại lịch sử.
- Chat thời gian thực có thể được triển khai bằng WebSocket ở bước lập trình.
