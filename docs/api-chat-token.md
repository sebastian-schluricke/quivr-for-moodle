# Chat Token API Documentation

## Overview

This document describes a new API endpoint that allows users to generate temporary JWT tokens for accessing the chat stream endpoint with a specific brain. The token is valid for 30 minutes and can only be used for the specified brain.

## New Endpoint

### Generate Chat Token

```
POST /api-key/chat-token
```

Generates a temporary JWT token for accessing chat with a specific brain.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| brain_id | UUID | Yes | The ID of the brain to access |
| Authorization | Header | Yes | API key in the format "Bearer {api_key}" |

#### Response

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800
}
```

| Field | Type | Description |
|-------|------|-------------|
| token | string | JWT token to use for authentication |
| expires_in | integer | Token expiration time in seconds (30 minutes = 1800 seconds) |

#### Example

```bash
curl -X POST "https://api.quivr.app/api-key/chat-token?brain_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer your_api_key_here"
```

## Using the Token

The generated token can be used to access the chat stream endpoint:

```
POST /chat/{chat_id}/question/stream
```

Include the token in the Authorization header:

```bash
curl -X POST "https://api.quivr.app/chat/550e8400-e29b-41d4-a716-446655440000/question/stream?brain_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Quivr?"}'
```

## Testing

To test the new functionality:

1. Generate an API key using the existing `/api-key` endpoint
2. Use the API key to make a request to the new `/api-key/chat-token` endpoint with a valid brain_id
3. Use the returned JWT token to make a request to the `/chat/{chat_id}/question/stream` endpoint
4. Verify that the request is successful and returns a streaming response

## Implementation Details

The token contains the following information:
- User ID (sub)
- User email
- Brain ID
- Expiration time (30 minutes from creation)

This allows the AuthBearer middleware to authenticate the user and validate their access to the specified brain.