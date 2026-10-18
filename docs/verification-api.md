# Verification API – Xác minh chủ sở hữu

## 1. Tạo câu hỏi xác minh

**Endpoint:** `POST /posts/{post_id}/questions`

**Mô tả:** Người đăng bài `FOUND` tạo câu hỏi để xác minh người yêu cầu nhận lại đồ.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ chủ sở hữu bài đăng mới được tạo câu hỏi.
- Chỉ áp dụng cho bài đăng có loại `FOUND`.
- Nội dung câu hỏi không được để trống.

**Request Body:**
```json
{
  "question_text": "Món đồ có đặc điểm gì đặc biệt?"
}
```

**Response – 201 Created:**
```json
{
  "message": "Tạo câu hỏi xác minh thành công",
  "question_id": 1
}
```

## 2. Lấy danh sách câu hỏi xác minh

**Endpoint:** `GET /posts/{post_id}/questions`

**Mô tả:** Lấy danh sách câu hỏi xác minh của bài đăng.

**Yêu cầu:**
- Bài đăng phải tồn tại và có loại `FOUND`.
- Chỉ người dùng đủ quyền mới được xem câu hỏi theo quy trình xác minh.
- Không công khai câu hỏi trên danh sách bài đăng thông thường.

**Response – 200 OK:** Trả về danh sách câu hỏi của bài đăng.

## 3. Gửi yêu cầu xác minh

**Endpoint:** `POST /posts/{post_id}/verification-requests`

**Mô tả:** Người dùng gửi yêu cầu chứng minh mình là chủ sở hữu món đồ.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Không được gửi yêu cầu xác minh đối với bài đăng do chính mình tạo.
- Chỉ áp dụng cho bài đăng `FOUND` đang hoạt động.
- Không cho phép tạo nhiều yêu cầu đang chờ xử lý cho cùng một người dùng và bài đăng.

**Response – 201 Created:**
```json
{
  "message": "Gửi yêu cầu xác minh thành công",
  "request_id": 1,
  "status": "PENDING"
}
```

## 4. Gửi câu trả lời xác minh

**Endpoint:** `POST /verification-requests/{request_id}/answers`

**Mô tả:** Người yêu cầu gửi câu trả lời cho các câu hỏi xác minh.

**Request Body:**
```json
{
  "answers": [
    {
      "question_id": 1,
      "answer_text": "Mô tả đặc điểm của món đồ"
    }
  ]
}
```

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ người tạo yêu cầu xác minh mới được gửi câu trả lời.
- Các câu hỏi phải thuộc bài đăng được yêu cầu xác minh.
- Câu trả lời chỉ được gửi khi yêu cầu còn ở trạng thái `PENDING`.

**Response – 201 Created:**
```json
{
  "message": "Gửi câu trả lời thành công"
}
```

## 5. Xem yêu cầu xác minh

**Endpoint:** `GET /verification-requests/{request_id}`

**Mô tả:** Xem thông tin yêu cầu xác minh và câu trả lời liên quan.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ người tạo bài đăng và người gửi yêu cầu mới được xem chi tiết.

**Response – 200 OK:** Trả về thông tin yêu cầu, trạng thái và câu trả lời phù hợp với quyền truy cập.

## 6. Chấp nhận hoặc từ chối yêu cầu

**Endpoint:** `PATCH /verification-requests/{request_id}`

**Mô tả:** Người đăng bài xem câu trả lời và quyết định chấp nhận hoặc từ chối yêu cầu.

**Request Body:**
```json
{
  "status": "APPROVED"
}
```

`status` chỉ nhận `APPROVED` hoặc `REJECTED`.

**Yêu cầu:**
- Người dùng phải đăng nhập.
- Chỉ chủ sở hữu bài đăng mới được quyết định.
- Yêu cầu phải đang ở trạng thái `PENDING`.
- Chỉ chấp nhận khi người yêu cầu đã gửi câu trả lời cần thiết.

**Response – 200 OK:**
```json
{
  "message": "Cập nhật yêu cầu xác minh thành công",
  "status": "APPROVED"
}
```

## 7. Quy tắc chung

- Người dùng phải đăng nhập khi thực hiện các thao tác xác minh.
- Máy chủ phải kiểm tra quyền sở hữu và quyền truy cập ở mọi endpoint.
- Không cho phép người dùng tự xác nhận yêu cầu của chính mình.
- Chỉ yêu cầu được chấp nhận mới đủ điều kiện để mở cuộc trò chuyện.
- Không tiết lộ câu trả lời xác minh cho người không có quyền truy cập.
- Các trạng thái hợp lệ gồm `PENDING`, `APPROVED` và `REJECTED`.
