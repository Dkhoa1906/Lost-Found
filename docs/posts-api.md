# Posts API – Quản lý bài đăng

## 1. Tạo bài đăng

**Endpoint:** `POST /posts`

**Mô tả:** Tạo bài đăng tìm đồ thất lạc hoặc thông báo nhặt được đồ.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- `type` chỉ nhận `LOST` hoặc `FOUND`.
- `title` là trường bắt buộc.
- `user_id` lấy từ thông tin xác thực của người dùng.
- `status` mặc định là `ACTIVE`.

**Request Body:**
```json
{
  "type": "LOST",
  "title": "Ví màu đen",
  "description": "Ví màu đen, bên trong có thẻ sinh viên",
  "category": "WALLET",
  "image_url": "https://example.com/image.jpg",
  "location": "Khuôn viên trường",
  "event_time": "2026-10-18T08:00:00"
}
```

**Response – 201 Created:**
```json
{
  "message": "Tạo bài đăng thành công",
  "post_id": 1
}
```

**Lỗi:** `401 Unauthorized`, `422 Unprocessable Entity`.

## 2. Lấy danh sách bài đăng

**Endpoint:** `GET /posts`

**Mô tả:** Lấy danh sách bài đăng đang hoạt động, hỗ trợ lọc và tìm kiếm.

**Query Parameters:**
- `type`: Lọc theo loại bài đăng (`LOST`, `FOUND`).
- `category`: Lọc theo danh mục đồ vật.
- `keyword`: Tìm kiếm theo tiêu đề và mô tả.

**Response – 200 OK:** Trả về danh sách bài đăng phù hợp.

**Lưu ý:** Không trả về thông tin liên hệ riêng tư của người đăng.

## 3. Xem chi tiết bài đăng

**Endpoint:** `GET /posts/{post_id}`

**Mô tả:** Lấy thông tin chi tiết của một bài đăng.

**Response – 200 OK:** Trả về thông tin bài đăng, bao gồm tiêu đề, mô tả, hình ảnh, địa điểm, thời điểm mất/nhặt được và trạng thái.

**Lỗi:** `404 Not Found` nếu không tìm thấy bài đăng.

## 4. Cập nhật bài đăng

**Endpoint:** `PUT /posts/{post_id}`

**Mô tả:** Cập nhật thông tin bài đăng.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ chủ sở hữu bài đăng mới được cập nhật.
- Dữ liệu cập nhật phải hợp lệ.

**Response – 200 OK:**
```json
{
  "message": "Cập nhật bài đăng thành công"
}
```

**Lỗi:** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`.

## 5. Xóa bài đăng

**Endpoint:** `DELETE /posts/{post_id}`

**Mô tả:** Xóa bài đăng của người dùng.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ chủ sở hữu bài đăng mới được xóa.
- Xử lý các dữ liệu liên quan để bảo đảm tính toàn vẹn dữ liệu.

**Response – 200 OK:**
```json
{
  "message": "Xóa bài đăng thành công"
}
```

**Lỗi:** `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.

## 6. Quy tắc chung

- Các API tạo, cập nhật và xóa bài đăng yêu cầu xác thực.
- Máy chủ phải kiểm tra quyền sở hữu trước khi cập nhật hoặc xóa.
- Không công khai số điện thoại hoặc thông tin liên hệ riêng tư.
- Kiểm tra dữ liệu đầu vào trước khi lưu vào cơ sở dữ liệu.
- Chỉ hiển thị bài đăng phù hợp với trạng thái hiện tại.
