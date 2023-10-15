"""update_column_createdat_inTable

Revision ID: 01fb3bc2b33b
Revises: a5068817932c
Create Date: 2023-10-13 13:13:21.557108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01fb3bc2b33b'
down_revision: Union[str, None] = 'a5068817932c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tb_account', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('tb_branch', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tb_branch', 'created_at')
    op.drop_column('tb_account', 'created_at')
    # ### end Alembic commands ###