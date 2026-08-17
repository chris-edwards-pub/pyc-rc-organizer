# Version History

## 0.1.2

- Pause daily Trivy vulnerability scan until we go live (still runnable via `workflow_dispatch`)

## 0.1.1

- Bump `cryptography` to `>=50.0.0` to resolve CVE-2026-69247 and CVE-2026-69249 (both HIGH, flagged by Trivy)

## 0.1.0

- Initial scaffold from [flask-app-template](https://github.com/chris-edwards-pub/flask-app-template): Flask app factory, auth (login/register/forgot-password), Bootstrap 5 base template, Docker Compose (web + MySQL), GitHub Actions deploy to AWS Lightsail, Trivy vulnerability scanning, pytest with in-memory SQLite fixtures, AGENTS.md conventions
