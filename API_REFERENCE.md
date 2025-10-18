# Scalper Bot - API Reference

Complete API reference for the Scalper Bot backend.

## Base URL

```
Development: http://localhost:8000
Production:  https://api.scalperbot.com
```

## API Version

Current version: **v1**

All endpoints are prefixed with `/api/v1`

## Authentication

**Current**: No authentication required (development mode)

**Future**: JWT Bearer token authentication

```http
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting

**Current**: No rate limiting (development mode)

**Future**: 60 requests per minute per IP

## Content Type

All requests and responses use JSON:

```http
Content-Type: application/json
Accept: application/json
```

---

## Bots API

### Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/bots/` | List all bots |
| POST | `/api/v1/bots/` | Create new bot |
| GET | `/api/v1/bots/{id}` | Get bot by ID |
| PUT | `/api/v1/bots/{id}` | Update bot |
| DELETE | `/api/v1/bots/{id}` | Delete bot |
| POST | `/api/v1/bots/{id}/start` | Start bot |
| POST | `/api/v1/bots/{id}/stop` | Stop bot |
| POST | `/api/v1/bots/{id}/toggle` | Toggle bot status |
| POST | `/api/v1/bots/stop-all` | Emergency stop all |
| GET | `/api/v1/bots/statistics/summary` | Get statistics |

---

### List All Bots

Get a list of all bots with optional filtering and pagination.

**Endpoint**
```
GET /api/v1/bots/
```

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |
| status | string | No | null | Filter by status (ACTIVE, STOPPED) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/bots/?skip=0&limit=10&status=ACTIVE"
```

**Success Response (200 OK)**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000.50,
    "sell_price": 46000.00,
    "trailing_percent": 1.5,
    "infinite_loop": true,
    "status": "ACTIVE",
    "pnl": 125.50,
    "total_trades": 10,
    "last_fill_time": "2024-01-01T10:30:00Z",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:30:00Z",
    "config": null
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "ticker": "ETH/USDT",
    "exchange": "Binance",
    "first_order": "SELL",
    "quantity": 0.1,
    "buy_price": 2800.00,
    "sell_price": 2900.00,
    "trailing_percent": null,
    "infinite_loop": false,
    "status": "ACTIVE",
    "pnl": -25.30,
    "total_trades": 5,
    "last_fill_time": "2024-01-01T11:00:00Z",
    "created_at": "2024-01-01T09:00:00Z",
    "updated_at": "2024-01-01T11:00:00Z",
    "config": null
  }
]
```

---

### Create Bot

Create a new bot with specified configuration.

**Endpoint**
```
POST /api/v1/bots/
```

**Request Body**

```json
{
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 45000.50,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true
}
```

**Field Specifications**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| ticker | string | Yes | Format: XXX/XXX |
| exchange | string | Yes | Enum: "Binance", "CoinDCX F" |
| first_order | string | Yes | Enum: "BUY", "SELL" |
| quantity | number | Yes | > 0 |
| buy_price | number | Yes | > 0 |
| sell_price | number | Yes | > buy_price |
| trailing_percent | number | No | 0.1 - 100 |
| infinite_loop | boolean | No | Default: false |

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/bots/" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000.50,
    "sell_price": 46000.00,
    "trailing_percent": 1.5,
    "infinite_loop": true
  }'
```

**Success Response (201 Created)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 45000.50,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true,
  "status": "ACTIVE",
  "pnl": 0.0,
  "total_trades": 0,
  "last_fill_time": null,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z",
  "config": null
}
```

**Error Response (422 Unprocessable Entity)**

```json
{
  "detail": [
    {
      "loc": ["body", "buy_price"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    },
    {
      "loc": ["body", "sell_price"],
      "msg": "sell_price must be greater than buy_price",
      "type": "value_error"
    }
  ]
}
```

---

### Get Bot by ID

Retrieve details of a specific bot.

**Endpoint**
```
GET /api/v1/bots/{bot_id}
```

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bot_id | UUID | Yes | Bot identifier |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000"
```

**Success Response (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.01,
  "buy_price": 45000.50,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true,
  "status": "ACTIVE",
  "pnl": 125.50,
  "total_trades": 10,
  "last_fill_time": "2024-01-01T10:30:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:30:00Z",
  "config": null
}
```

**Error Response (404 Not Found)**

```json
{
  "detail": "Bot not found"
}
```

---

### Update Bot

Update an existing bot's configuration.

**Endpoint**
```
PUT /api/v1/bots/{bot_id}
```

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bot_id | UUID | Yes | Bot identifier |

**Request Body** (all fields optional)

