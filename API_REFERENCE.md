# API Reference - SIBERINDO BTS GUI

Complete API endpoint documentation for SIBERINDO BTS GUI v2.0.0

## Base URL

```
http://localhost:5000
```

## Authentication

### Login Endpoint

**Endpoint**: `POST /auth/login`

Login with username and password.

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password123"
```

**Request Body**:
```
username=admin&password=password123
```

**Response** (302 Redirect):
```
Location: /dashboard/dashboard
```

---

### Logout

**Endpoint**: `GET /auth/logout`

```bash
curl -X GET http://localhost:5000/auth/logout
```

**Response** (302 Redirect):
```
Location: /auth/login
```

---

## Dashboard Endpoints

### Dashboard View

**Endpoint**: `GET /dashboard/dashboard`

Renders dashboard HTML page with system stats.

```bash
curl -X GET http://localhost:5000/dashboard/dashboard
```

**Response**: HTML Page (200 OK)

---

### Refresh Dashboard Stats

**Endpoint**: `GET /dashboard/api/dashboard/refresh`

Get latest system statistics (JSON).

```bash
curl -X GET http://localhost:5000/dashboard/api/dashboard/refresh \
  -H "Accept: application/json"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "cpu_percent": 25.4,
    "memory_percent": 42.1,
    "disk_percent": 65.3,
    "uptime_hours": 72.5,
    "services_running": 6,
    "health_score": 92
  },
  "timestamp": "2024-11-26T12:00:00"
}
```

---

### Detect HackRF Device

**Endpoint**: `GET /dashboard/api/hackrf/detect`

Detect HackRF device availability.

```bash
curl -X GET http://localhost:5000/dashboard/api/hackrf/detect
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "detected": true,
    "device_id": "hackrf_one",
    "serial": "0000000000000000"
  }
}
```

---

## Subscriber Management

### Get Subscribers List

**Endpoint**: `GET /subscribers/subscribers`

Renders HTML page with subscribers.

```bash
curl -X GET http://localhost:5000/subscribers/subscribers
```

**Response**: HTML Page (200 OK)

---

### API: Get Subscribers

**Endpoint**: `GET /subscribers/api/subscribers`

Get subscribers as JSON with pagination.

**Query Parameters**:
- `limit` (optional, default: 10): Results per page
- `offset` (optional, default: 0): Starting position

```bash
curl -X GET "http://localhost:5000/subscribers/api/subscribers?limit=20&offset=0"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "imsi": "310260000000000",
      "msisdn": "14155552671",
      "name": "John Doe",
      "location": "New York",
      "status": "active",
      "network": "GSM",
      "last_seen": 1732617600
    }
  ],
  "pagination": {
    "total": 100,
    "page": 0,
    "limit": 20
  }
}
```

---

### API: Subscriber Count

**Endpoint**: `GET /subscribers/api/subscribers/count`

Get total subscriber count.

```bash
curl -X GET http://localhost:5000/subscribers/api/subscribers/count
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total_subscribers": 150,
    "active": 145,
    "inactive": 5
  }
}
```

---

### API: Subscriber Statistics

**Endpoint**: `GET /subscribers/api/subscribers/stats`

Get subscriber statistics.

```bash
curl -X GET http://localhost:5000/subscribers/api/subscribers/stats
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total_subscribers": 150,
    "active_subscribers": 145,
    "inactive_subscribers": 5,
    "gsm_subscribers": 120,
    "umts_subscribers": 30,
    "networks": {
      "GSM": 120,
      "UMTS": 30
    }
  }
}
```

---

## SMS Management

### Send SMS

**Endpoint**: `POST /sms/api/sms/send`

Send single SMS message.

```bash
curl -X POST http://localhost:5000/sms/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "msisdn": "14155552671",
    "message": "Hello World",
    "type": "sms"
  }'
```

**Request Body**:
```json
{
  "msisdn": "14155552671",
  "message": "Hello World",
  "type": "sms"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": 42,
    "msisdn": "14155552671",
    "message": "Hello World",
    "status": "sent",
    "timestamp": "2024-11-26T12:00:00"
  }
}
```

---

### Send Silent SMS

**Endpoint**: `POST /sms/api/sms/send`

Send SMS without notification indicator.

```bash
curl -X POST http://localhost:5000/sms/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "msisdn": "14155552671",
    "message": "Silent message",
    "type": "silent_sms"
  }'
```

---

### Batch Send SMS

**Endpoint**: `POST /sms/api/sms/batch`

Send SMS to multiple recipients.

```bash
curl -X POST http://localhost:5000/sms/api/sms/batch \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      "14155552671",
      "14155552672",
      "14155552673"
    ],
    "message": "Batch message"
  }'
