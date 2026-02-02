"""Initial MSSQL schema for ApnaBackup

Revision ID: 001_initial
Revises: 
Create Date: 2025-02-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'backups',
        sa.Column('project_id', sa.String(512), primary_key=True),
        sa.Column('id', sa.Float(), primary_key=True),
        sa.Column('name', sa.Float(), nullable=True),
        sa.Column('date_time', sa.Float(), nullable=True),
        sa.Column('from_computer', sa.String(512), nullable=True),
        sa.Column('from_path', sa.String(1024), nullable=True),
        sa.Column('data_repo', sa.String(256), nullable=True),
        sa.Column('mime_type', sa.String(64), nullable=True),
        sa.Column('size', sa.Float(), nullable=True),
        sa.Column('file_name', sa.String(1024), nullable=True),
        sa.Column('full_file_name', sa.String(2048), nullable=True),
        sa.Column('log', sa.JSON(), nullable=True),
        sa.Column('pNameText', sa.String(512), nullable=True),
        sa.Column('pIdText', sa.String(512), nullable=True),
        sa.Column('bkupType', sa.String(128), nullable=True),
        sa.Column('sum_all', sa.Integer(), nullable=True),
        sa.Column('sum_done', sa.Integer(), nullable=True),
        sa.Column('done_all', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(64), nullable=True),
        sa.Column('status', sa.String(64), nullable=True),
        sa.Column('data_repod', sa.String(4096), nullable=True),
        sa.Column('repid', sa.String(256), nullable=True),
        sa.Column('fidi', sa.String(256), nullable=True),
    )
    op.create_index('idx_backups_project_id', 'backups', ['project_id'])
    op.create_index('idx_backups_project_name_id', 'backups', ['project_id', 'name', 'id'])
    op.create_index('idx_backups_project_pidtext', 'backups', ['project_id', 'pIdText'])
    op.create_index('idx_backups_project_fullfile', 'backups', ['project_id', 'full_file_name'])
    op.create_index('idx_backups_project_name_sum', 'backups', ['project_id', 'name'])

    op.create_table(
        'backups_M',
        sa.Column('project_id', sa.String(512), primary_key=True),
        sa.Column('id', sa.Float(), primary_key=True),
        sa.Column('date_time', sa.Float(), nullable=True),
        sa.Column('from_computer', sa.String(512), nullable=True),
        sa.Column('from_path', sa.String(1024), nullable=True),
        sa.Column('data_repo', sa.String(256), nullable=True),
        sa.Column('mime_type', sa.String(64), nullable=True),
        sa.Column('file_name', sa.String(1024), nullable=True),
        sa.Column('size', sa.Float(), nullable=True),
        sa.Column('pNameText', sa.String(512), nullable=True),
        sa.Column('pIdText', sa.String(512), nullable=True),
        sa.Column('bkupType', sa.String(128), nullable=True),
        sa.Column('sum_all', sa.Integer(), nullable=True),
        sa.Column('sum_done', sa.Integer(), nullable=True),
        sa.Column('done_all', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(64), nullable=True),
        sa.Column('status', sa.String(64), nullable=True),
        sa.Column('data_repod', sa.String(4096), nullable=True),
    )
    op.create_index('idx_backupsm_project_id', 'backups_M', ['project_id'])
    op.create_index('idx_backupsm_project_pidtext', 'backups_M', ['project_id', 'pIdText'])
    op.create_index('idx_backupsm_project_repo_agent_dt', 'backups_M', ['project_id', 'data_repo', 'from_computer', 'id'])

    op.create_table(
        'restores',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('project_id', sa.String(512), nullable=False),
        sa.Column('RestoreLocation', sa.String(255), nullable=False),
        sa.Column('backup_id', sa.Float(), nullable=False),
        sa.Column('backup_file_id', sa.Float(), nullable=False),
        sa.Column('backup_name', sa.String(255), nullable=False),
        sa.Column('file', sa.String(255), nullable=False),
        sa.Column('file_restore_time', sa.Float(), nullable=False),
        sa.Column('file_start', sa.String(255), nullable=False),
        sa.Column('file_end', sa.String(255), nullable=False),
        sa.Column('from_backup_pc', sa.String(255), nullable=False),
        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('restore', sa.String(255), nullable=False),
        sa.Column('storage_type', sa.String(255), nullable=False),
        sa.Column('p_id', sa.Float(), nullable=True),
        sa.Column('t14', sa.Float(), nullable=False),
        sa.Column('targetlocation', sa.String(255), nullable=False),
        sa.Column('torestore_pc', sa.String(255), nullable=False),
    )
    op.create_index('idx_restores_project_backup', 'restores', ['project_id', 'backup_id', 't14'])

    op.create_table(
        'restoreM',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('project_id', sa.String(512), nullable=False),
        sa.Column('RestoreLocation', sa.String(255), nullable=False),
        sa.Column('backup_id', sa.Float(), nullable=False),
        sa.Column('storage_type', sa.String(255), nullable=False),
        sa.Column('backup_name', sa.String(255), nullable=False),
        sa.Column('p_id', sa.Float(), nullable=True),
        sa.Column('t14', sa.Float(), nullable=False),
        sa.Column('from_backup_pc', sa.String(255), nullable=False),
        sa.Column('targetlocation', sa.String(255), nullable=False),
        sa.Column('torestore_pc', sa.String(255), nullable=False),
    )
    op.create_index('idx_restoreM_project_backup', 'restoreM', ['project_id', 'backup_id'])

    op.create_table(
        'node_jobs',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('project_id', sa.String(512), nullable=False),
        sa.Column('node', sa.String(512), nullable=False),
        sa.Column('nodeName', sa.String(512), nullable=True),
        sa.Column('total_success', sa.Integer(), default=0),
        sa.Column('total_failed', sa.Integer(), default=0),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('failed_data', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('project_id', 'node', name='uq_node_jobs_project_node'),
    )
    op.create_index('idx_node_jobs_project_node', 'node_jobs', ['project_id', 'node'])

    op.create_table(
        'jobs_recordManager',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('project_id', sa.String(512), nullable=False),
        sa.Column('idx', sa.String(256), nullable=True),
        sa.Column('agent', sa.String(512), nullable=True),
        sa.Column('name', sa.String(512), nullable=True),
        sa.Column('job_id', sa.String(256), nullable=True),
        sa.Column('src_path', sa.String(1024), nullable=True),
        sa.Column('data_repo', sa.String(256), nullable=True),
        sa.Column('next_run_time', sa.String(128), nullable=True),
        sa.Column('created_at', sa.String(64), nullable=True),
    )
    op.create_index('idx_jobrecords_project', 'jobs_recordManager', ['project_id'])
    op.create_index('idx_jobrecords_agent_name', 'jobs_recordManager', ['project_id', 'agent', 'name'])
    op.create_index('idx_jobrecords_created', 'jobs_recordManager', ['project_id', 'created_at'])

    op.create_table(
        'sessions',
        sa.Column('key_id', sa.String(256), primary_key=True),
        sa.Column('aes_key', sa.LargeBinary(), nullable=False),
        sa.Column('expires_at', sa.Float(), nullable=False),
        sa.Column('created_at', sa.Float(), nullable=False),
    )
    op.create_index('idx_sessions_expires', 'sessions', ['expires_at'])


def downgrade() -> None:
    op.drop_table('sessions')
    op.drop_table('jobs_recordManager')
    op.drop_table('node_jobs')
    op.drop_table('restoreM')
    op.drop_table('restores')
    op.drop_table('backups_M')
    op.drop_table('backups')
