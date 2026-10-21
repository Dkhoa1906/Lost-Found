# 🔎 Lost & Found

> Ứng dụng di động giúp **người mất đồ** và **người nhặt được đồ** tìm thấy nhau, đồng thời hạn chế giả mạo và lợi dụng thông tin bài đăng.

![Platform](https://img.shields.io/badge/mobile-Android%20(Kotlin%20%2B%20Compose)-3DDC84)
![Backend](https://img.shields.io/badge/backend-FastAPI%20(Python)-009688)
![Database](https://img.shields.io/badge/database-Supabase%20(PostgreSQL)-3ECF8E)
![Admin](https://img.shields.io/badge/admin-React%20%2B%20TypeScript-61DAFB)

---

## 1. Vấn đề và hướng giải quyết

Các nhóm Facebook "nhặt được của rơi" có hai vấn đề lớn:

| Vấn đề | Hậu quả |
|---|---|
| Ai cũng bình luận được dưới bài nhặt đồ | Người **không phải chủ đồ** có thể nhận bừa, người nhặt bị làm phiền hoặc bị lừa |
| Thông tin liên hệ công khai | Bị spam, bị lợi dụng, bị đòi tiền "chuộc" |

**Lost & Found không dùng comment công khai.** Thay vào đó, luồng chính của hệ thống là:

```
Find  →  Verify  →  Contact  →  Return  →  Confirm  →  Done
Tìm      Xác minh   Chat riêng   Trao trả   2 bên xác nhận   Hoàn tất
```

### Luồng xác minh quyền sở hữu (điểm đặc trưng)

```mermaid
flowchart TD
    A[Người nhặt đăng bài FOUND<br/>+ đặt 1-3 câu hỏi xác minh] --> B[Người mất đồ tìm thấy bài]
    B --> C[Bấm 'Đây là đồ của tôi']
    C --> D[Trả lời các câu hỏi]
    D --> E{Người nhặt<br/>đọc và quyết định}
    E -- Fail --> F[Không được liên hệ<br/>có thể thử lại tối đa N lần]
    E -- Pass --> G[💬 Mở chat riêng realtime]
    G --> H[Thống nhất thời gian / địa điểm]
    H --> I[Trao trả đồ]
    I --> J{Cả hai bên<br/>cùng bấm xác nhận?}
    J -- Chưa đủ --> I
    J -- Đủ --> K[✅ DONE<br/>bài chuyển RESOLVED]
```

> Hệ thống **không tự kết luận** ai là chủ sở hữu. Quyết định Pass/Fail thuộc về người nhặt đồ.
> Bài không được xử lý sau **30 ngày** sẽ tự chuyển `EXPIRED`.

---

## 2. Tính năng (phạm vi MVP)

| Nhóm | Chức năng |
|---|---|
| 👤 Tài khoản | Đăng ký / đăng nhập bằng email + password, kiểm tra điều kiện tối thiểu, không trùng tài khoản, quên / đổi mật khẩu bằng mã gửi qua email, số điện thoại lưu nhưng **không công khai**, phân quyền User / Admin, password luôn được hash |
| 📰 Bảng tin | Chuyển đổi **Lost** (đồ mình mất) / **Found** (đồ mình nhặt), bài đăng gồm ảnh, mô tả, loại tài sản, tag, địa điểm, thời gian, người đăng; tìm kiếm + bộ lọc (loại bài, danh mục, thời gian đăng), sắp xếp **Mới nhất / Gần nhất**, khối **Cần xử lý** trên trang chủ |
| 🛡️ Xác minh | Câu hỏi do người nhặt đặt, người nhận chủ phải trả lời, người nhặt chấm Pass/Fail |
| 💬 Nhắn tin | Chat riêng 1-1 realtime, lưu lịch sử, không có comment công khai |
| ✅ Hoàn tất | Hai bên cùng xác nhận → DONE; bài quá hạn → Expired/Archived; người dùng có thể ẩn / hiện lại / xóa bài của mình |
| 🔔 Thông báo | Yêu cầu xác minh mới, được duyệt nhắn tin, chờ xác nhận trao trả, bài DONE, kết quả xử lý báo cáo |
| 🚩 Report & Admin | Báo cáo spam, scam, thông tin sai, đòi tiền bất thường; admin xử lý report, gỡ bài, khóa tài khoản |

**Chưa làm trong MVP:** AI matching, recommendation, OTP, comment, map realtime, tính năng social phụ.

---

## 3. Kiến trúc tổng quan

```mermaid
flowchart LR
    subgraph Clients
        APP["📱 Android App<br/>Kotlin + Jetpack Compose"]
        WEB["🖥️ Admin Web<br/>React + TypeScript"]
    end

    subgraph Backend["Backend (tự viết)"]
        API["⚙️ FastAPI (Python)<br/>logic nghiệp vụ + kiểm tra quyền"]
    end

    subgraph Supabase["☁️ Supabase"]
        AUTH["🔐 Auth<br/>(JWT, password hash)"]
        DB[("🗄️ PostgreSQL<br/>+ Row Level Security")]
        RT["⚡ Realtime<br/>(WebSocket)"]
        STO["🖼️ Storage<br/>(ảnh)"]
    end

    APP -- "đăng nhập" --> AUTH
    APP -- "đọc dữ liệu (RLS)" --> DB
    APP -- "upload ảnh" --> STO
    APP <-. "tin nhắn realtime" .-> RT
    APP -- "hành động nghiệp vụ<br/>REST + JWT" --> API

    WEB -- "đăng nhập" --> AUTH
    WEB -- "đọc danh sách" --> DB
    WEB -- "hành động admin<br/>REST + JWT" --> API

    API -- "xác thực JWT (JWKS)" --> AUTH
    API -- "SQL + transaction<br/>(secret key)" --> DB
    DB --- RT
```

### Quy tắc phân chia (dễ nhớ)

> **Đọc → đi thẳng Supabase (được RLS bảo vệ).  Ghi thay đổi trạng thái nghiệp vụ → đi qua FastAPI.**

| Việc cần làm | Đi đường nào | Vì sao |
|---|---|---|
| Xem bảng tin, tìm kiếm, xem chi tiết | App → Supabase (PostgREST / RPC `search_posts`) | Nhanh, ít code, RLS tự chặn dữ liệu không được xem |
| Gửi / nhận tin nhắn | App → Supabase Realtime | Realtime, độ trễ thấp |
| Upload ảnh | App → Supabase Storage | Không tốn băng thông backend |
| Đăng ký tài khoản | App → **FastAPI** | Kiểm tra email/password ở server, tự tạo hồ sơ và handle công khai |
| Đăng nhập, quên / đổi mật khẩu | App → Supabase Auth | Dùng sẵn, không cần viết lại |
| Cập nhật số điện thoại | App → **FastAPI** | SĐT nằm ở bảng riêng tư, không cho client ghi trực tiếp |
| Sắp xếp theo khoảng cách, số liệu "Cần xử lý" | App → Supabase (RPC) | Hàm SQL `search_posts`, `my_todo_counts` |
| Tạo bài (ảnh + tag + câu hỏi) | App → **FastAPI** | Cần transaction nhiều bảng, kiểm tra dữ liệu |
| Lấy câu hỏi, nộp câu trả lời, Pass/Fail | App → **FastAPI** | Giới hạn số lần thử, chống dò đáp án |
| Xác nhận DONE | App → **FastAPI** | Đảm bảo đúng quy tắc hai bên xác nhận |
| Report, xử lý report, gỡ bài, khóa tài khoản | App/Web → **FastAPI** | Phải kiểm tra quyền Admin và ghi nhật ký |

---

## 4. Công nghệ sử dụng

### 📱 Mobile (Android)

| Mục đích | Công nghệ |
|---|---|
| Ngôn ngữ / UI | Kotlin, Jetpack Compose, Material 3 |
| Kiến trúc | MVVM (UI → ViewModel → Repository), Kotlin Coroutines + Flow |
| Điều hướng | Navigation Compose |
| Dependency Injection | Hilt (hoặc Koin) |
| Kết nối Supabase | `supabase-kt` (Auth, Postgrest, Storage, Realtime) |
| Gọi FastAPI | Retrofit + OkHttp + kotlinx.serialization |
| Hiển thị ảnh | Coil |
| Phân trang bảng tin | Paging 3 |
| Chọn ảnh | Android Photo Picker |
| Vị trí hiện tại ("Gần nhất") | Fused Location Provider |
| Lưu phiên đăng nhập | DataStore |
| Test | JUnit, MockK, Compose UI Test |

### ⚙️ Backend

| Mục đích | Công nghệ |
|---|---|
| Framework | FastAPI + Uvicorn, Pydantic v2 |
| Truy cập DB | SQLAlchemy 2.0 (async) + driver PostgreSQL, kết nối qua pooler của Supabase |
| Xác thực | Kiểm tra JWT của Supabase bằng JWKS (PyJWT) |
| Giới hạn tốc độ | slowapi |
| Gửi email (quên mật khẩu) | SMTP riêng (Resend hoặc Gmail SMTP), vì dịch vụ email mặc định của Supabase giới hạn rất thấp |
| Test | pytest + httpx |
| Đóng gói / triển khai | Docker; Render hoặc Google Cloud Run |

### 🗄️ Database & dịch vụ

| Mục đích | Công nghệ |
|---|---|
| CSDL | Supabase PostgreSQL |
| Đăng nhập | Supabase Auth (password hash bằng bcrypt) |
| Bảo mật dữ liệu | Row Level Security (RLS) |
| Chat realtime | Supabase Realtime |
| Lưu ảnh | Supabase Storage |
| Tìm kiếm tiếng Việt không dấu | `pg_trgm` + `unaccent` |
| Tự hết hạn bài đăng | `pg_cron` |
| Migration | Supabase CLI |

### 🖥️ Admin Web

| Mục đích | Công nghệ |
|---|---|
| Framework | React + Vite + TypeScript |
| Giao diện | Tailwind CSS + shadcn/ui |
| Gọi dữ liệu | TanStack Query + TanStack Table |
| Đăng nhập | `supabase-js` |
| Triển khai | Vercel / Netlify / Cloudflare Pages |

---

## 5. Thiết kế cơ sở dữ liệu

Schema gồm **16 bảng**; toàn bộ (bảng, ràng buộc, trigger, hàm tìm kiếm, RLS, seed) nằm trong [`supabase/schema.sql`](supabase/schema.sql).

```mermaid
erDiagram
    PROFILES ||--|| USER_PRIVATE : "có (SĐT riêng tư)"
    PROFILES ||--o{ POSTS : "đăng"
    CATEGORIES ||--o{ POSTS : "phân loại"
    POSTS ||--o{ POST_IMAGES : "có"
    POSTS ||--o{ POST_TAGS : "có"
    TAGS ||--o{ POST_TAGS : "gắn"
    POSTS ||--o{ VERIFICATION_QUESTIONS : "đặt câu hỏi"
    POSTS ||--o{ CLAIMS : "nhận yêu cầu"
    PROFILES ||--o{ CLAIMS : "gửi"
    CLAIMS ||--o{ CLAIM_ANSWERS : "gồm"
    VERIFICATION_QUESTIONS ||--o{ CLAIM_ANSWERS : "trả lời"
    CLAIMS ||--o| CONVERSATIONS : "Pass → tạo chat"
    CONVERSATIONS ||--o{ MESSAGES : "chứa"
    PROFILES ||--o{ REPORTS : "báo cáo"
    PROFILES ||--o{ ADMIN_ACTIONS : "thực hiện"
    PROFILES ||--o{ NOTIFICATIONS : "nhận"
    CLAIMS ||--o{ NOTIFICATIONS : "sinh ra"

    PROFILES {
        uuid id PK
        text username UK
        text display_name
        text bio
        enum role "USER | ADMIN"
        bool is_banned
    }
    USER_PRIVATE {
        uuid user_id PK
        text phone "không công khai"
    }
    POSTS {
        uuid id PK
        enum type "LOST | FOUND"
        text title
        text description
        text location_text
        timestamptz event_time
        enum status "ACTIVE | RESOLVED | EXPIRED | ARCHIVED | REMOVED | DELETED"
        timestamptz expires_at
    }
    CLAIMS {
        uuid id PK
        enum status "SUBMITTED | PASSED | FAILED | CANCELLED | COMPLETED | CLOSED"
        timestamptz author_confirmed_at
        timestamptz claimant_confirmed_at
    }
    CONVERSATIONS {
        uuid id PK
        bool is_locked
    }
    MESSAGES {
        bigint id PK
        enum type "TEXT | IMAGE | SYSTEM"
        text content
    }
    NOTIFICATIONS {
        uuid id PK
        enum type "CLAIM_RECEIVED | CLAIM_PASSED | HANDOVER_WAITING | POST_DONE | ..."
        timestamptz read_at
    }
    REPORTS {
        uuid id PK
        enum reason "SPAM | SCAM | FALSE_INFO | MONEY_REQUEST | VIOLATION | OTHER"
        enum status "PENDING | REVIEWING | RESOLVED | DISMISSED"
    }
```

### Trạng thái bài đăng và yêu cầu xác minh

```mermaid
stateDiagram-v2
    direction LR
    state "Bài đăng (posts.status)" as P {
        [*] --> ACTIVE
        ACTIVE --> RESOLVED: hai bên xác nhận DONE
        ACTIVE --> EXPIRED: quá 30 ngày
        ACTIVE --> ARCHIVED: người đăng ẩn bài
        ARCHIVED --> ACTIVE: hiện lại
        ACTIVE --> REMOVED: admin gỡ
        ARCHIVED --> DELETED: người đăng xóa bài
    }
```

```mermaid
stateDiagram-v2
    direction LR
    [*] --> SUBMITTED: nộp câu trả lời
    SUBMITTED --> PASSED: người đăng chấm Pass
    SUBMITTED --> FAILED: người đăng chấm Fail
    PASSED --> COMPLETED: hai bên xác nhận
    SUBMITTED --> CANCELLED
    PASSED --> CANCELLED
    SUBMITTED --> CLOSED: bài đã có người nhận
    PASSED --> CLOSED: bài đã có người nhận
```

---

## 6. Bảo mật: những điểm chính

- **Password** được Supabase Auth hash (bcrypt); ứng dụng không bao giờ lưu hay ghi log password gốc.
- **Email và số điện thoại** không công khai: email nằm trong Supabase Auth, SĐT ở bảng riêng `user_private`, RLS chỉ cho chính chủ và admin đọc. Người khác chỉ thấy tên hiển thị và handle.
- **Đăng ký công khai bị tắt** ở Supabase; tài khoản chỉ được tạo qua FastAPI để kiểm tra điều kiện email/password.
- **Câu hỏi xác minh** chỉ trả về qua FastAPI, có giới hạn số lần thử để chống dò đáp án.
- **Tin nhắn** chỉ hai người trong cuộc đọc được. Admin chỉ xem chat bị report, qua FastAPI, và hành động này **được ghi log** (`admin_actions`).
- **Khóa bí mật** (`secret key`) chỉ nằm ở server FastAPI, không bao giờ đưa vào app hay web.
- **Thông báo** chỉ do hệ thống tạo (trigger trong DB), client không tự tạo hay gọi hàm tạo thông báo được.
- **Quy tắc nghiệp vụ quan trọng** (không tự claim bài của mình, DONE khi đủ hai bên, tự tạo chat khi Pass) được bảo vệ bằng **trigger trong database**, không phụ thuộc vào việc code client có đúng hay không.

---

## 7. Giao diện (thiết kế Figma)

Thiết kế nằm trong file Figma của nhóm (trang *01 - UI Design*, *02 - Components*).

| Nhóm màn hình | Nội dung |
|---|---|
| Khởi động & tài khoản | Splash, Đăng nhập, Đăng ký, Quên mật khẩu → Nhập mã → Đặt lại mật khẩu |
| Trang chủ | Lời chào, chuông thông báo, khối **Cần xử lý** (3 bộ đếm), tìm kiếm, sắp xếp Mới nhất / Gần nhất, tab Tất cả / Lost / Found, thẻ bài đăng |
| Tìm kiếm | Từ khóa, loại bài, danh mục, thời gian đăng, danh sách kết quả, trạng thái không có kết quả |
| Đăng bài | Lost / Found, tối đa 5 ảnh, tiêu đề, danh mục, tag, địa điểm, thời gian, mô tả, câu hỏi xác minh (bài Found) |
| Xác minh | Người nhận trả lời câu hỏi; người đăng duyệt danh sách yêu cầu → Từ chối / Cho phép nhắn tin |
| Nhắn tin & trao trả | Danh sách hội thoại, màn hình chat, bước **Xác nhận trao trả** với thanh tiến trình Xác minh → Chat → Trao trả → Hoàn tất |
| Bài của tôi | Đang đăng, Đã DONE, Đã ẩn (hiện lại, xóa, xem lý do bị gỡ) |
| Cá nhân | Hồ sơ, chỉnh sửa hồ sơ, đổi mật khẩu, báo cáo đã gửi, đăng xuất |
| Thông báo | Mục Mới / Trước đó, nút Đọc hết |

---

## 8. Cấu trúc repository

```
lost-and-found/
├── mobile/          # Android app (Kotlin, Jetpack Compose)
├── backend/         # FastAPI
│   ├── app/
│   │   ├── api/         # routers: auth, posts, claims, reports, admin
│   │   ├── core/        # config, security (JWT/JWKS)
│   │   ├── services/    # logic nghiệp vụ
│   │   └── db/          # kết nối, truy vấn
│   └── tests/
├── admin-web/       # React + Vite + TypeScript
├── supabase/
│   ├── schema.sql       # (hoặc migrations/0001_init.sql)
│   └── seed.sql
├── docs/            # thiết kế, API contract, báo cáo
└── README.md
```

---

## 9. Chạy thử dự án (tóm tắt)

1. **Supabase**: tạo project, chạy `supabase/schema.sql` trong SQL Editor, tắt *Allow new users to sign up*, tắt *Confirm email*, cấu hình **SMTP riêng** cho email quên mật khẩu, bucket `post-images` đã được schema tạo sẵn.
2. **Backend**: `cd backend && python -m venv .venv && pip install -r requirements.txt`, tạo `.env` (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`), chạy `uvicorn app.main:app --reload`.
3. **Mobile**: mở thư mục `mobile/` bằng Android Studio, khai báo `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `API_BASE_URL` trong `local.properties`, chạy trên máy ảo hoặc điện thoại thật.
4. **Admin web**: `cd admin-web && npm install && npm run dev`.

> Tuyệt đối **không commit** file `.env`, `local.properties` hoặc bất kỳ khóa bí mật nào lên GitHub.

---

## 10. Lộ trình

- [ ] **M0** Nền tảng: repo, Supabase, API contract, các thử nghiệm kỹ thuật rủi ro
- [ ] **M1** Tài khoản: đăng ký, đăng nhập, quên / đổi mật khẩu, hồ sơ, phân quyền
- [ ] **M2** Bài đăng: tạo bài, ảnh, tag, vị trí, bảng tin Lost/Found, tìm kiếm, bộ lọc, sắp xếp Gần nhất
- [ ] **M3** Xác minh quyền sở hữu (Verify)
- [ ] **M4** Chat realtime
- [ ] **M5** Hoàn tất trao trả (DONE), vòng đời bài đăng (Expired/Archived/ẩn/xóa) và thông báo
- [ ] **M6** Report và Admin web
- [ ] **M7** Hoàn thiện: bảo mật, hiệu năng, kiểm thử
- [ ] **M8** Phát hành, tài liệu, demo

---

## 11. Nhóm thực hiện

| Thành viên | Vai trò chính |
|---|---|
| Phạm Gia Khiêm | _(điền)_ |
| _(thành viên 2)_ | _(điền)_ |
| _(thành viên 3)_ | _(điền)_ |

Đồ án môn Lập trình thiết bị di động, Trường Đại học Giao thông Vận tải TP.HCM (UTH).
