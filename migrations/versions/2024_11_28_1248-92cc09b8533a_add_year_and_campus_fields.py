"""add year and campus fields

Revision ID: 92cc09b8533a
Revises: 53750a299101
Create Date: 2024-11-28 12:48:57.475607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92cc09b8533a'
down_revision: Union[str, None] = '53750a299101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('count_by_schools', sa.Column('year', sa.String(length=10), nullable=False))
    op.add_column('count_by_schools', sa.Column('campus', sa.String(length=30), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('count_by_schools', 'campus')
    op.drop_column('count_by_schools', 'year')
    # ### end Alembic commands ###
