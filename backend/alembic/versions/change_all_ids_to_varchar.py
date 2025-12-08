"""change all ids to varchar

Revision ID: change_all_ids_to_varchar
Revises: 25753b260180
Create Date: 2025-12-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'change_all_ids_to_varchar'
down_revision: Union[str, None] = '597f7ddd950d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Change all ID fields from BIGINT to VARCHAR(50).
    Since we're starting fresh (clearing data), we can use ALTER TABLE directly.
    """
    
    # List of all tables and their ID fields to modify
    tables_to_modify = [
        # Main tables - id field
        ('tenants', 'id'),
        ('users', 'id'),
        ('departments', 'id'),
        ('roles', 'id'),
        ('permissions', 'id'),
        ('menus', 'id'),
        ('sys_login_log', 'id'),
        ('sys_opt_log', 'id'),
        
        # Association tables - id field
        ('user_roles', 'id'),
        ('role_permissions', 'id'),
        ('role_departments', 'id'),
        
        # Foreign key fields - tenant_id
        ('users', 'tenant_id'),
        ('departments', 'tenant_id'),
        ('roles', 'tenant_id'),
        ('permissions', 'tenant_id'),
        ('menus', 'tenant_id'),
        ('sys_login_log', 'tenant_id'),
        ('sys_opt_log', 'tenant_id'),
        ('user_roles', 'tenant_id'),
        ('role_permissions', 'tenant_id'),
        
        # Foreign key fields - user_id, dept_id, etc.
        ('users', 'dept_id'),
        ('departments', 'parent_id'),
        ('departments', 'leader_id'),
        ('permissions', 'parent_id'),
        ('menus', 'parent_id'),
        ('sys_login_log', 'user_id'),
        ('sys_opt_log', 'user_id'),
        ('user_roles', 'user_id'),
        ('user_roles', 'role_id'),
        ('role_permissions', 'role_id'),
        ('role_permissions', 'permission_id'),
        ('role_departments', 'role_id'),
        ('role_departments', 'department_id'),
        ('tenants', 'package_id'),
        
        # Audit fields - created_by, updated_by, deleted_by
        ('tenants', 'created_by'),
        ('tenants', 'updated_by'),
        ('tenants', 'deleted_by'),
        ('users', 'created_by'),
        ('users', 'updated_by'),
        ('users', 'deleted_by'),
        ('departments', 'created_by'),
        ('departments', 'updated_by'),
        ('departments', 'deleted_by'),
        ('roles', 'created_by'),
        ('roles', 'updated_by'),
        ('roles', 'deleted_by'),
        ('permissions', 'created_by'),
        ('permissions', 'updated_by'),
        ('permissions', 'deleted_by'),
        ('menus', 'created_by'),
        ('menus', 'updated_by'),
        ('menus', 'deleted_by'),
        ('sys_login_log', 'created_by'),
        ('sys_login_log', 'updated_by'),
        ('sys_login_log', 'deleted_by'),
        ('sys_opt_log', 'created_by'),
        ('sys_opt_log', 'updated_by'),
        ('sys_opt_log', 'deleted_by'),
        ('user_roles', 'created_by'),
        ('role_permissions', 'created_by'),
    ]
    
    # Modify each field
    for table_name, column_name in tables_to_modify:
        try:
            # Check if table exists
            connection = op.get_bind()
            inspector = sa.inspect(connection)
            if table_name not in inspector.get_table_names():
                print(f"Table {table_name} does not exist, skipping...")
                continue
            
            # Check if column exists
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if column_name not in columns:
                print(f"Column {table_name}.{column_name} does not exist, skipping...")
                continue
            
            # Alter column type
            op.alter_column(
                table_name,
                column_name,
                type_=sa.String(50),
                existing_type=sa.BigInteger(),
                existing_nullable=True if column_name in ['dept_id', 'parent_id', 'leader_id', 'created_by', 'updated_by', 'deleted_by', 'user_id', 'package_id'] else False,
                postgresql_using=f'{column_name}::text'
            )
            print(f"Changed {table_name}.{column_name} from BIGINT to VARCHAR(50)")
        except Exception as e:
            print(f"Error modifying {table_name}.{column_name}: {e}")
            # Continue with other fields even if one fails
            continue


