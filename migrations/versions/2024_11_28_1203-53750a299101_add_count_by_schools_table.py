"""add count_by_schools table

Revision ID: 53750a299101
Revises: 
Create Date: 2024-11-28 12:03:36.469161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53750a299101'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('count_by_schools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=False),
    sa.Column('school', sa.String(length=100), nullable=False),
    sa.Column('race', sa.String(length=50), nullable=False),
    sa.Column('count_type', sa.String(length=30), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('count_by_schools')
    # ### end Alembic commands ###
