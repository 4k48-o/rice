"""add dict tables

Revision ID: add_dict_tables
Revises: d55f3c7d5656
Create Date: 2025-12-10 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_dict_tables'
down_revision: Union[str, None] = 'd55f3c7d5656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dict_types table
    op.create_table('dict_types',
    sa.Column('name', sa.String(length=50), nullable=False, comment='字典类型名称'),
    sa.Column('code', sa.String(length=50), nullable=False, comment='字典类型编码(唯一)'),
    sa.Column('sort', sa.Integer(), server_default='0', nullable=False, comment='排序(升序)'),
    sa.Column('status', sa.SmallInteger(), server_default='1', nullable=False, comment='状态:0禁用,1启用'),
    sa.Column('id', sa.String(length=50), nullable=False, comment='主键ID'),
    sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.Column('created_by', sa.String(length=50), nullable=True, comment='创建人ID'),
    sa.Column('updated_by', sa.String(length=50), nullable=True, comment='更新人ID'),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False, comment='是否删除'),
    sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间'),
    sa.Column('deleted_by', sa.String(length=50), nullable=True, comment='删除人ID'),
    sa.Column('tenant_id', sa.String(length=50), server_default='0', nullable=False, comment='租户ID,0表示平台级'),
    sa.PrimaryKeyConstraint('id'),
    comment='字典类型表'
    )
    op.create_index(op.f('ix_dict_types_code'), 'dict_types', ['code'], unique=False)
    op.create_index(op.f('ix_dict_types_tenant_id'), 'dict_types', ['tenant_id'], unique=False)
    # Create unique index for code + tenant_id combination
    op.create_index('uk_dict_types_code_tenant', 'dict_types', ['code', 'tenant_id'], unique=True)
    
    # Create dict_data table
    op.create_table('dict_data',
    sa.Column('dict_type_id', sa.String(length=50), nullable=False, comment='字典类型ID'),
    sa.Column('label', sa.String(length=100), nullable=False, comment='字典标签(显示文本)'),
    sa.Column('value', sa.String(length=100), nullable=False, comment='字典值'),
    sa.Column('sort', sa.Integer(), server_default='0', nullable=False, comment='排序(升序)'),
    sa.Column('status', sa.SmallInteger(), server_default='1', nullable=False, comment='状态:0禁用,1启用'),
    sa.Column('css_class', sa.String(length=100), nullable=True, comment='CSS类名'),
    sa.Column('color', sa.String(length=50), nullable=True, comment='颜色值'),
    sa.Column('icon', sa.String(length=100), nullable=True, comment='图标'),
    sa.Column('id', sa.String(length=50), nullable=False, comment='主键ID'),
    sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.Column('created_by', sa.String(length=50), nullable=True, comment='创建人ID'),
    sa.Column('updated_by', sa.String(length=50), nullable=True, comment='更新人ID'),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False, comment='是否删除'),
    sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='删除时间'),
    sa.Column('deleted_by', sa.String(length=50), nullable=True, comment='删除人ID'),
    sa.Column('tenant_id', sa.String(length=50), server_default='0', nullable=False, comment='租户ID,0表示平台级'),
    sa.PrimaryKeyConstraint('id'),
    comment='字典数据表'
    )
    op.create_index(op.f('ix_dict_data_dict_type_id'), 'dict_data', ['dict_type_id'], unique=False)
    op.create_index(op.f('ix_dict_data_tenant_id'), 'dict_data', ['tenant_id'], unique=False)
    # Create unique index for value + dict_type_id combination
    op.create_index('uk_dict_data_value_type', 'dict_data', ['value', 'dict_type_id'], unique=True)


def downgrade() -> None:
    op.drop_index('uk_dict_data_value_type', table_name='dict_data')
    op.drop_index(op.f('ix_dict_data_tenant_id'), table_name='dict_data')
    op.drop_index(op.f('ix_dict_data_dict_type_id'), table_name='dict_data')
    op.drop_table('dict_data')
    op.drop_index('uk_dict_types_code_tenant', table_name='dict_types')
    op.drop_index(op.f('ix_dict_types_tenant_id'), table_name='dict_types')
    op.drop_index(op.f('ix_dict_types_code'), table_name='dict_types')
    op.drop_table('dict_types')

