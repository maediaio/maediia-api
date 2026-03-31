# Maediia Platform Architecture

> Full platform architecture reference. Read this for big-picture understanding.

## System Overview

The Maediia Platform is a voice-first API platform for AI-powered business reception.

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Web App    │  │  Mobile App │  │  Voice Gateway      │  │
│  │  (React)    │  │  (React Nat)│  │  (WebSocket)        │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                      API LAYER                              │
│                   (FastAPI / Python)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Auth       │  │  Voice      │  │  Business Config    │  │
│  │  Service    │  │  Service    │  │  Service            │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
┌─────────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│    PostgreSQL    │ │     Redis       │ │   Object       │
│   (Primary DB)   │ │   (Cache/Queue) │ │   Storage      │
└──────────────────┘ └─────────────────┘ └────────────────┘
```

## Service Boundaries

### Auth Service
- User registration/login
- JWT token management
- Password reset
- Session management

### Voice Service
- WebSocket session handling
- Real-time audio streaming
- STT/TTS orchestration
- Call state management

### Business Config Service
- Business profile management
- Voice persona settings
- Script customization
- Integration settings

## Data Flow

### Voice Call Flow
```
1. Client → POST /api/v1/voice/sessions (create session)
2. Client → WS /api/v1/ws/voice?token=xyz (connect)
3. Client → Send audio chunk (base64 encoded PCM16)
4. Server → Forward to STT service
5. Server → Process intent → Generate response
6. Server → TTS → Stream audio back
7. Server → Log interaction
```

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastAPI | Async-native, OpenAPI auto-gen |
| Database | PostgreSQL | ACID compliance, JSON support |
| Cache | Redis | Sessions, rate limiting, pub/sub |
| ORM | SQLAlchemy 2.0 | Async support, mature ecosystem |
| Auth | JWT | Stateless, scalable |
| Deploy | Docker | Consistent environments |

## Scaling Strategy

### Phase 1: Single Instance
- Docker Compose on single VPS
- PostgreSQL + Redis containers
- ~100 concurrent voice sessions

### Phase 2: Horizontal Scaling
- Kubernetes cluster
- Separate voice gateway nodes
- Read replicas for DB

### Phase 3: Global Distribution
- Multi-region deployment
- Edge caching
- Regional voice gateways

## Security Model

- All traffic over TLS 1.3
- JWT access tokens (15 min expiry)
- Refresh tokens with rotation
- Rate limiting per IP + user
- Input validation on all endpoints

---

*Last updated: 2026-03-31*
