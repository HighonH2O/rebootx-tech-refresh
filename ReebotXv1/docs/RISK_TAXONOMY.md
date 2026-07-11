# Risk Taxonomy — RebootX

> Risk categories, severity definitions, scoring rules, and the check-to-risk mapping system.

---

## Risk Severity Levels

RebootX classifies all identified risks into four severity bands:

| Level | Colour | Score Range | Definition | Action Required |
|-------|--------|-------------|------------|-----------------|
| 🟢 **Low** | Green | 0.0 – 2.5 | Minor or no compatibility issues expected. Upgrade is straightforward. | Proceed with standard testing |
| 🟡 **Medium** | Yellow | 2.6 – 5.0 | Some changes required; manageable with standard processes and minor code updates. | Proceed with targeted testing |
| 🟠 **High** | Orange | 5.1 – 7.5 | Significant risks identified; thorough testing, planning, and dependency updates needed. | Proceed with caution — detailed plan required |
| 🔴 **Critical** | Red | 7.6 – 10.0 | Breaking changes detected; upgrade may require major rework, dependency replacement, or multi-step migration. | Do not proceed without remediation |

---

## Overall Risk Calculation

The **overall risk score** is computed as:

```
overall_score = max(individual_risk_scores) * 0.6 + weighted_average(all_risks) * 0.4
```

The **overall risk level** is derived from this score using the ranges above.

### Weighting by Risk Category

| Category | Weight | Rationale |
|----------|--------|-----------|
| Breaking Changes | 1.5× | Direct functional breakage |
| Deprecated API | 1.3× | Known removal path, high urgency |
| Security Vulnerability | 1.4× | Compliance and safety implications |
| Driver / ORM Mismatch | 1.2× | Typically fixable but impactful |
| Schema Drift | 1.1× | Data integrity concern |
| Configuration Changes | 1.0× | Usually straightforward to resolve |
| Performance Impact | 0.9× | Important but rarely blocking |
| Documentation Gap | 0.7× | Increases effort but rarely breaks |

---

## Risk Categories

### 1. Deprecated API / Removed Feature

**When flagged:** A feature, function, or API used by the current system is deprecated or removed in the target version.

**Severity heuristic:**
- **Critical** — Feature is removed entirely; code will fail at runtime
- **High** — Feature is deprecated with no automatic fallback
- **Medium** — Feature is deprecated but still functional with warnings
- **Low** — Feature has a drop-in replacement available

**Examples:**
- Python 3.12 removes `distutils` module
- PostgreSQL 16 removes legacy `postmaster` binary name

---

### 2. Dependency / Driver Mismatch

**When flagged:** A dependency (library, driver, ORM) is not confirmed compatible with the target version.

**Severity heuristic:**
- **Critical** — Dependency has no release supporting the target version
- **High** — Dependency requires a major version upgrade with breaking API changes
- **Medium** — Dependency needs a minor version bump; changes are well-documented
- **Low** — Dependency is confirmed compatible; only cosmetic updates needed

**Examples:**
- `psycopg2` vs PostgreSQL 16 connection API changes
- Django 3.2 does not officially support Python 3.12

---

### 3. Breaking Changes

**When flagged:** The target version introduces changes that will cause existing functionality to fail without modification.

**Severity heuristic:**
- **Critical** — Core functionality broken; system will not start or will crash
- **High** — Significant features broken; workarounds exist but are non-trivial
- **Medium** — Minor functionality affected; straightforward fix available
- **Low** — Edge cases only; unlikely to affect production workloads

---

### 4. Security Vulnerability

**When flagged:** The current version has known CVEs, or the upgrade path introduces security-relevant changes.

**Severity heuristic:**
- **Critical** — Known exploited CVE (CVSS ≥ 9.0) in current version
- **High** — High-severity CVE (CVSS 7.0–8.9) or auth mechanism change in target
- **Medium** — Medium CVE or security best-practice change
- **Low** — Informational security advisory

---

### 5. Schema / Data Migration

**When flagged:** The upgrade requires changes to database schemas, data formats, or serialisation protocols.

**Severity heuristic:**
- **Critical** — Data format is incompatible; migration is lossy or requires downtime
- **High** — Schema migration is required; can be done online but needs careful planning
- **Medium** — Minor schema changes; standard migration tools can handle
- **Low** — No schema changes; data is fully compatible

---

### 6. Integration Impact

**When flagged:** An integrated service (ETL, CI/CD, monitoring, etc.) may be affected by the upgrade.

**Severity heuristic:**
- **Critical** — Integration will break entirely (e.g., MWAA doesn't support new runtime)
- **High** — Integration needs reconfiguration or version alignment
- **Medium** — Integration works but may exhibit degraded behaviour
- **Low** — Integration is unaffected

---

### 7. Configuration Changes

**When flagged:** Configuration files, environment variables, or init scripts need updates.

**Severity heuristic:**
- **Critical** — Service fails to start with old configuration
- **High** — Configuration parameter renamed/removed with no fallback
- **Medium** — New required parameters added with sensible defaults
- **Low** — Optional new parameters available

---

### 8. Performance Impact

**When flagged:** The upgrade may affect query plans, execution speed, memory usage, or throughput.

**Severity heuristic:**
- **High** — Known performance regression in target version for relevant workloads
- **Medium** — Query planner changes that may affect execution plans
- **Low** — Performance improvements expected; verify with benchmarks

---

## Validation Check Types

Each identified risk maps to one or more recommended validation checks:

| Check Type | Description | Typical Priority |
|-----------|-------------|-----------------|
| **Regression** | Run full test suite against target version | P0 |
| **Build** | Verify all dependencies compile/install on target | P0 |
| **Integration** | End-to-end test with connected services | P0 |
| **Data** | Validate data migration, integrity, and schema compatibility | P0 |
| **Performance** | Benchmark critical workloads and queries | P1 |
| **Rollback** | Verify rollback procedure works cleanly | P0 |
| **Configuration** | Audit config files for removed/renamed parameters | P1 |
| **Security** | Verify auth, encryption, and certificate compatibility | P1 |
| **Monitoring** | Confirm observability tools work with new version | P2 |

---

## Risk-to-Check Mapping

The **Check Mapper** module automatically assigns validation checks based on identified risks:

```
Risk Category                → Recommended Check Types
─────────────────────────────────────────────────────
Deprecated API               → Build, Regression
Dependency Mismatch          → Build, Regression, Integration
Breaking Changes             → Regression, Build, Rollback
Security Vulnerability       → Security, Configuration
Schema / Data Migration      → Data, Rollback, Regression
Integration Impact           → Integration, Configuration
Configuration Changes        → Configuration, Build
Performance Impact           → Performance, Regression
```

### Priority Assignment Rules

| Rule | Priority |
|------|----------|
| Risk severity is Critical → all mapped checks are **P0** |
| Risk severity is High → primary check is **P0**, secondary checks are **P1** |
| Risk severity is Medium → all mapped checks are **P1** |
| Risk severity is Low → all mapped checks are **P2** |
| Any risk involves data integrity → related checks are **P0** regardless |
| Any risk involves rollback capability → rollback check is **P0** regardless |

---

## Verdict Logic

The final verdict is derived from the overall risk level:

| Overall Risk | Verdict |
|-------------|---------|
| 🟢 Low | **Go** — Proceed with standard upgrade process |
| 🟡 Medium | **Go with caution** — Proceed with targeted testing plan |
| 🟠 High | **Caution** — Proceed only with comprehensive testing and remediation plan |
| 🔴 Critical | **No-Go** — Do not proceed until critical risks are resolved |
