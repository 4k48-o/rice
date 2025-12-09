"""add_updated_fields_to_associations

Revision ID: d55f3c7d5656
Revises: add_remark_to_permissions
Create Date: 2025-12-08 17:57:03.025209

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd55f3c7d5656'
down_revision: Union[str, None] = 'add_remark_to_permissions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if columns exist before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Add updated_at and updated_by to role_permissions
    if 'role_permissions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('role_permissions')]
        
        if 'updated_at' not in columns:
            op.add_column('role_permissions', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, onupdate=sa.text('now()'), comment='更新时间'))
            print("✅ Added updated_at column to role_permissions table")
        else:
            print("⚠️  updated_at column already exists in role_permissions table")
        
        if 'updated_by' not in columns:
            op.add_column('role_permissions', sa.Column('updated_by', sa.String(length=50), nullable=True, comment='更新人ID'))
            print("✅ Added updated_by column to role_permissions table")
        else:
            print("⚠️  updated_by column already exists in role_permissions table")
    
    # Add updated_at and updated_by to user_roles
    if 'user_roles' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('user_roles')]
        
        if 'updated_at' not in columns:
            op.add_column('user_roles', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, onupdate=sa.text('now()'), comment='更新时间'))
            print("✅ Added updated_at column to user_roles table")
        else:
            print("⚠️  updated_at column already exists in user_roles table")
        
        if 'updated_by' not in columns:
            op.add_column('user_roles', sa.Column('updated_by', sa.String(length=50), nullable=True, comment='更新人ID'))
            print("✅ Added updated_by column to user_roles table")
        else:
            print("⚠️  updated_by column already exists in user_roles table")


def downgrade() -> None:
    # Check if columns exist before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'user_roles' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('user_roles')]
        
        if 'updated_by' in columns:
            op.drop_column('user_roles', 'updated_by')
        if 'updated_at' in columns:
            op.drop_column('user_roles', 'updated_at')
    
    if 'role_permissions' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('role_permissions')]
        
        if 'updated_by' in columns:
            op.drop_column('role_permissions', 'updated_by')
        if 'updated_at' in columns:
            op.drop_column('role_permissions', 'updated_at')
