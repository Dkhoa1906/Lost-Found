# Lost & Found – API Design

## 1. Tổng quan

Backend sử dụng Python + FastAPI để cung cấp API cho ứng dụng Android viết bằng Kotlin.
Database sử dụng PostgreSQL.

## 2. Các nhóm API

### Authentication
- Đăng ký
- Đăng nhập
- Lấy thông tin tài khoản hiện tại

### Posts
- Tạo bài đăng
- Xem danh sách bài đăng
- Xem chi tiết bài đăng
- Tìm kiếm và lọc bài đăng
- Cập nhật trạng thái bài đăng

### Verification
- Tạo câu hỏi xác minh
- Gửi yêu cầu xác minh
- Gửi câu trả lời
- Chấp nhận hoặc từ chối yêu cầu

### Chat
- Lấy danh sách cuộc trò chuyện
- Lấy lịch sử tin nhắn
- Gửi tin nhắn
- Nhận tin nhắn thời gian thực qua WebSocket

### Reports
- Gửi báo cáo vi phạm
- Xem và xử lý báo cáo bằng tài khoản Admin
