"""add remark to permissions

Revision ID: add_remark_to_permissions
Revises: change_all_ids_to_varchar
Create Date: 2025-12-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_remark_to_permissions'
down_revision: Union[str, None] = 'change_all_ids_to_varchar'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'permissions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('permissions')]
        
        # Add remark column if it doesn't exist
        if 'remark' not in columns:
            op.add_column('permissions', sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'))
            print("✅ Added remark column to permissions table")
        else:
            print("⚠️  remark column already exists in permissions table")
        
        # Add tenant_id column if it doesn't exist (Permission inherits TenantMixin)
        if 'tenant_id' not in columns:
            op.add_column('permissions', sa.Column('tenant_id', sa.String(length=50), server_default='0', nullable=False, comment='租户ID,0表示平台级'))
            op.create_index(op.f('ix_permissions_tenant_id'), 'permissions', ['tenant_id'], unique=False)
            print("✅ Added tenant_id column to permissions table")
        else:
            print("⚠️  tenant_id column already exists in permissions table")


def downgrade() -> None:
    # Check if columns exist before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'permissions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('permissions')]
        
        # Remove tenant_id column if it exists
        if 'tenant_id' in columns:
            op.drop_index(op.f('ix_permissions_tenant_id'), table_name='permissions')
            op.drop_column('permissions', 'tenant_id')
        
        # Remove remark column if it exists
        if 'remark' in columns:
            op.drop_column('permissions', 'remark')