```

**Request Body**:
```json
{
  "recipients": ["14155552671", "14155552672"],
  "message": "Hello All",
  "type": "sms"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "sent": 2,
    "failed": 0,
    "messages": [
      {
        "msisdn": "14155552671",
        "status": "sent"
      },
      {
        "msisdn": "14155552672",
        "status": "sent"
      }
    ]
  }
}
```

---

### SMS History

**Endpoint**: `GET /sms/api/sms/history`

Get SMS sending history.

**Query Parameters**:
- `limit` (optional, default: 50): Results per page
- `offset` (optional, default: 0): Starting position

```bash
curl -X GET "http://localhost:5000/sms/api/sms/history?limit=20&offset=0"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "msisdn": "14155552671",
      "message": "Hello World",
      "status": "sent",
      "timestamp": "2024-11-26T12:00:00",
      "delivered_at": "2024-11-26T12:00:05"
    }
  ],
  "pagination": {
    "total": 500,
    "page": 0,
    "limit": 20
  }
}
```

---

## BTS Scanner

### Start Scan

**Endpoint**: `POST /scanner/api/bts_scan/start`

Start frequency band scan.

```bash
curl -X POST http://localhost:5000/scanner/api/bts_scan/start \
  -H "Content-Type: application/json" \
  -d '{
    "bands": ["GSM900", "GSM1800"],
    "duration": 60
  }'
```

**Request Body**:
```json
{
  "bands": ["GSM900", "GSM1800"],
  "duration": 60
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_001",
    "status": "running",
    "bands": ["GSM900", "GSM1800"],
    "duration": 60,
    "started_at": "2024-11-26T12:00:00"
  }
}
```

---

### Stop Scan

**Endpoint**: `POST /scanner/api/bts_scan/stop`

Stop active scan.

```bash
curl -X POST http://localhost:5000/scanner/api/bts_scan/stop \
  -H "Content-Type: application/json" \
  -d '{"scan_id": "scan_001"}'
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_001",
    "status": "stopped",
    "results_count": 150
  }
}
```

---

### Scan Status

**Endpoint**: `GET /scanner/api/bts_scan/status`

Get current scan status.

```bash
curl -X GET "http://localhost:5000/scanner/api/bts_scan/status?scan_id=scan_001"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_001",
    "status": "running",
    "progress": 75,
    "results_found": 112
  }
}
```

---

### Scan Results

**Endpoint**: `GET /scanner/api/bts_scan/results`

Get scan results.

```bash
curl -X GET "http://localhost:5000/scanner/api/bts_scan/results?scan_id=scan_001"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_001",
    "results": [
      {
        "arfcn": 0,
        "band": "GSM900",
        "signal_strength": -75,
        "quality": "Good",
        "mcc": "310",
        "mnc": "260"
      }
    ]
  }
}
```

---

## Health Check

### Health Endpoint

**Endpoint**: `GET /health`

Simple health check endpoint.

```bash
curl -X GET http://localhost:5000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2024-11-26T12:00:00"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "message": "Error description",
  "error_code": 400,
  "timestamp": "2024-11-26T12:00:00"
}
```

### Common Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 302 | Redirect - Authentication required |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Not authenticated |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Server Error - Internal error |

---

## Validation Rules

### IMSI (International Mobile Subscriber Identity)

- Format: 15 digits
- Pattern: `^[0-9]{15}$`
- Example: `310260000000000`

### MSISDN (Mobile Number)

- Format: 10-15 digits
- Pattern: `^[0-9]{10,15}$`
- Example: `14155552671`

### Email

- Format: Standard email
- Pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Example: `user@example.com`

---

## Rate Limiting

### Limits

- **Default**: 100 requests per minute per IP
- **SMS Endpoints**: 50 requests per minute
- **Admin Endpoints**: 10 requests per minute

### Rate Limit Response

```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error_code": 429,
  "retry_after": 60
}
```

---

## Pagination

### Pagination Query Parameters

- `limit`: Items per page (default: 10, max: 100)
- `offset`: Starting position (default: 0)
- `page`: Page number (alternative to offset)

### Pagination Response

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 500,
    "limit": 10,
    "offset": 0,
    "page": 0,
    "pages": 50
  }
}
```

---

## Examples

### Complete cURL Workflow

```bash
# 1. Login
curl -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=password123" \
  -c cookies.txt

# 2. Get subscribers
curl -X GET "http://localhost:5000/subscribers/api/subscribers?limit=10" \
  -b cookies.txt

# 3. Send SMS
curl -X POST http://localhost:5000/sms/api/sms/send \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "msisdn": "14155552671",
    "message": "Test message"
  }'

# 4. Get SMS history
curl -X GET "http://localhost:5000/sms/api/sms/history?limit=20" \
  -b cookies.txt

# 5. Logout
curl -X GET http://localhost:5000/auth/logout \
  -b cookies.txt
```

---

## API Documentation

- For more details, see README.md
- For setup information, see SETUP_GUIDE.md
- For version history, see CHANGELOG.md

---

**API Version**: 2.0.0  
**Last Updated**: November 26, 2024  
**Status**: Production Ready
