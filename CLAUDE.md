# CLAUDE.md

## Project Overview

Production-ready Python Flask template following a **layered MVC+ architecture** (Controller -> Service -> DAO -> Model) for building RESTful APIs. Features JWT authentication with refresh tokens, request validation, rate limiting, file upload, health checks, and Docker deployment.

## Development Commands

```bash
# Install dependencies
make install          # production deps
make install-dev      # production + dev deps (pytest, black, flake8)

# Run the development server (http://0.0.0.0:3000)
make run

# Run tests
make test             # pytest with coverage

# Lint & format
make lint             # check style
make format           # auto-format

# Docker
make docker-up        # start app + mysql + redis
make docker-down      # stop all

# Database migrations
make migrate          # apply migrations
make migrate-init     # first-time setup

# API docs
# http://127.0.0.1:3000/apidocs/
```

## Architecture

### Layer Structure
- **Controller** (`app/api/controller/`): HTTP handlers, validation, rate limiting
- **Service** (`app/api/service/`): Business logic
- **DAO** (`app/api/dao/`): Database operations (SQLAlchemy ORM)
- **Model** (`app/api/models/`): Table definitions

### Key Patterns
- **Application Factory**: `app/__init__.py` exports `create_app(config_name)`
- **Config Validation**: Lazy validation in `create_app()`, not at import time
- **Response Format**: `Result.success(data)` / `Result.failed(code, msg)` / `Result.page(...)`
- **Auth**: JWT with access + refresh tokens, `@token_required` decorator
- **Validation**: marshmallow schemas with `@validate_json(SchemaClass)` decorator
- **Rate Limiting**: flask-limiter, 5/min on login, 100/min global default
- **Caching**: Redis cache decorator `@cache(ttl=300)`

### Blueprint Registration
All blueprints in `app/api/__init__.py`. Routes get `/api` prefix by default:
- `/health` - Health check (no prefix)
- `/api/user/*` - User CRUD + auth
- `/api/demo/*` - Demo endpoints
- `/api/upload` - File upload

### Configuration
- Environment selection via `FLASK_ENV` (development/testing/production)
- All secrets via `.env` file (see `.env.example`)
- `TestingConfig` uses SQLite in-memory, no real DB needed

### Database
- **Primary**: SQLAlchemy ORM via `app/extension.py`
- **Secondary**: `app/common/util/MySQLUtil.py` for complex raw SQL queries

## Adding New Features

1. Create model in `app/api/models/`
2. Create DAO in `app/api/dao/`
3. Create service in `app/api/service/`
4. Create controller in `app/api/controller/` (add validation schema if needed)
5. Register blueprint in `app/api/__init__.py` `DEFAULT_BLUEPRINT`

## Key Files

- `manage.py` - Entry point + scheduler
- `app/config.py` - Configuration with lazy validation
- `app/extension.py` - Flask extensions (db, redis)
- `app/common/error_handlers.py` - Global exception handlers
- `app/common/rate_limiter.py` - Rate limiting setup
- `app/common/validation/` - marshmallow schemas + decorator
- `app/common/util/pagination.py` - Pagination helpers
- `app/common/util/cache.py` - Redis cache decorator
- `app/middleware/authMiddleware.py` - JWT auth decorator
