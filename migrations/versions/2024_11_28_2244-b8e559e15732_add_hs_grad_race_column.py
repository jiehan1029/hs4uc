"""add hs grad race column

Revision ID: b8e559e15732
Revises: a5f7918c7251
Create Date: 2024-11-28 22:44:27.082094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e559e15732'
down_revision: Union[str, None] = 'a5f7918c7251'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hs_populations', sa.Column('count_type', sa.String(length=30), nullable=False))
    op.add_column('hs_populations', sa.Column('race', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hs_populations', 'race')
    op.drop_column('hs_populations', 'count_type')
    # ### end Alembic commands ###