```json
{
  "quantity": 0.02,
  "buy_price": 44000.00,
  "sell_price": 45500.00,
  "trailing_percent": 2.0
}
```

**Example Request**

```bash
curl -X PUT "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 0.02,
    "buy_price": 44000.00
  }'
```

**Success Response (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticker": "BTC/USDT",
  "exchange": "Binance",
  "first_order": "BUY",
  "quantity": 0.02,
  "buy_price": 44000.00,
  "sell_price": 46000.00,
  "trailing_percent": 1.5,
  "infinite_loop": true,
  "status": "ACTIVE",
  "pnl": 125.50,
  "total_trades": 10,
  "last_fill_time": "2024-01-01T10:30:00Z",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "config": null
}
```

---

### Delete Bot

Delete a bot permanently.

**Endpoint**
```
DELETE /api/v1/bots/{bot_id}
```

**Path Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bot_id | UUID | Yes | Bot identifier |

**Example Request**

```bash
curl -X DELETE "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000"
```

**Success Response (204 No Content)**

No response body.

**Error Response (404 Not Found)**

```json
{
  "detail": "Bot not found"
}
```

---

### Start Bot

Start a stopped bot.

**Endpoint**
```
POST /api/v1/bots/{bot_id}/start
```

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000/start"
```

**Success Response (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ACTIVE",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

---

### Stop Bot

Stop an active bot.

**Endpoint**
```
POST /api/v1/bots/{bot_id}/stop
```

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000/stop"
```

**Success Response (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "STOPPED",
  "updated_at": "2024-01-01T14:00:00Z"
}
```

---

### Toggle Bot Status

Toggle bot between ACTIVE and STOPPED states.

**Endpoint**
```
POST /api/v1/bots/{bot_id}/toggle
```

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/bots/550e8400-e29b-41d4-a716-446655440000/toggle"
```

**Success Response (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "STOPPED",
  "updated_at": "2024-01-01T15:00:00Z"
}
```

---

### Emergency Stop All

Stop all active bots immediately.

**Endpoint**
```
POST /api/v1/bots/stop-all
```

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/bots/stop-all"
```

**Success Response (200 OK)**

```json
{
  "message": "Stopped 5 bots",
  "count": 5
}
```

---

### Get Statistics

Get aggregated statistics for all bots.

**Endpoint**
```
GET /api/v1/bots/statistics/summary
```

**Example Request**

```bash
curl "http://localhost:8000/api/v1/bots/statistics/summary"
```

**Success Response (200 OK)**

```json
{
  "total_bots": 10,
  "active_bots": 7,
  "stopped_bots": 3,
  "total_pnl": 1250.75,
  "total_trades": 156
}
```

---

## Activity Logs API

### Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/logs/` | List activity logs |
| POST | `/api/v1/logs/` | Create log entry |
| DELETE | `/api/v1/logs/` | Clear all logs |
| GET | `/api/v1/logs/count` | Get log counts |

---

### List Activity Logs

Get activity logs with optional filtering and pagination.

**Endpoint**
```
GET /api/v1/logs/
```

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |
| level | string | No | null | Filter by level |
| bot_id | UUID | No | null | Filter by bot ID |

**Log Levels**: INFO, SUCCESS, WARNING, ERROR, TELEGRAM

**Example Request**

```bash
curl "http://localhost:8000/api/v1/logs/?level=ERROR&limit=20"
```

**Success Response (200 OK)**

```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "bot_id": "550e8400-e29b-41d4-a716-446655440000",
    "level": "SUCCESS",
    "message": "Bot started for BTC/USDT on Binance",
    "timestamp": "2024-01-01T10:00:00Z",
    "extra_data": null
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "bot_id": null,
    "level": "ERROR",
    "message": "Emergency stop - All bots stopped",
    "timestamp": "2024-01-01T10:05:00Z",
    "extra_data": {
      "reason": "manual",
      "stopped_count": 5
    }
  }
]
```

---

### Create Activity Log

Create a new log entry.

**Endpoint**
```
POST /api/v1/logs/
```

**Request Body**

```json
{
  "bot_id": "550e8400-e29b-41d4-a716-446655440000",
  "level": "INFO",
  "message": "Custom log message",
  "extra_data": {
    "custom_field": "custom_value"
  }
}
```

**Field Specifications**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| bot_id | UUID | No | Must be valid bot ID |
| level | string | Yes | Enum: INFO, SUCCESS, WARNING, ERROR, TELEGRAM |
| message | string | Yes | Max 500 characters |
| extra_data | object | No | Any JSON object |

**Example Request**

```bash
curl -X POST "http://localhost:8000/api/v1/logs/" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "INFO",
    "message": "System check completed"
  }'
```

**Success Response (201 Created)**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "bot_id": null,
  "level": "INFO",
  "message": "System check completed",
  "timestamp": "2024-01-01T16:00:00Z",
  "extra_data": null
}
```

---

### Clear All Logs

Delete all activity logs.

**Endpoint**
```
DELETE /api/v1/logs/
```

**Example Request**

```bash
curl -X DELETE "http://localhost:8000/api/v1/logs/"
```

**Success Response (200 OK)**

```json
{
  "message": "All logs cleared",
  "count": 150
}
```

---

### Get Log Counts

Get count of logs by level.

**Endpoint**
```
GET /api/v1/logs/count
```

**Example Request**

```bash
curl "http://localhost:8000/api/v1/logs/count"
```

**Success Response (200 OK)**

```json
{
  "INFO": 50,
  "SUCCESS": 30,
  "WARNING": 15,
  "ERROR": 5,
  "TELEGRAM": 10,
  "total": 110
}
```

---

## Data Models

### Bot Model

```typescript
{
  id: string (UUID),
  ticker: string,
  exchange: "Binance" | "CoinDCX F",
  first_order: "BUY" | "SELL",
  quantity: number,
  buy_price: number,
  sell_price: number,
  trailing_percent: number | null,
  infinite_loop: boolean,
  status: "ACTIVE" | "STOPPED" | "ERROR",
  pnl: number,
  total_trades: number,
  last_fill_time: string (ISO 8601) | null,
  created_at: string (ISO 8601),
  updated_at: string (ISO 8601),
  config: object | null
}
```

### Activity Log Model

```typescript
{
  id: string (UUID),
  bot_id: string (UUID) | null,
  level: "INFO" | "SUCCESS" | "WARNING" | "ERROR" | "TELEGRAM",
  message: string,
  timestamp: string (ISO 8601),
  extra_data: object | null
}
```

### Statistics Model

```typescript
{
  total_bots: number,
  active_bots: number,
  stopped_bots: number,
  total_pnl: number,
  total_trades: number
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "request_id": "req_123456",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no response body |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## Pagination

All list endpoints support pagination via query parameters:

- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

**Example**:
```bash
# Get second page with 20 items per page
curl "http://localhost:8000/api/v1/bots/?skip=20&limit=20"
```

---

## Filtering

List endpoints support filtering via query parameters:

**Bots**:
- `status`: Filter by bot status (ACTIVE, STOPPED)

**Logs**:
- `level`: Filter by log level (INFO, SUCCESS, WARNING, ERROR, TELEGRAM)
- `bot_id`: Filter by bot ID

**Example**:
```bash
# Get only active bots
curl "http://localhost:8000/api/v1/bots/?status=ACTIVE"

# Get error logs only
curl "http://localhost:8000/api/v1/logs/?level=ERROR"
```

---

## Timestamps

All timestamps are in ISO 8601 format with timezone:

```
2024-01-01T10:30:00Z
```

To parse in JavaScript:
```javascript
new Date("2024-01-01T10:30:00Z")
```

To format for display:
```javascript
new Date(timestamp).toLocaleString()
```

---

## Testing with curl

### Create and manage a bot

```bash
# 1. Create bot
BOT_ID=$(curl -s -X POST "http://localhost:8000/api/v1/bots/" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "BTC/USDT",
    "exchange": "Binance",
    "first_order": "BUY",
    "quantity": 0.01,
    "buy_price": 45000,
    "sell_price": 46000,
    "trailing_percent": 1.5,
    "infinite_loop": true
  }' | jq -r '.id')

echo "Created bot: $BOT_ID"

# 2. Get bot details
curl "http://localhost:8000/api/v1/bots/$BOT_ID"

# 3. Update bot
curl -X PUT "http://localhost:8000/api/v1/bots/$BOT_ID" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 0.02}'

# 4. Stop bot
curl -X POST "http://localhost:8000/api/v1/bots/$BOT_ID/stop"

# 5. Start bot
curl -X POST "http://localhost:8000/api/v1/bots/$BOT_ID/start"

# 6. Delete bot
curl -X DELETE "http://localhost:8000/api/v1/bots/$BOT_ID"
```

---

## Interactive Documentation

For interactive testing and full schema documentation, visit:

**http://localhost:8000/docs** (Swagger UI)
**http://localhost:8000/redoc** (ReDoc)

---

**Version**: 1.0.0
**Last Updated**: 2024-01-01
**Maintained by**: Anuj Saini (@anujsainicse)
