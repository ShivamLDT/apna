"""
Centralized SQLAlchemy models for ApnaBackup.
All tenant-scoped tables include project_id for multi-tenant MSSQL.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    JSON,
    Index,
    UniqueConstraint,
    LargeBinary,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BackupLogs(Base):
    """Backup logs (per-file backup records)."""

    __tablename__ = "backups"
    __table_args__ = (
        Index("idx_backups_project_id", "project_id"),
        Index("idx_backups_project_name_id", "project_id", "name", "id"),
        Index("idx_backups_project_pidtext", "project_id", "pIdText"),
        Index("idx_backups_project_fullfile", "project_id", "full_file_name"),
        Index("idx_backups_project_name_sum", "project_id", "name"),
    )

    project_id = Column(String(512), primary_key=True)
    id = Column(Float, primary_key=True)
    name = Column(Float)
    date_time = Column(Float)
    from_computer = Column(String(512))
    from_path = Column(String(1024))
    data_repo = Column(String(256))
    mime_type = Column(String(64))
    size = Column(Float)
    file_name = Column(String(1024))
    full_file_name = Column(String(2048))
    log = Column(JSON)
    pNameText = Column(String(512))
    pIdText = Column(String(512))
    bkupType = Column(String(128))
    sum_all = Column(Integer)
    sum_done = Column(Integer)
    done_all = Column(Integer)
    mode = Column(String(64))
    status = Column(String(64))
    data_repod = Column(String(4096))
    repid = Column(String(256))
    fidi = Column(String(256))


class BackupMain(Base):
    """Backup main (aggregated backup job metadata)."""

    __tablename__ = "backups_M"
    __table_args__ = (
        Index("idx_backupsm_project_id", "project_id"),
        Index("idx_backupsm_project_pidtext", "project_id", "pIdText"),
        Index(
            "idx_backupsm_project_repo_agent_dt",
            "project_id",
            "data_repo",
            "from_computer",
            "id",
        ),
    )

    project_id = Column(String(512), primary_key=True)
    id = Column(Float, primary_key=True)
    date_time = Column(Float)
    from_computer = Column(String(512))
    from_path = Column(String(1024))
    data_repo = Column(String(256))
    mime_type = Column(String(64))
    file_name = Column(String(1024))
    size = Column(Float)
    pNameText = Column(String(512))
    pIdText = Column(String(512))
    bkupType = Column(String(128))
    sum_all = Column(Integer)
    sum_done = Column(Integer)
    done_all = Column(Integer)
    mode = Column(String(64))
    status = Column(String(64))
    data_repod = Column(String(4096))


class RestoreChild(Base):
    """Restore child records (per-file restore)."""

    __tablename__ = "restores"
    __table_args__ = (
        Index("idx_restores_project_backup", "project_id", "backup_id", "t14"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(512), nullable=False)
    RestoreLocation = Column(String(255), nullable=False)
    backup_id = Column(Float, nullable=False)
    backup_file_id = Column(Float, nullable=False)
    backup_name = Column(String(255), nullable=False)
    file = Column(String(255), nullable=False)
    file_restore_time = Column(Float, nullable=False)
    file_start = Column(String(255), nullable=False)
    file_end = Column(String(255), nullable=False)
    from_backup_pc = Column(String(255), nullable=False)
    reason = Column(String(255), nullable=False)
    restore = Column(String(255), nullable=False)
    storage_type = Column(String(255), nullable=False)
    p_id = Column(Float, nullable=True)
    t14 = Column(Float, nullable=False)
    targetlocation = Column(String(255), nullable=False)
    torestore_pc = Column(String(255), nullable=False)

    @classmethod
    def to_dict(cls, instance):
        return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}


class RestoreParent(Base):
    """Restore parent records."""

    __tablename__ = "restoreM"
    __table_args__ = (Index("idx_restoreM_project_backup", "project_id", "backup_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(512), nullable=False)
    RestoreLocation = Column(String(255), nullable=False)
    backup_id = Column(Float, nullable=False)
    storage_type = Column(String(255), nullable=False)
    backup_name = Column(String(255), nullable=False)
    p_id = Column(Float, nullable=True)
    t14 = Column(Float, nullable=False)
    from_backup_pc = Column(String(255), nullable=False)
    targetlocation = Column(String(255), nullable=False)
    torestore_pc = Column(String(255), nullable=False)

    @classmethod
    def to_dict(cls, instance, bwith_children=False, session=None):
        parent_dict = {c.name: getattr(instance, c.name) for c in instance.__table__.columns}
        if bwith_children and session:
            children = session.query(RestoreChild).filter_by(
                project_id=instance.project_id,
                backup_id=parent_dict["backup_id"],
                t14=parent_dict["t14"],
            ).all()
            parent_dict["restore_files"] = [RestoreChild.to_dict(c) for c in children]
        return parent_dict

    @classmethod
    def getchildren_dict(cls, instance):
        return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}


class NodeJob(Base):
    """Node job aggregates (success/failed counts per node)."""

    __tablename__ = "node_jobs"
    __table_args__ = (
        UniqueConstraint("project_id", "node", name="uq_node_jobs_project_node"),
        Index("idx_node_jobs_project_node", "project_id", "node"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(512), nullable=False)
    node = Column(String(512), nullable=False)
    nodeName = Column(String(512), nullable=True)
    total_success = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    data = Column(JSON, nullable=True)
    failed_data = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JobRecord(Base):
    """Job records from jobs_recordManager."""

    __tablename__ = "jobs_recordManager"
    __table_args__ = (
        Index("idx_jobrecords_project", "project_id"),
        Index("idx_jobrecords_agent_name", "project_id", "agent", "name"),
        Index("idx_jobrecords_created", "project_id", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(512), nullable=False)
    idx = Column(String(256))
    agent = Column(String(512))
    name = Column(String(512))
    job_id_col = Column("job_id", String(256))  # job identifier (original SQLite column was 'id')
    src_path = Column(String(1024))
    data_repo = Column(String(256))
    next_run_time = Column(String(128))
    created_at = Column(String(64))


class SqliteMigrationLog(Base):
    """Tracks SQLite files already migrated to MSSQL to avoid re-migration on restart."""

    __tablename__ = "sqlite_migration_log"
    __table_args__ = (
        Index("idx_sqlite_migration_project", "project_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(512), nullable=False)
    source_path = Column(String(2048), nullable=False)
    migrated_at = Column(DateTime, default=datetime.utcnow)


class CryptoSession(Base):
    """Ephemeral crypto session storage (no project_id - global)."""

    __tablename__ = "sessions"
    __table_args__ = (Index("idx_sessions_expires", "expires_at"),)

    key_id = Column(String(256), primary_key=True)
    aes_key = Column(LargeBinary, nullable=False)
    expires_at = Column(Float, nullable=False)
    created_at = Column(Float, nullable=False)
