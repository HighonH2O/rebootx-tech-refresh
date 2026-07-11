# Sample Upgrade Scenarios

> These scenarios demonstrate the end-to-end assessment capability of RebootX.
> Each scenario represents a realistic enterprise technology upgrade request.

---

## Scenario 1: PostgreSQL 12.4 → 16.2 (Database Upgrade)

### Input

```json
{
  "technology_type": "Database",
  "current_version": "PostgreSQL 12.4",
  "target_version": "PostgreSQL 16.2",
  "dependencies": [
    "psycopg2 2.9.3",
    "pgbouncer 1.17",
    "SQLAlchemy 1.4.39",
    "Alembic 1.8.1",
    "Django ORM 4.1"
  ],
  "integrations": [
    "ETL pipeline (Apache Airflow 2.5)",
    "Reporting service (Metabase 0.44)",
    "API gateway (Kong 3.1)",
    "Backup system (pgBackRest 2.40)"
  ],
  "environment": "Production"
}
```

### Expected Risk Assessment

| Risk ID | Category | Severity | Description |
|---------|----------|----------|-------------|
| R-001 | Deprecated API | **Critical** | Deprecated connection pooling API removed in v16. `psycopg2` connection handling patterns may break. Migrate to `psycopg3` or verify `psycopg2` compatibility with PG 16 |
| R-002 | Driver Mismatch | **Medium** | `pgbouncer 1.17` may need configuration updates for PG 16's new authentication methods (SCRAM-SHA-256 default changes) |
| R-003 | Schema Drift | **Medium** | ETL pipeline schema drift risk — PG 16 changes to `pg_catalog` system tables may affect Airflow DAGs that query metadata |
| R-004 | ORM Compatibility | **Low** | SQLAlchemy 1.4 supports PG 16 but may emit deprecation warnings. Consider upgrading to SQLAlchemy 2.0 |
| R-005 | Breaking Changes | **High** | PG 16 removes legacy `postmaster` binary name. Init scripts and health checks referencing `postmaster` will fail |
| R-006 | Extension Compat | **Medium** | Verify all installed PG extensions are rebuilt/compatible with PG 16 (especially `pg_stat_statements`, `pgcrypto`) |

### Expected Validation Checks

| Check Type | Check Description | Priority |
|-----------|-------------------|----------|
| Regression | Run full test suite against PG 16 staging instance | P0 |
| Build | Verify `psycopg2` compiles against PG 16 `libpq` headers | P0 |
| Integration | Test ETL pipeline end-to-end with PG 16 backend | P0 |
| Data | Run `pg_upgrade --check` in dry-run mode | P0 |
| Performance | Benchmark critical queries — PG 16 query planner changes may affect execution plans | P1 |
| Rollback | Validate `pgBackRest` restore procedure works with PG 16 WAL format | P0 |
| Configuration | Audit `postgresql.conf` for removed/renamed parameters | P1 |
| Security | Verify SCRAM-SHA-256 auth compatibility with all connecting services | P1 |
| Monitoring | Confirm Metabase dashboard queries work with PG 16 system catalog changes | P2 |

### Expected Overall Rating

- **Overall Risk:** 🟠 **High**
- **Risks Found:** 6
- **Checks Recommended:** 9
- **Verdict:** Proceed with caution — thorough testing and dependency updates required before production cutover

---

## Scenario 2: Python 3.8 → 3.12 (Runtime Upgrade)

### Input

```json
{
  "technology_type": "Runtime",
  "current_version": "Python 3.8.16",
  "target_version": "Python 3.12.3",
  "dependencies": [
    "Django 3.2.18",
    "celery 5.2.7",
    "numpy 1.24.3",
    "pandas 1.5.3",
    "boto3 1.28.0",
    "cryptography 38.0.4",
    "setuptools 67.8.0"
  ],
  "integrations": [
    "AWS Lambda (runtime layer)",
    "Docker base image (python:3.8-slim)",
    "CI/CD pipeline (Jenkins + tox)",
    "MWAA (Managed Workflows for Apache Airflow)"
  ],
  "environment": "Production"
}
```

### Expected Risk Assessment

