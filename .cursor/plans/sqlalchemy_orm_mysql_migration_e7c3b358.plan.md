---
name: SQLAlchemy ORM MySQL Migration
overview: Migrate ApnaBackup from SQLite (mixed SQLAlchemy + direct SQL) to a unified SQLAlchemy ORM backend on MySQL, with async MySQL for the ephemeral crypto SessionStore. Use a single MySQL database with project_id/epc columns for multi-tenancy.
todos: []
isProject: false
---

# SQLAlchemy ORM + MySQL Migration Plan

## Architecture Overview

```mermaid
flowchart TB
    subgraph before [Current State]
        SQLiteManager[sqlite_managerA]
        DirectSQL[sqlite3.connect]
        AioSQL[aiosqlite]
        Views[views.py]
        Module2[module2.py]
        JobData[jobdata.py]
        SessionStore[SessionStore]
        
        Views --> SQLiteManager
        Module2 --> SQLiteManager
        Views --> DirectSQL
        JobData --> DirectSQL
        SessionStore --> AioSQL
    end
    
    subgraph after [Target State]
        Engine[SQLAlchemy Engine]
        SessionFactory[get_session_for_project]
        AsyncEngine[Async SQLAlchemy Engine]
        AsyncSession[AsyncSession]
        
        Views2[views.py] --> SessionFactory
        Module2b[module2.py] --> SessionFactory
        JobData2[jobdata.py] --> SessionFactory
        SessionStore2[SessionStore] --> AsyncSession
        
        SessionFactory --> Engine
        AsyncSession --> AsyncEngine
        Engine --> MySQL[(MySQL)]
        AsyncEngine --> MySQL
    end
```



---

## Phase 1: Foundation

### 1.1 Dependencies and Config

**Add to requirements:**

- `pymysql` (sync MySQL driver for SQLAlchemy)
- `aiomysql` or `asyncmy` (async MySQL driver)
- `alembic` (schema migrations, optional but recommended)

**Config (env or app config):**

```python
DATABASE_URL = "mysql+pymysql://user:pass@localhost:3306/apnabackup"
ASYNC_DATABASE_URL = "mysql+aiomysql://user:pass@localhost:3306/apnabackup"
```

**Prerequisite:** MySQL Server installed locally; create database `apnabackup`.

---

### 1.2 Centralized Models with project_id

**New file:** [FlaskWebProject3/FlaskWebProject3/models.py](FlaskWebProject3/FlaskWebProject3/models.py)

- Consolidate models from [module2.py](FlaskWebProject3/module2.py): `BackupLogs`, `BackupMain`, `restore_child`, `restore_parent`, `NodeJob`
- Add `project_id` (or `epc`) column to all tenant-scoped tables:
  - `backups` (BackupLogs)
  - `backups_M` (BackupMain)
  - `restores`, `restoreM`
  - `node_jobs`
- Add `JobRecord` model for `jobs_recordManager` table
- Add `CryptoSession` model for ephemeral crypto `sessions` table
- Use `project_id` as part of composite primary keys or add indexed column for filtering
- Define indexes in `__table_args__` per Phase 6 (project_id, common filter columns, composite indexes for hot queries)

**Key change:** Current schema has one DB file per project; new schema has one DB with `project_id` in each row.

---

### 1.3 Database Session Factory

**New file:** [FlaskWebProject3/FlaskWebProject3/db.py](FlaskWebProject3/FlaskWebProject3/db.py)

- Create sync engine: `create_engine(DATABASE_URL, pool_size=20, max_overflow=10)`
- Create `sessionmaker` bound to engine
- `get_session_for_project(project_id)` context manager: yields session, automatically scopes queries by `project_id` where needed
- Helper: `get_engine()` for raw connections (e.g. streaming)

**Note:** For most ORM queries, callers pass `project_id` explicitly in filters (e.g. `session.query(BackupLogs).filter(BackupLogs.project_id == epc)`). The factory provides the session; scoping is in the query.

---

## Phase 2: Replace SQLiteManager and Direct SQL

### 2.1 module2.create_database

**File:** [FlaskWebProject3/module2.py](FlaskWebProject3/module2.py)

- Replace `SQLiteManager.execute_queries` with SQLAlchemy `Base.metadata.create_all(engine)` or Alembic migrations
- `create_database(project_id)` becomes: ensure tables exist (idempotent), optionally ensure project_id is registered
- Remove raw `CREATE TABLE` / `ALTER TABLE` strings; use model definitions
- For MySQL, handle `IF NOT EXISTS` via Alembic or try/except on create

---

