"""empty message

Revision ID: 0d5ab5037e05
Revises: 88b337c831b7
Create Date: 2025-01-10 08:56:40.447723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '0d5ab5037e05'
down_revision: Union[str, None] = '88b337c831b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('scheduletask', schema=None) as batch_op:
        batch_op.add_column(sa.Column('schedule_params', sqlite.JSON(), nullable=True))
        batch_op.add_column(sa.Column('user_telegram_data', sqlite.JSON(), nullable=True))
        batch_op.alter_column('task_type',
               existing_type=sa.VARCHAR(length=7),
               type_=sa.Enum('REGULAR', 'ONCE', 'DAILY', 'WEEKLY', 'REMINDER', 'TASK', name='tasktype'),
               existing_nullable=False)
        batch_op.drop_column('schedule')
        batch_op.drop_column('action')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('scheduletask', schema=None) as batch_op:
        batch_op.add_column(sa.Column('action', sa.VARCHAR(), nullable=False))
        batch_op.add_column(sa.Column('schedule', sa.VARCHAR(), nullable=False))
        batch_op.alter_column('task_type',
               existing_type=sa.Enum('REGULAR', 'ONCE', 'DAILY', 'WEEKLY', 'REMINDER', 'TASK', name='tasktype'),
               type_=sa.VARCHAR(length=7),
               existing_nullable=False)
        batch_op.drop_column('user_telegram_data')
        batch_op.drop_column('schedule_params')

    # ### end Alembic commands ###
