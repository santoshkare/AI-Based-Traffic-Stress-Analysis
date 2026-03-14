# SafeDrive.ai - API Documentation

## Overview

SafeDrive.ai Flask server provides REST APIs for authentication, event logging, and system statistics.

**Base URL:** `http://localhost:5000`

---

## Authentication Endpoints

### POST `/api/login`

Authenticate a user with email and password.

**Request:**

```json
{
  "email": "demo@test.com",
  "password": "demo1234"
}
```

**Success Response (200):**

```json
{
  "ok": true,
  "name": "Demo Driver"
}
```

**Error Responses:**

- `400` - Missing or invalid email/password format
- `401` - Invalid credentials
- `429` - Too many login attempts (try again in 5 minutes)
- `500` - Server error

---

### POST `/api/register`

Register a new user account.

**Request:**

```json
{
  "email": "newuser@example.com",
  "name": "John Doe",
  "password": "securepass123"
}
```

**Success Response (200):**

```json
{
  "ok": true,
  "name": "John Doe"
}
```

**Error Responses:**

- `400` - Missing fields or weak password (min 8 chars)
- `409` - Email already registered
- `500` - Server error

**Password Requirements:**

- Minimum 8 characters
- Should contain mix of letters and numbers for security

---

### POST `/api/logout`

Logout the current user.

**Request:** No body required

**Success Response (200):**

```json
{
  "ok": true
}
```

---

## Data Endpoints (Requires Authentication)

### POST `/api/log_event`

Log a driver event with risk score.

**Authentication:** Required (user must be logged in)

**Request:**

```json
{
  "type": "drowsiness",
  "score": 7.5
}
```

**Parameters:**

- `type` (string) - Event type (drowsiness, emotion, stress, visibility, child_detected, etc.)
- `score` (number) - Risk score 0-10

**Success Response (200):**

```json
{
  "ok": true
}
```

**Error Responses:**

- `400` - Missing event type or invalid score
- `401` - Not authenticated
- `500` - Server error

---

### GET `/api/stats`

Get system statistics.

**Authentication:** Required (user must be logged in)

**Success Response (200):**

```json
{
  "ok": true,
  "events": 42,
  "users": 3,
  "timestamp": "2024-03-14T10:30:45.123456"
}
```

**Error Responses:**

- `401` - Not authenticated
- `500` - Server error

---

## Default Credentials

Test the API with these default accounts:

| Email              | Password |
| ------------------ | -------- |
| admin@safedrive.ai | admin123 |
| demo@test.com      | demo1234 |

Or use "Continue as Guest" for limited functionality.

---

## Error Codes

| Code | Meaning                             |
| ---- | ----------------------------------- |
| 200  | Success                             |
| 400  | Bad request (validation error)      |
| 401  | Unauthorized (not logged in)        |
| 404  | Endpoint not found                  |
| 409  | Conflict (email already registered) |
| 429  | Too many requests (rate limited)    |
| 500  | Internal server error               |

---

## Session Management

- Sessions are stored server-side and identified by cookies
- Session timeout: 1 hour of inactivity
- Cookies are HttpOnly and Secure (when HTTPS is used)
- CORS is enabled for cross-origin requests

---

## Usage Example (cURL)

```bash
# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo1234"}' \
  -c cookies.txt

# Log an event (with saved session)
curl -X POST http://localhost:5000/api/log_event \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"type":"drowsiness","score":6.5}'

# Get stats
curl -X GET http://localhost:5000/api/stats \
  -b cookies.txt

# Logout
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

---

## Rate Limiting

After 5 failed login attempts, the account is locked for 5 minutes to prevent brute force attacks.

---

## Security Best Practices

1. **Never** commit sensitive credentials to version control
2. Use environment variables for SECRET_KEY in production
3. Enable HTTPS in production
4. Implement additional authentication (2FA) for production
5. Monitor `safedrive.log` for suspicious activity
6. Regularly update dependencies: `pip install --upgrade -r requirements.txt`
