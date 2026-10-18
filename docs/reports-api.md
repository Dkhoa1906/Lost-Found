# Reports API – Báo cáo vi phạm

## 1. Tạo báo cáo

**Endpoint:** `POST /reports`

**Mô tả:** Cho phép người dùng báo cáo bài đăng hoặc người dùng có dấu hiệu vi phạm.

**Request Body:**
```json
{
  "post_id": 1,
  "reported_user_id": null,
  "reason": "SCAM",
  "description": "Nội dung có dấu hiệu lừa đảo."
}
```

**Yêu cầu:**
- Người dùng phải đăng nhập.
- `post_id` hoặc `reported_user_id` phải có ít nhất một giá trị.
- `reason` là trường bắt buộc.
- `reporter_user_id` được lấy từ token xác thực.
- Không cho phép người dùng tự báo cáo chính mình.
- Báo cáo mới có trạng thái mặc định `PENDING`.

**Response – 201 Created:**
```json
{
  "message": "Tạo báo cáo thành công",
  "report_id": 1,
  "status": "PENDING"
}
```

## 2. Xem danh sách báo cáo

**Endpoint:** `GET /reports`

**Mô tả:** Cho phép quản trị viên xem danh sách báo cáo để xử lý vi phạm.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ tài khoản có vai trò `ADMIN` mới được sử dụng endpoint này.
- Có thể lọc báo cáo theo trạng thái.

**Query Parameters:**
- `status`: Lọc theo trạng thái báo cáo, ví dụ `PENDING`, `RESOLVED`, `REJECTED`.

**Response – 200 OK:** Trả về danh sách báo cáo phù hợp.

## 3. Xem chi tiết báo cáo

**Endpoint:** `GET /reports/{report_id}`

**Mô tả:** Xem chi tiết một báo cáo vi phạm.

**Yêu cầu:**
- Chỉ quản trị viên mới được xem.
- Máy chủ kiểm tra sự tồn tại của báo cáo trước khi trả kết quả.

**Response – 200 OK:** Trả về nội dung báo cáo, đối tượng bị báo cáo và trạng thái xử lý.

**Lỗi:** `404 Not Found` nếu không tìm thấy báo cáo.

## 4. Cập nhật trạng thái báo cáo

**Endpoint:** `PATCH /reports/{report_id}`

**Mô tả:** Quản trị viên cập nhật kết quả xử lý báo cáo.

**Request Body:**
```json
{
  "status": "RESOLVED"
}
```

**Yêu cầu:**
- Chỉ tài khoản `ADMIN` mới được thực hiện.
- `status` chỉ nhận các giá trị được hệ thống cho phép.
- Máy chủ phải kiểm tra quyền quản trị viên trước khi cập nhật.

**Response – 200 OK:**
```json
{
  "message": "Cập nhật báo cáo thành công",
  "status": "RESOLVED"
}
```

## 5. Quy tắc chung

- Người dùng phải đăng nhập để gửi báo cáo.
- Chỉ quản trị viên được xem danh sách, xem chi tiết và xử lý báo cáo.
- Không cho phép người dùng tự báo cáo chính mình.
- Máy chủ phải xác thực dữ liệu và quyền truy cập.
- Thông tin người báo cáo không được công khai tùy tiện.
- Các trạng thái báo cáo phải thống nhất với quy định của hệ thống.
