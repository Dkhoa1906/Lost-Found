# ĐẶC TẢ API BÀI ĐĂNG (POSTS API)

## 1. Tạo bài đăng

**Endpoint:** `POST /posts`

**Xác thực:** Bắt buộc đăng nhập.

**Dữ liệu gửi lên (Request Body):**

```json
{
  "type": "LOST",
  "title": "Ví màu đen bị thất lạc",
  "description": "Ví màu đen, bên trong có thẻ sinh viên",
  "category": "WALLET",
  "image_url": "https://example.com/image.jpg",
  "location": "Khuôn viên trường đại học",
  "event_time": "2026-10-18T08:00:00"
}
```

**Quy tắc xử lý:**
- Người dùng phải đăng nhập trước khi tạo bài đăng.
- `type` chỉ nhận một trong hai giá trị `LOST` (thất lạc) hoặc `FOUND` (nhặt được).
- `title` là trường bắt buộc.
- `user_id` được lấy từ thông tin người dùng đã xác thực, không nhận trực tiếp từ dữ liệu gửi lên.
- `status` mặc định là `ACTIVE` (đang hoạt động).
- `event_time` là thời điểm món đồ bị mất hoặc được tìm thấy.

**Phản hồi thành công:** `201 Created`

```json
{
  "message": "Tạo bài đăng thành công",
  "post_id": 1
}
```

**Các lỗi có thể xảy ra:**
- `400 Bad Request`: Dữ liệu gửi lên không hợp lệ.
- `401 Unauthorized`: Người dùng chưa đăng nhập hoặc thông tin xác thực không hợp lệ.
- `422 Unprocessable Entity`: Dữ liệu không đáp ứng yêu cầu kiểm tra.

## 2. Lấy danh sách bài đăng

**Endpoint:** `GET /posts`

**Xác thực:** Không bắt buộc.

**Tham số truy vấn (Query Parameters):**
- `type`: Lọc theo loại bài đăng `LOST` hoặc `FOUND` (không bắt buộc).
- `category`: Lọc theo danh mục đồ vật (không bắt buộc).
- `keyword`: Tìm kiếm theo tiêu đề và mô tả (không bắt buộc).

**Quy tắc xử lý:**
- Chỉ trả về các bài đăng có trạng thái `ACTIVE`.
- Áp dụng các điều kiện lọc và tìm kiếm nếu người dùng cung cấp.
- Không trả về thông tin liên hệ riêng tư như số điện thoại.

**Phản hồi thành công:** `200 OK`

Trả về danh sách các bài đăng phù hợp với điều kiện tìm kiếm.

## 3. Xem chi tiết bài đăng

**Endpoint:** `GET /posts/{post_id}`

**Xác thực:** Không bắt buộc.

**Quy tắc xử lý:**
- Tìm bài đăng theo `post_id`.
- Chỉ trả về thông tin được phép công khai.
- Không tiết lộ số điện thoại hoặc thông tin liên hệ riêng tư của người đăng.

**Phản hồi thành công:** `200 OK`

Trả về thông tin chi tiết gồm:
- Mã bài đăng.
- Mã người đăng.
- Loại bài đăng.
- Tiêu đề và mô tả.
- Danh mục đồ vật.
- Đường dẫn hình ảnh.
- Địa điểm.
- Thời điểm mất hoặc tìm thấy.
- Trạng thái bài đăng.
- Thời điểm tạo bài đăng.

**Lỗi có thể xảy ra:**
- `404 Not Found`: Không tìm thấy bài đăng hoặc bài đăng không còn khả dụng.

## 4. Cập nhật bài đăng

**Endpoint:** `PUT /posts/{post_id}`

**Xác thực:** Bắt buộc đăng nhập.

**Quy tắc xử lý:**
- Chỉ người tạo bài đăng mới có quyền cập nhật.
- Máy chủ phải kiểm tra quyền sở hữu bài đăng trước khi xử lý.
- Dữ liệu cập nhật phải được kiểm tra tính hợp lệ.
- Không cho phép người dùng tự thay đổi quyền hoặc danh tính người đăng.

**Phản hồi thành công:** `200 OK`

```json
{
  "message": "Cập nhật bài đăng thành công"
}
```

**Các lỗi có thể xảy ra:**
- `401 Unauthorized`: Chưa đăng nhập hoặc thông tin xác thực không hợp lệ.
- `403 Forbidden`: Không có quyền cập nhật bài đăng.
- `404 Not Found`: Không tìm thấy bài đăng.
- `422 Unprocessable Entity`: Dữ liệu cập nhật không hợp lệ.

## 5. Xóa bài đăng

**Endpoint:** `DELETE /posts/{post_id}`

**Xác thực:** Bắt buộc đăng nhập.

**Quy tắc xử lý:**
- Chỉ người tạo bài đăng mới có quyền xóa.
- Máy chủ phải kiểm tra quyền sở hữu trước khi xóa.
- Cần xử lý các dữ liệu liên quan như câu hỏi xác minh và yêu cầu nhận lại đồ để tránh lỗi liên kết dữ liệu.

**Phản hồi thành công:** `200 OK`

```json
{
  "message": "Xóa bài đăng thành công"
}
```

**Các lỗi có thể xảy ra:**
- `401 Unauthorized`: Chưa đăng nhập hoặc thông tin xác thực không hợp lệ.
- `403 Forbidden`: Không có quyền xóa bài đăng.
- `404 Not Found`: Không tìm thấy bài đăng.

## 6. Quy tắc bảo mật

- Chỉ người dùng đã đăng nhập mới được tạo, cập nhật hoặc xóa bài đăng.
- Máy chủ phải kiểm tra quyền sở hữu trước khi cho phép cập nhật hoặc xóa.
- Không công khai số điện thoại hoặc thông tin liên hệ riêng tư.
- Dữ liệu đầu vào phải được kiểm
