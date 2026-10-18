# Authentication API Specification

## 1. Tổng quan

- Backend: Python + FastAPI
- Database: PostgreSQL
- Authentication: JWT
- Content-Type: application/json

## 2. API đăng ký

**Endpoint:** `POST /auth/register`

### Request

    {
      "username": "khoa123",
      "password": "example_password",
      "phone": "0901234567"
    }

### Xử lý
1. Kiểm tra dữ liệu đầu vào.
2. Kiểm tra username đã tồn tại chưa.
3. Kiểm tra username, password và số điện thoại hợp lệ.
4. Băm password bằng thuật toán phù hợp.
5. Lưu tài khoản vào database với role mặc định là USER.
6. Trả về kết quả đăng ký.

### Response thành công — 201 Created

    {
      "message": "Registration successful"
    }

### Các lỗi có thể xảy ra

- `400 Bad Request`: Dữ liệu không hợp lệ.
- `409 Conflict`: Username đã tồn tại.

## 3. API đăng nhập

**Endpoint:** `POST /auth/login`

### Request

    {
      "username": "khoa123",
      "password": "example_password"
    }

### Xử lý
1. Tìm tài khoản theo username.
2. Kiểm tra password với password hash đã lưu.
3. Nếu thông tin không hợp lệ, trả về lỗi đăng nhập.
4. Nếu hợp lệ, tạo access token.
5. Trả token và thông tin tài khoản cần thiết.

### Response thành công — 200 OK

    {
      "access_token": "<access_token>",
      "token_type": "bearer",
      "user": {
        "user_id": 1,
        "username": "khoa123",
        "role": "USER"
      }
    }

### Các lỗi có thể xảy ra

- `401 Unauthorized`: Username hoặc password không chính xác.
- `422 Unprocessable Entity`: Request sai định dạng hoặc thiếu trường bắt buộc.

## 4. API lấy thông tin người dùng hiện tại

**Endpoint:** `GET /users/me`

### Authentication

Yêu cầu access token hợp lệ trong header:

    Authorization: Bearer <access_token>

### Response thành công — 200 OK

    {
      "user_id": 1,
      "username": "khoa123",
      "phone": "0901234567",
      "role": "USER"
    }

### Các lỗi có thể xảy ra

- `401 Unauthorized`: Token không hợp lệ hoặc đã hết hạn.

## 5. Quy tắc bảo mật

- Không lưu password dạng văn bản thuần.
- Không trả password hoặc password hash về ứng dụng Android.
- Không công khai số điện thoại trong thông tin hồ sơ công khai.
- Role phải được kiểm tra ở Backend; không tin role do ứng dụng gửi lên.
- Không phân biệt lỗi đăng nhập giữa username không tồn tại và password sai.