| Risk ID | Category | Severity | Description |
|---------|----------|----------|-------------|
| R-101 | Deprecated Syntax | **Critical** | Python 3.12 removes deprecated `distutils` module entirely. `setuptools 67.x` still imports from `distutils` — must upgrade setuptools first |
| R-102 | Framework Compat | **Critical** | Django 3.2 is EOL and does not officially support Python 3.12. Must upgrade Django to 4.2 LTS or 5.0+ |
| R-103 | Typing Changes | **High** | Python 3.12 changes to `typing` module (PEP 695) — code using `typing.TypeAlias` or `Optional` from `__future__` annotations may need updates |
| R-104 | C Extension Rebuild | **Medium** | `numpy 1.24` and `cryptography 38.x` C extensions must be recompiled for Python 3.12 ABI. Verify wheels are available |
| R-105 | Docker Base Image | **Medium** | Docker base image must change from `python:3.8-slim` to `python:3.12-slim` — verify all Dockerfile `RUN` steps still work |
| R-106 | AWS Lambda | **High** | AWS Lambda Python 3.12 runtime has different bundled SDK versions. Verify `boto3` pinned version is compatible with Lambda 3.12 runtime |
| R-107 | MWAA Compat | **High** | MWAA may not yet support Python 3.12 — verify AWS MWAA supported runtime versions before proceeding |
| R-108 | Test Framework | **Low** | `unittest` and `pytest` deprecation warnings for `asyncio` mode changes in 3.12 |

### Expected Validation Checks

| Check Type | Check Description | Priority |
|-----------|-------------------|----------|
| Build | Attempt `pip install -r requirements.txt` on Python 3.12 — identify any packages that fail to install | P0 |
| Build | Run `python -W error::DeprecationWarning` to surface all deprecation issues | P0 |
| Regression | Full test suite on Python 3.12 with `tox -e py312` | P0 |
| Integration | Deploy to staging Lambda with Python 3.12 runtime and run smoke tests | P0 |
| Integration | Verify MWAA environment supports Python 3.12 or identify migration path | P0 |
| Data | Confirm `numpy`/`pandas` numerical output consistency (floating point changes between CPython versions) | P1 |
| Performance | Benchmark — Python 3.12 has significant performance improvements; validate no regressions | P2 |
| Rollback | Maintain parallel Python 3.8 deployment for rollback during transition | P0 |
| Security | Verify `cryptography` package compiles against Python 3.12 and OpenSSL version matches | P1 |
| Configuration | Update CI/CD pipeline to test against both 3.8 and 3.12 during transition | P1 |

### Expected Overall Rating

- **Overall Risk:** 🔴 **Critical**
- **Risks Found:** 8
- **Checks Recommended:** 10
- **Verdict:** Do not proceed without upgrading Django to 4.2 LTS and setuptools first. Multi-step upgrade recommended: Python 3.8 → 3.10 → 3.12 with validation at each step

---

## Scenario 3: MWAA 2.4 → 2.8 (Managed Workflows for Apache Airflow)

### Input

```json
{
  "technology_type": "MWAA",
  "current_version": "Apache Airflow 2.4.3 (MWAA)",
  "target_version": "Apache Airflow 2.8.1 (MWAA)",
  "dependencies": [
    "apache-airflow-providers-amazon 8.2.0",
    "apache-airflow-providers-postgres 5.6.0",
    "apache-airflow-providers-http 4.5.0",
    "SQLAlchemy 1.4.41",
    "Jinja2 3.1.2"
  ],
  "integrations": [
    "S3 data lake",
    "Redshift warehouse",
    "Glue ETL jobs",
    "SNS/SQS notifications",
    "Custom Python operators"
  ],
  "environment": "Production"
}
```

### Expected Risk Assessment

| Risk ID | Category | Severity | Description |
|---------|----------|----------|-------------|
| R-201 | DAG Serialization | **High** | Airflow 2.6+ changes DAG serialization format. Complex DAGs with custom XCom backends may fail deserialization |
| R-202 | Provider Compat | **Medium** | `apache-airflow-providers-amazon 8.x` may not be compatible with Airflow 2.8 — check provider compatibility matrix |
| R-203 | DB Migration | **High** | Airflow 2.8 runs `airflow db migrate` with schema changes. MWAA handles this automatically but custom metadata queries may break |
| R-204 | Deprecated Operators | **Medium** | Several operators deprecated between 2.4 and 2.8 — `BashOperator` import path changes, `SubDagOperator` removed |
| R-205 | Config Changes | **Low** | MWAA environment configuration format may differ between versions — audit `airflow.cfg` overrides |

### Expected Overall Rating

- **Overall Risk:** 🟠 **High**
- **Risks Found:** 5
- **Checks Recommended:** 7
- **Verdict:** Proceed with caution — test all DAGs in a non-production MWAA environment first. Provider package upgrades required.

---

## Using These Scenarios

These scenarios serve as:

1. **Development Reference** — expected input/output format for the assessment API
2. **Test Cases** — seed these into the test suite to validate end-to-end pipeline
3. **Demo Data** — use during the final prototype demonstration
4. **RAG Calibration** — verify the RAG pipeline retrieves relevant context for each scenario
5. **Report Template** — the output format matches the expected readiness report structure
