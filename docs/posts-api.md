# Posts API Specification

## 1. Create Post

**Endpoint:** `POST /posts`

**Authentication:** Required

**Request Body:**
```json
{
  "type": "LOST",
  "title": "Lost black wallet",
  "description": "Black wallet containing student card",
  "category": "WALLET",
  "image_url": "https://example.com/image.jpg",
  "location": "University campus",
  "event_time": "2026-10-18T08:00:00"
}
```

**Rules:**
- The user must be logged in.
- `type` must be `LOST` or `FOUND`.
- `title` is required.
- `user_id` is obtained from the authenticated user, not from the request body.
- `status` defaults to `ACTIVE`.
- `event_time` represents when the item was lost or found.

**Success Response:** `201 Created`

```json
{
  "message": "Post created successfully",
  "post_id": 1
}
```

## 2. Get Posts

**Endpoint:** `GET /posts`

**Authentication:** Not required

**Query Parameters:**
- `type`: `LOST` or `FOUND` (optional)
- `category`: Filter by category (optional)
- `keyword`: Search title and description (optional)

**Success Response:** `200 OK`

Returns a list of active posts matching the filters.

## 3. Get Post Details

**Endpoint:** `GET /posts/{post_id}`

**Authentication:** Not required

**Success Response:** `200 OK`

Returns post details, including title, description, category, image, location, event time, status, and poster ID.

**Error Response:** `404 Not Found` if the post does not exist or is unavailable.

## 4. Update Post

**Endpoint:** `PUT /posts/{post_id}`

**Authentication:** Required

**Rules:**
- Only the post owner can update their post.
- The backend validates all updated fields.

**Success Response:** `200 OK`

```json
{
  "message": "Post updated successfully"
}
```

## 5. Delete Post

**Endpoint:** `DELETE /posts/{post_id}`

**Authentication:** Required

**Rules:**
- Only the post owner can delete their post.
- The backend must verify ownership.

**Success Response:** `200 OK`

```json
{
  "message": "Post deleted successfully"
}
```

## 6. Security Rules

- Only authenticated users can create, update, or delete posts.
- Users cannot modify other users' posts.
- Public post responses must not expose phone numbers or other private contact information.
- The backend validates all inputs and permissions.
