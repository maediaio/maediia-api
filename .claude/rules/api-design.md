# API Design Rules

> Auto-loaded by Claude. Defines API patterns for the Maediia Platform.

## URL Structure

### Base Path
All API routes under: `/api/v1/`

### Resource Naming
- **Plural nouns:** `/users`, `/calls`, `/sessions`
- **Nesting:** Max 2 levels deep
  - ✅ `/users/123/calls`
  - ❌ `/users/123/calls/456/transcripts`

### HTTP Methods
| Method | Action | Idempotent |
|--------|--------|------------|
| GET | Read | ✅ |
| POST | Create | ❌ |
| PUT | Full update | ✅ |
| PATCH | Partial update | ❌ |
| DELETE | Remove | ✅ |

## Response Format

### Success (200-299)
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150
  }
}
```

### Error (400-599)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Email is required"]
    }
  }
}
```

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `UNAUTHORIZED` | 401 | Auth required |
| `FORBIDDEN` | 403 | Permission denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource already exists |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Authentication

### JWT Flow
1. `POST /api/v1/auth/login` → Access + Refresh tokens
2. Include `Authorization: Bearer <access_token>` header
3. `POST /api/v1/auth/refresh` → New access token
4. `POST /api/v1/auth/logout` → Invalidate tokens

### Token Structure
```python
# Access token (15 min expiry)
{
  "sub": "user_id",
  "type": "access",
  "exp": 1234567890
}

# Refresh token (7 day expiry)
{
  "sub": "user_id",
  "type": "refresh",
  "jti": "token_id",  # For revocation
  "exp": 1234567890
}
```

## Pagination

### Request
```
GET /api/v1/users?page=2&per_page=50
```

### Response
```json
{
  "data": [...],
  "meta": {
    "page": 2,
    "per_page": 50,
    "total": 237,
    "total_pages": 5
  },
  "links": {
    "first": "/api/v1/users?page=1",
    "prev": "/api/v1/users?page=1",
    "next": "/api/v1/users?page=3",
    "last": "/api/v1/users?page=5"
  }
}
```

## WebSocket Patterns

### Connection
```
WS /api/v1/ws/voice?token=<jwt>
```

### Message Format
```json
{
  "type": "audio_chunk",
  "payload": {
    "session_id": "uuid",
    "data": "base64_encoded_audio"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

*Enforced by: FastAPI, Pydantic schemas*
