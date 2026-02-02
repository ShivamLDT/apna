"""Add sqlite_migration_log table for auto-migration tracking

Revision ID: 002_sqlite_log
Revises: 001_initial
Create Date: 2025-02-01

"""
from alembic import op
import sqlalchemy as sa

revision = '002_sqlite_log'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sqlite_migration_log',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('project_id', sa.String(512), nullable=False),
        sa.Column('source_path', sa.String(2048), nullable=False),
        sa.Column('migrated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_sqlite_migration_project', 'sqlite_migration_log', ['project_id'])


def downgrade() -> None:
    op.drop_index('idx_sqlite_migration_project', table_name='sqlite_migration_log')
    op.drop_table('sqlite_migration_log')
