# Changelog

## [Unreleased]

### Fixed
- Added `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` to the shared Airflow environment so the `load` task can connect to PostgreSQL from inside the container.

## [dd74dd2] - 2026-06-16 — Infrastructure updated to Airflow 3.2.2

### Added
- `airflow-api-server` service replacing the old `airflow-webserver` (Airflow 3.x architecture).
- `airflow-dag-processor` service for parsing DAG files as a separate process.
- `airflow-triggerer` service for handling deferrable operators.
- `AIRFLOW__CORE__AUTH_MANAGER` to use the FAB auth manager.
- `AIRFLOW__CORE__EXECUTION_API_SERVER_URL` so the scheduler knows where to reach the API server.
- `AIRFLOW__CORE__SECRET_KEY` and `AIRFLOW__API_AUTH__JWT_SECRET` pinned in the shared environment so all services share the same JWT signing key — without this, each container generates a random key at startup causing `Signature verification failed` errors.
- `apache-airflow-providers-fab` to `requirements.txt`.
- SELinux volume mount flags (`:z`, `:Z`) for DAGs, logs, and plugins volumes.

### Changed
- Upgraded Airflow from `2.9.1` to `3.2.2`.
- DAG rewritten to use `with DAG(...)` context manager and `airflow.sdk` imports.
- Scheduler `environment` block moved to the shared `&airflow-env` anchor to prevent child services from losing inherited variables.

### Removed
- `.env.example` file.
