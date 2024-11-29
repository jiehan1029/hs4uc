"""fix school fk name

Revision ID: a5f7918c7251
Revises: 285bff27284b
Create Date: 2024-11-28 20:30:15.910009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5f7918c7251'
down_revision: Union[str, None] = '285bff27284b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('count_by_schools', sa.Column('school', sa.String(length=100), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('count_by_schools', 'school')
    # ### end Alembic commands ###
