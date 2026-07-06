# PYC RC Organizer

Privateer Yacht Club race committee organizer

## Stack

- **Backend:** Flask 3.13, SQLAlchemy, Flask-Login, Flask-Migrate
- **Database:** MySQL 8
- **Frontend:** Bootstrap 5, server-rendered Jinja templates
- **Container:** Docker + Docker Compose (web + db)
- **Deploy:** AWS Lightsail Container Service (us-east-1) via GitHub Actions → GHCR
- **Tests:** pytest with in-memory SQLite

## Local development

### With Docker (recommended)

```bash
cp .env.example .env
# Edit .env: set SECRET_KEY, INIT_ADMIN_PASSWORD
docker compose up --build
# Open http://localhost
```

### Host-mode (requires MySQL running locally as root/no-password)

```bash
cp .env.example .env
./dev.sh start        # creates .venv, installs deps, migrates, starts on :5001
./dev.sh logs         # tail output
./dev.sh stop
./dev.sh reset-db     # drop and recreate the local database
```

## Deploy to production

Deploys automatically on push to `master`:

1. Build image → push to `ghcr.io/chris-edwards-pub/pyc-rc-organizer`
2. Trivy scans for CRITICAL/HIGH CVEs (fails build if found)
3. `aws lightsail create-container-service-deployment` rolls out the new image

Required GitHub **secrets**:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- `SECRET_KEY`, `MYSQL_PASSWORD`
- `INIT_ADMIN_EMAIL`, `INIT_ADMIN_PASSWORD`

Required GitHub **variables**:
- `CONTAINER_SERVICE_NAME` (Lightsail service name)
- `DB_ENDPOINT`, `MYSQL_DATABASE`, `MYSQL_USER`

## Project structure

```
app/
├── __init__.py          # create_app() factory, __version__
├── config.py            # env-based config
├── commands.py          # `flask init-admin`, `flask create-admin`
├── models.py            # User, SiteSetting
├── permissions.py       # require_admin decorator
└── auth/                # login, register, forgot/reset password, profile, admin users
migrations/              # Flask-Migrate (Alembic)
tests/                   # pytest suite
.github/workflows/       # deploy, vulnerability scan, GHCR cleanup
AGENTS.md                # standards for AI coding agents (see agents.md convention)
CLAUDE.md                # symlink → AGENTS.md
```

## Standards

Read [AGENTS.md](AGENTS.md) before contributing.