### 2.2 views.py - SQLiteManager Call Sites

**File:** [FlaskWebProject3/FlaskWebProject3/views.py](FlaskWebProject3/FlaskWebProject3/views.py)

Approx. 25+ call sites. Pattern change:


| Current                                                                               | Target                                                                                                |
| ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `s_manager = SQLiteManager(); results = s_manager.execute_queries([(dbname, [sql])])` | `with get_session_for_project(epc) as session: records = session.query(BackupLogs).filter(...).all()` |
| Raw `INSERT ... ON CONFLICT`                                                          | `session.merge(BackupMain(...))` or explicit get/update/commit                                        |
| Raw `INSERT OR REPLACE`                                                               | Same as above                                                                                         |
| `SELECT * FROM backups WHERE id=X AND name=Y`                                         | `session.query(BackupLogs).filter(BackupLogs.id==X, BackupLogs.name==Y).first()`                      |
| `datetime(date_time, 'unixepoch')` in SQL                                             | Python `datetime.fromtimestamp()` or `func.from_unixtime()` for MySQL                                 |
| `replace(replace(full_file_name,...))`                                                | Python string ops or `func.replace()`                                                                 |


**Critical routes to refactor:**

- `data_download` (~3543)
- `save_savelogdata` (~7903, 8013, 8081, 8129, 8145)
- `save_saveinit_log` (~8272)
- `get_restpre_file_data` (~8502, 8515, 8540)
- `get_restore_data` (~8728, 8759, 8954, 9909, 9937, 9961, 9970)
- Aggregation logic using `text("UPDATE backups_M...")` (~8365) - convert to ORM or parameterized raw SQL

**SQL dialect fixes:**

- `ON CONFLICT(id) DO UPDATE` -> `session.merge()` or MySQL `INSERT ... ON DUPLICATE KEY UPDATE` via `text()` if needed
- `INSERT OR REPLACE` -> `session.merge()` or delete + insert
- `char(92)` (backslash) -> MySQL `CHAR(92)` or Python handling
- `COALESCE(from_path || char(92) || file_name, ...)` -> `func.concat()` or Python

---

### 2.3 get_db_connection (node_jobs)

**File:** [FlaskWebProject3/FlaskWebProject3/views.py](FlaskWebProject3/FlaskWebProject3/views.py) ~2663

- Remove `get_db_connection` and `sqlite3.connect`
- Use `session.query(NodeJob).filter(...)` with `get_session_for_project`
- Ensure `NodeJob` has `project_id` or equivalent scoping

---

### 2.4 jobdata.py

**File:** [FlaskWebProject3/FlaskWebProject3/jobdata.py](FlaskWebProject3/FlaskWebProject3/jobdata.py)

- Replace `sqlite3.connect` with SQLAlchemy session from `db.py`
- Use `JobRecord` model; map `create_table` to model; replace `cursor.execute` with ORM
- Add `project_id` to `JobRecord` if job data is per-project

---

### 2.5 fClient sjbs (class1x.py, class2.py)

**Files:** [fClient/fClient/sjbs/class1x.py](fClient/fClient/sjbs/class1x.py), [fClient/fClient/sjbs/class2.py](fClient/fClient/sjbs/class2.py)

- Replace `sqlite3.connect` + `cursor.execute` with SQLAlchemy session
- Map tables to models or use `session.execute(text(...))` with parameterized queries
- Determine project/scope from context and pass to session factory

---

### 2.6 fClient runserver.py

**File:** [fClient/runserver.py](fClient/runserver.py)

- Update `SQLALCHEMY_DATABASE_URI` to MySQL URL
- Update `SCHEDULER_JOBSTORES` URL to same MySQL
- Replace `SQLiteManager.execute_queries` (schema migrations ~2573) with Alembic or `create_all`
- Replace all `create_engine("sqlite:///...")` with shared MySQL engine
- Update DoneJob, MissedJob, restore_parent, restore_child usages to use MySQL-backed session

---

### 2.7 module13.py

**File:** [FlaskWebProject3/module13.py](FlaskWebProject3/module13.py)

- Replace `sqlite3.connect` and `cursor.execute` with SQLAlchemy session

---

## Phase 3: Async MySQL for SessionStore

### 3.1 Ephemeral Crypto SessionStore

**File:** [FlaskWebProject3/FlaskWebProject3/ephemeral_crypto/middleware.py](FlaskWebProject3/FlaskWebProject3/ephemeral_crypto/middleware.py)

- Replace `aiosqlite` with SQLAlchemy 2.0 async:
  - `create_async_engine(ASYNC_DATABASE_URL)`
  - `AsyncSession`, `async_sessionmaker`
