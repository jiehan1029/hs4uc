"""add school tables

Revision ID: 77cdffd2045e
Revises: 92cc09b8533a
Create Date: 2024-11-28 20:11:19.808719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77cdffd2045e'
down_revision: Union[str, None] = '92cc09b8533a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('high_schools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('gs_score', sa.Float(), nullable=True),
    sa.Column('gs_url', sa.String(length=250), nullable=True),
    sa.Column('niche_score', sa.Float(), nullable=True),
    sa.Column('niche_url', sa.String(length=250), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hs_populations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.String(length=10), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['school_id'], ['high_schools.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('count_by_schools', sa.Column('school_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'count_by_schools', 'high_schools', ['school_id'], ['id'])
    op.drop_column('count_by_schools', 'school')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('count_by_schools', sa.Column('school', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'count_by_schools', type_='foreignkey')
    op.drop_column('count_by_schools', 'school_id')
    op.drop_table('hs_populations')
    op.drop_table('high_schools')
    # ### end Alembic commands ###
