"""Drop indicator table

Revision ID: bf680218422d
Revises: 2f87409d32a3
Create Date: 2024-12-26 15:23:47.506427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf680218422d'
down_revision: Union[str, None] = '2f87409d32a3'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('indicator')


def downgrade():
    # Если нужно вернуть таблицу при откате миграции:
    op.create_table(
        'indicator',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('indicator_name', sa.String, nullable=False, unique=True),
        sa.Column('indicator_value', sa.Integer, nullable=False),
        sa.Column('indicator_params_id', sa.Integer, nullable=False),
    )