"""add role_id to role_permissions

Revision ID: b1c2d3e4f5a6
Revises: a94ea22df0ac
Create Date: 2026-03-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'a94ea22df0ac'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('role_permissions', sa.Column('role_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_role_permissions_role_id', 'role_permissions', 'roles', ['role_id'], ['id'])
    op.drop_index('ix_role_permissions_lookup', table_name='role_permissions')
    op.create_index('ix_role_permissions_lookup', 'role_permissions', ['role_id', 'blueprint', 'endpoint', 'method'])


def downgrade():
    op.drop_index('ix_role_permissions_lookup', table_name='role_permissions')
    op.create_index('ix_role_permissions_lookup', 'role_permissions', ['blueprint', 'endpoint', 'method'])
    op.drop_constraint('fk_role_permissions_role_id', 'role_permissions', type_='foreignkey')
    op.drop_column('role_permissions', 'role_id')