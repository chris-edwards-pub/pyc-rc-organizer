# PYC RC Organizer — Project Standards

## Python Standards
- Python 3.13
- Type hints encouraged on function signatures
- f-strings over `.format()` or `%` formatting
- Use pathlib for file paths where practical
- The local dev environment uses .venv

## Code Style
- **Formatter:** Black (line length 88)
- **Imports:** isort (Black-compatible profile)
- **Linting:** flake8 (max line length 120, configured in `.flake8`)
- Run: `black . && isort . && flake8`

## Project Conventions
- Flask app factory pattern (`create_app()` in `app/__init__.py`)
- Blueprints for route organization (start with `auth`; add more as needed)
- SQLAlchemy models in `app/models.py`
- Config from environment variables via `app/config.py`
- All secrets in `.env` — **never committed**

## Version Schema
Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`
- **MAJOR:** breaking changes (auth overhaul, DB schema rewrite)
- **MINOR:** new features (new page, new functionality)
- **PATCH:** bug fixes, small tweaks
- Version tracked in `app/__init__.py` as `__version__`
- **Every `feature/` or `fix/` branch must bump the version and update `VERSIONS.md` before merging**
  - `feature/` branches bump MINOR (e.g. 0.1.0 → 0.2.0)
  - `fix/` branches bump PATCH (e.g. 0.2.0 → 0.2.1)
- **After merging, tag the merge commit:** `git tag v<version>` and `git push origin --tags`

## Task Tracking
- When working on complex or multi-step tasks, create a todo list to track progress and remain on track
- Check off items as they are completed to maintain visibility into what remains

## Git Workflow
- `master` branch is production-ready — **never push directly to master**
- All work must be on a branch: `feature/<name>` for new work, `fix/<name>` for bug fixes
- Merge to `master` via PR when complete and tested
- Commit messages: imperative mood, concise ("Add regatta CRUD routes")
- **After tests pass**, prompt the user to: commit, push, create PR, merge, tag, and clean up branches — do not proceed without confirmation at each step

## Testing
- Framework: pytest
- Tests in `tests/` directory
- Run: `pytest` (or `.venv/bin/pytest` outside venv)
- **Fixtures** (`tests/conftest.py`):
  - `app` — Flask app with SQLite in-memory DB, CSRF disabled, `TESTING=True`
  - `db` — SQLAlchemy database instance
  - `client` — Flask test client
  - `admin_user` — pre-created admin user (admin@test.com / password)
  - `logged_in_client` — test client already authenticated as admin
- **Patterns**: use `unittest.mock.patch` for external APIs; all fixtures are function-scoped
- **All new features and bug fixes MUST include tests** — write and run tests for every code change before considering it complete
- **Always ask the user before running tests** — never run `pytest` without prompting first
- **Run the full test suite (`pytest`) after every change** to ensure nothing is broken

## Docker
- Local dev: `docker compose up --build`
- Production: AWS Lightsail container service (us-east-1)
- 2 containers: web (Flask/Gunicorn), db (MySQL 8)

## Security
- Store all sensitive information in GitHub secrets and variables
- Check each PR for known security issues
- When planning, take security into consideration

## Design
- All pages and components must be responsive — designed to work on phones, tablets, and desktop screens
- Use Bootstrap's responsive grid, breakpoints, and utility classes to ensure layouts adapt to all screen sizes
- Test views at mobile (< 576px), tablet (768px), and desktop (1200px+) widths

## Documentation
- Keep the README.md file up to date with each PR

## Local testing
- Testing can be done locally. Docker and MySQL should be locally installed.
- Testing should be done with each PR
- Local admin credentials are set via `INIT_ADMIN_EMAIL` and `INIT_ADMIN_PASSWORD` in `.env`

## Database
- Every feature or code change that depends on a schema update must have a corresponding migration applied first.
