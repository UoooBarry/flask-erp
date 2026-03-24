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
    with op.batch_alter_table('role_permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_role_permissions_role_id', 'roles', ['role_id'], ['id'])
        batch_op.drop_index('ix_role_permissions_lookup')
        batch_op.create_index('ix_role_permissions_lookup', ['role_id', 'blueprint', 'endpoint', 'method'])


def downgrade():
    with op.batch_alter_table('role_permissions', schema=None) as batch_op:
        batch_op.drop_index('ix_role_permissions_lookup')
        batch_op.create_index('ix_role_permissions_lookup', ['blueprint', 'endpoint', 'method'])
        batch_op.drop_constraint('fk_role_permissions_role_id', type_='foreignkey')
        batch_op.drop_column('role_id')
