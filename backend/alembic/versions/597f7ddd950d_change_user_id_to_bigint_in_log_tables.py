"""change_user_id_to_bigint_in_log_tables

Revision ID: 597f7ddd950d
Revises: d675cfa187b4
Create Date: 2025-12-07 20:17:02.631120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '597f7ddd950d'
down_revision: Union[str, None] = 'd675cfa187b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change user_id from INTEGER to BIGINT in log tables
    op.alter_column('sys_login_log', 'user_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)
    op.alter_column('sys_opt_log', 'user_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)


def downgrade() -> None:
    # Revert user_id from BIGINT to INTEGER in log tables
    op.alter_column('sys_opt_log', 'user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=True)
    op.alter_column('sys_login_log', 'user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=True)
