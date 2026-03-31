# Build Checklists

> Verification checklists for each build phase. Use with `@verify-phase`.

## Phase 0: Foundation

### Structure
- [ ] Directory structure matches plan
- [ ] `.claude/rules/` has all 4 modules
- [ ] `.claude/commands/` has all 3 commands
- [ ] `docs/` has all reference docs

### Documentation
- [ ] `CLAUDE.md` is populated
- [ ] `PROGRESS.md` is created
- [ ] `README.md` has setup instructions
- [ ] `.env.example` has all vars

### Dependencies
- [ ] `requirements.txt` created
- [ ] Base dependencies listed
- [ ] Dev dependencies listed

---

## Phase 1: Core API Skeleton

### App Setup
- [ ] FastAPI app factory works
- [ ] Health endpoint responds
- [ ] Config loads from .env
- [ ] Logging outputs JSON

### Database
- [ ] PostgreSQL connection works
- [ ] SQLAlchemy async session works
- [ ] Base model with timestamps

### Docker
- [ ] `docker-compose.yml` runs
- [ ] App container boots
- [ ] DB container accessible

---

## Phase 2: Authentication

### Models
- [ ] User model created
- [ ] Migration applied

### Endpoints
- [ ] POST /auth/login works
- [ ] POST /auth/refresh works
- [ ] POST /auth/logout works
- [ ] GET /me works

### Security
- [ ] Passwords hashed with bcrypt
- [ ] JWT tokens validate
- [ ] Protected routes reject unauthenticated

---

## Phase 3: Voice Reception

### WebSocket
- [ ] WS connection accepts
- [ ] Authentication validates token
- [ ] session_start sent on connect

### Audio Flow
- [ ] Client can send audio chunks
- [ ] Server responds with audio chunks
- [ ] Transcript accumulated

### Session Management
- [ ] Sessions stored in DB
- [ ] session_end handled
- [ ] session_summary sent

### REST API
- [ ] POST /voice/sessions works
- [ ] GET /voice/sessions/{id} works
- [ ] GET /voice/sessions works

---

## Testing Checklist

### Unit Tests
- [ ] Service layer has tests
- [ ] Utility functions have tests
- [ ] All tests pass

### Integration Tests
- [ ] API endpoints have tests
- [ ] Database queries have tests
- [ ] All tests pass

### Coverage
- [ ] Overall coverage >= 80%
- [ ] Models coverage >= 90%
- [ ] Services coverage >= 85%

---

## Pre-Deploy Checklist

- [ ] All tests passing
- [ ] Migrations tested on fresh DB
- [ ] Environment variables documented
- [ ] Docker images build
- [ ] Health checks pass
- [ ] Logs are structured
- [ ] No hardcoded secrets

---

*Use these checklists with `@verify-phase` command.*