- Remove all `PRAGMA` calls (MySQL has no equivalent)
- Replace `INSERT OR REPLACE` with `session.merge(CryptoSession(...))` or MySQL `INSERT ... ON DUPLICATE KEY UPDATE`
- Replace `file:path?mode=ro` with normal async connection (MySQL supports read-only via user/session)
- Keep `_run_async` wrapper for calling from sync Flask context
- Add `CryptoSession` model with columns: `key_id`, `aes_key`, `expires_at`, `created_at`

---

## Phase 4: Data Migration and Cleanup

### 4.1 Data Migration Script

**New file:** [tools/migrate_sqlite_to_mysql.py](tools/migrate_sqlite_to_mysql.py)

- Scan `app.config["location"]` for `*.db` SQLite files
- For each file, extract `project_id` from filename (e.g. strip `.db`)
- Connect to SQLite (read-only) and MySQL
- For each table: read rows, add `project_id`, insert into MySQL
- Handle `backups`, `backups_M`, `restores`, `restoreM`, `node_jobs`, `jobs_recordManager`
- Run once before cutover

---

### 4.2 Deprecate SQLiteManager

- Delete or stub [FlaskWebProject3/FlaskWebProject3/sqlite_managerA.py](FlaskWebProject3/FlaskWebProject3/sqlite_managerA.py)
- Delete [FlaskWebProject3/sqlite_managerA.py](FlaskWebProject3/sqlite_managerA.py)
- Delete [fClient/fClient/sqlite_managerA.py](fClient/fClient/sqlite_managerA.py)
- Remove all imports and usages

---

## Phase 5: Schema and Compatibility

### 5.1 Alembic (Recommended)

- `alembic init`
- Generate initial revision from models
- Use for future schema changes
- Handles MySQL-specific DDL (e.g. `IF NOT EXISTS`)

### 5.2 Backward Compatibility

- Add config flag `USE_MYSQL=true`; if false, keep SQLite path (optional, for gradual rollout)
- Or hard cutover: remove SQLite code once migration is validated

---

## Execution Order

1. Add dependencies, config, create MySQL DB
2. Create `models.py` with all models + `project_id` + indexes (`__table_args__`)
3. Create `db.py` with engine and session factory (pool settings)
4. Add `CryptoSession` model and refactor `SessionStore` to async MySQL
5. Refactor `module2.create_database` to use SQLAlchemy
6. Refactor `views.py` SQLiteManager call sites (largest effort)
7. Refactor `get_db_connection`, `jobdata.py`, `class1x.py`, `class2.py`, `module13.py`
8. Refactor `fClient/runserver.py`
9. Write and run data migration script
10. Remove SQLiteManager and sqlite3 usages
11. Run Alembic migrations to create tables and indexes
12. Test end-to-end; profile slow queries; add indexes if needed

---

## Phase 6: Database Optimizations (Indexes and Performance)

### 6.1 Index Strategy

Indexes are defined in SQLAlchemy models via `Index()` or `__table_args__` and applied via Alembic migrations. Below are indexes derived from actual query patterns in [views.py](FlaskWebProject3/FlaskWebProject3/views.py), [jobdata.py](FlaskWebProject3/FlaskWebProject3/jobdata.py), and [module2.py](FlaskWebProject3/module2.py).

**backups (BackupLogs):**


| Index                        | Columns                    | Rationale                                     |
| ---------------------------- | -------------------------- | --------------------------------------------- |
| PK                           | id                         | Primary key lookup                            |
| idx_backups_project_id       | project_id                 | Every query filters by project first          |
| idx_backups_project_name_id  | project_id, name, id       | data_download: `WHERE id=X AND name=Y`        |
| idx_backups_project_pidtext  | project_id, pIdText        | Restore file lookup by backup_pid             |
| idx_backups_project_fullfile | project_id, full_file_name | Restore path matching                         |
| idx_backups_project_name_sum | project_id, name           | Aggregation: `WHERE name = j_sta GROUP BY id` |


**backups_M (BackupMain):**


| Index                              | Columns                                  | Rationale                                        |
| ---------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| PK                                 | id                                       | Primary key                                      |
| idx_backupsm_project_id            | project_id                               | Tenant scoping                                   |
| idx_backupsm_project_pidtext       | project_id, pIdText                      | Restore list, file lookup                        |
| idx_backupsm_project_repo_agent_dt | project_id, data_repo, from_computer, id | Restore filters: storage type, agent, date range |


**restores, restoreM:**


