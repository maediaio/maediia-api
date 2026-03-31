# Voice Reception Contract

> API contract for voice reception functionality. Defines WebSocket protocol and endpoints.

## Overview

The Voice Reception API provides real-time AI-powered phone reception through WebSocket connections.

## WebSocket Connection

### Endpoint
```
WS /api/v1/ws/voice
```

### Authentication
Pass JWT access token as query parameter:
```
/api/v1/ws/voice?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Connection Lifecycle

```
┌─────────┐                              ┌─────────┐
│ Client  │                              │ Server  │
└────┬────┘                              └────┬────┘
     │                                         │
     │── CONNECT ─────────────────────────────>│
     │                                         │
     │<─ session_start (session_id, config) ───│
     │                                         │
     │── audio_chunk (caller audio) ──────────>│
     │                                         │
     │<─ audio_chunk (AI response) ────────────│
     │                                         │
     │── audio_chunk (caller audio) ──────────>│
     │<─ audio_chunk (AI response) ────────────│
     │       [continue...]                     │
     │                                         │
     │── session_end (reason) ────────────────>│
     │<─ session_summary (transcript, actions) ─│
     │                                         │
     │── DISCONNECT ──────────────────────────>│
```

## Message Protocol

### Client → Server

#### audio_chunk
```json
{
  "type": "audio_chunk",
  "payload": {
    "data": "base64_encoded_pcm16_audio",
    "timestamp": "2024-01-15T10:30:00.123Z"
  }
}
```

#### session_end
```json
{
  "type": "session_end",
  "payload": {
    "reason": "completed|transferred|voicemail|error"
  }
}
```

### Server → Client

#### session_start
```json
{
  "type": "session_start",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": {
      "voice": "alloy|echo|fable|onyx|nova|shimmer",
      "language": "en-US",
      "greeting": "Hello, thanks for calling..."
    }
  }
}
```

#### audio_chunk
```json
{
  "type": "audio_chunk",
  "payload": {
    "data": "base64_encoded_pcm16_audio",
    "is_interruptible": true,
    "timestamp": "2024-01-15T10:30:00.456Z"
  }
}
```

#### session_summary
```json
{
  "type": "session_summary",
  "payload": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "duration_seconds": 245,
    "transcript": [
      {"speaker": "ai", "text": "Hello, how can I help?"},
      {"speaker": "caller", "text": "I need to book an appointment."}
    ],
    "actions": [
      {"type": "appointment_booked", "details": {...}}
    ],
    "recording_url": "https://storage.maediia.com/recordings/abc.mp3"
  }
}
```

## Error Messages

```json
{
  "type": "error",
  "payload": {
    "code": "STT_ERROR|LLM_ERROR|TTS_ERROR|RATE_LIMITED",
    "message": "Description of error",
    "recoverable": true
  }
}
```

## REST Endpoints

### Create Session
```
POST /api/v1/voice/sessions
Authorization: Bearer <token>

Response 201:
{
  "session_id": "uuid",
  "ws_url": "wss://api.maediia.com/api/v1/ws/voice?token=xyz"
}
```

### Get Session
```
GET /api/v1/voice/sessions/{session_id}
Authorization: Bearer <token>

Response 200:
{
  "session_id": "uuid",
  "status": "active|ended|error",
  "started_at": "2024-01-15T10:30:00Z",
  "ended_at": "2024-01-15T10:34:05Z",
  "transcript_url": "..."
}
```

### List Sessions
```
GET /api/v1/voice/sessions?business_id=xyz&limit=20
Authorization: Bearer <token>
```

## Audio Specifications

- **Format:** PCM 16-bit signed little-endian
- **Sample Rate:** 16kHz (input), 24kHz (output)
- **Channels:** Mono
- **Chunk Size:** 20ms (320 samples @ 16kHz)
- **Encoding:** Base64 string

---

*Contract Version: 1.0*  
*Last updated: 2026-03-31*