def downgrade() -> None:
    """
    Revert all ID fields from VARCHAR(50) back to BIGINT.
    Note: This will fail if there are non-numeric string values.
    """
    
    # Same list as upgrade, but in reverse order
    tables_to_modify = [
        # Audit fields first (to avoid foreign key issues)
        ('user_roles', 'created_by'),
        ('role_permissions', 'created_by'),
        ('sys_opt_log', 'deleted_by'),
        ('sys_opt_log', 'updated_by'),
        ('sys_opt_log', 'created_by'),
        ('sys_login_log', 'deleted_by'),
        ('sys_login_log', 'updated_by'),
        ('sys_login_log', 'created_by'),
        ('menus', 'deleted_by'),
        ('menus', 'updated_by'),
        ('menus', 'created_by'),
        ('permissions', 'deleted_by'),
        ('permissions', 'updated_by'),
        ('permissions', 'created_by'),
        ('roles', 'deleted_by'),
        ('roles', 'updated_by'),
        ('roles', 'created_by'),
        ('departments', 'deleted_by'),
        ('departments', 'updated_by'),
        ('departments', 'created_by'),
        ('users', 'deleted_by'),
        ('users', 'updated_by'),
        ('users', 'created_by'),
        ('tenants', 'deleted_by'),
        ('tenants', 'updated_by'),
        ('tenants', 'created_by'),
        
        # Foreign key fields
        ('tenants', 'package_id'),
        ('role_departments', 'department_id'),
        ('role_departments', 'role_id'),
        ('role_permissions', 'permission_id'),
        ('role_permissions', 'role_id'),
        ('user_roles', 'role_id'),
        ('user_roles', 'user_id'),
        ('sys_opt_log', 'user_id'),
        ('sys_login_log', 'user_id'),
        ('menus', 'parent_id'),
        ('permissions', 'parent_id'),
        ('departments', 'leader_id'),
        ('departments', 'parent_id'),
        ('users', 'dept_id'),
        ('role_permissions', 'tenant_id'),
        ('user_roles', 'tenant_id'),
        ('sys_opt_log', 'tenant_id'),
        ('sys_login_log', 'tenant_id'),
        ('menus', 'tenant_id'),
        ('permissions', 'tenant_id'),
        ('roles', 'tenant_id'),
        ('departments', 'tenant_id'),
        ('users', 'tenant_id'),
        
        # Association tables - id field
        ('role_departments', 'id'),
        ('role_permissions', 'id'),
        ('user_roles', 'id'),
        
        # Main tables - id field
        ('sys_opt_log', 'id'),
        ('sys_login_log', 'id'),
        ('menus', 'id'),
        ('permissions', 'id'),
        ('roles', 'id'),
        ('departments', 'id'),
        ('users', 'id'),
        ('tenants', 'id'),
    ]
    
    # Modify each field
    for table_name, column_name in tables_to_modify:
        try:
            connection = op.get_bind()
            inspector = sa.inspect(connection)
            if table_name not in inspector.get_table_names():
                continue
            
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if column_name not in columns:
                continue
            
            # Alter column type back to BigInteger
            op.alter_column(
                table_name,
                column_name,
                type_=sa.BigInteger(),
                existing_type=sa.String(50),
                existing_nullable=True if column_name in ['dept_id', 'parent_id', 'leader_id', 'created_by', 'updated_by', 'deleted_by', 'user_id', 'package_id'] else False,
                postgresql_using=f'{column_name}::bigint'
            )
            print(f"Reverted {table_name}.{column_name} from VARCHAR(50) to BIGINT")
        except Exception as e:
            print(f"Error reverting {table_name}.{column_name}: {e}")
            continue