| Index                       | Columns                    | Rationale             |
| --------------------------- | -------------------------- | --------------------- |
| idx_restores_project_backup | project_id, backup_id, t14 | restore_child lookup  |
| idx_restoreM_project_backup | project_id, backup_id      | restore_parent filter |


**node_jobs:**


| Index                      | Columns          | Rationale                                           |
| -------------------------- | ---------------- | --------------------------------------------------- |
| idx_node_jobs_project_node | project_id, node | `WHERE node = ?` lookup; node is unique per project |


**jobs_recordManager (JobRecord):**


| Index                     | Columns                 | Rationale                          |
| ------------------------- | ----------------------- | ---------------------------------- |
| idx_jobrecords_project    | project_id              | Tenant scoping                     |
| idx_jobrecords_agent_name | project_id, agent, name | `GROUP BY agent, name`             |
| idx_jobrecords_created    | project_id, created_at  | `ORDER BY created_at DESC LIMIT N` |


**sessions (CryptoSession):**


| Index                | Columns    | Rationale                              |
| -------------------- | ---------- | -------------------------------------- |
| PK                   | key_id     | Session lookup by key                  |
| idx_sessions_expires | expires_at | Cleanup: `DELETE WHERE expires_at < ?` |


---

### 6.2 Model Definition (SQLAlchemy)

Define indexes in [models.py](FlaskWebProject3/FlaskWebProject3/models.py) using `__table_args__`:

```python
from sqlalchemy import Index

class BackupLogs(Base):
    __tablename__ = "backups"
    __table_args__ = (
        Index("idx_backups_project_name_id", "project_id", "name", "id"),
        Index("idx_backups_project_pidtext", "project_id", "pIdText"),
        Index("idx_backups_project_fullfile", "project_id", "full_file_name"),
        Index("idx_backups_project_name_sum", "project_id", "name"),
    )
    # ... columns
```

---

### 6.3 Alembic Migration for Indexes

- Add indexes in the initial Alembic revision or in a follow-up migration.
- Use `op.create_index()` for manual control, or let Alembic auto-generate from model `__table_args__`.
- For existing data, `CREATE INDEX` in MySQL is online-friendly (no full table lock in MySQL 8.0+).

---

### 6.4 Other Optimizations

**Connection pool (already in Phase 1):**

- `pool_size=20`, `max_overflow=10` for sync engine
- Async pool: `pool_size=10`, `max_overflow=5` for SessionStore

**MySQL server tuning (optional, for ops):**

- InnoDB buffer pool size
- `innodb_flush_log_at_trx_commit` (1 for durability, 2 for performance)
- Query cache (deprecated in MySQL 8.0; rely on app caching instead)

**Query-level:**

- Use `session.query(Model).filter(...).options(joinedload(...))` to avoid N+1 when loading relationships.
- For large result sets (e.g. restore list), use `yield_per(1000)` or server-side cursors.
- Avoid `SELECT *` where only a few columns are needed; select explicit columns to reduce I/O.

**Application-level:**

- Cache hot data (e.g. restore job lists) in Redis or in-memory with TTL if needed later.

---

### 6.5 Index Maintenance

- Monitor slow queries: enable MySQL slow query log, use `EXPLAIN` for new queries.
- Add indexes incrementally via Alembic if new query patterns emerge.
- Avoid over-indexing: each index adds write overhead; prioritize read-heavy columns.

---

## Risk Mitigation

- **Row tuple vs ORM object:** Current code often uses `file_paths[0][8]` (column index). After ORM, use attribute access (`row.mime_type`) or keep explicit column ordering in selects.
- **JSON columns:** MySQL 5.7+ has `JSON` type; use `JSON` or `VARCHAR(MAX)` with JSON validation. SQLAlchemy `JSON` works with both.
- **Float primary keys:** `BackupLogs.id`, `BackupMain.id` are FLOAT. MySQL supports `DOUBLE`; keep as-is in models.
- **Concurrency:** MySQL handles concurrent writes; no WAL/PRAGMA. Connection pooling in SQLAlchemy is sufficient.

---

## Estimated Effort


| Phase                                 | Days           |
| ------------------------------------- | -------------- |
| 1. Foundation                         | 1–2            |
| 2. Replace SQLiteManager + direct SQL | 4–5            |
| 3. Async SessionStore                 | 1              |
| 4. Data migration + cleanup           | 1–2            |
| 5. Schema + Alembic                   | 0.5            |
| 6. Indexes and optimizations          | 0.5–1          |
| 7. Testing and fixes                  | 2–3            |
| **Total**                             | **10–14 days** |


