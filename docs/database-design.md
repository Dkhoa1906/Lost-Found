Mình đã thiết kế sơ bộ Database cho dự án Lost & Found bằng dbdiagram.io. Đây là bản thiết kế cấu trúc cơ sở dữ liệu, chưa phải database PostgreSQL đã triển khai thực tế.

Database hiện có 8 bảng chính:
- `users`: Lưu thông tin tài khoản và vai trò người dùng.
- `posts`: Lưu các bài đăng mất đồ/nhặt được đồ.
- `verification_questions`: Lưu câu hỏi xác minh quyền sở hữu.
- `verification_requests`: Lưu yêu cầu xác minh của người muốn nhận đồ.
- `verification_answers`: Lưu câu trả lời xác minh.
- `conversations`: Quản lý các cuộc trò chuyện giữa người dùng.
- `messages`: Lưu nội dung tin nhắn.
- `reports`: Lưu báo cáo vi phạm.

Sơ đồ thể hiện cấu trúc dữ liệu, khóa chính, khóa ngoại và mối quan hệ giữa các bảng.
Mục đích là thống nhất cách tổ chức dữ liệu trước khi lập trình Backend và Android, giúp các thành viên phối hợp dễ dàng và hạn chế phải sửa cấu trúc dữ liệu nhiều lần.

https://dbdiagram.io/d/LostAndFound_Database-6ad41dc2fe5cc8bda2e7c8a7
