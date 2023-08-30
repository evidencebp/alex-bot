"""add dontvocieSleep to user config

Revision ID: ebe62bce51c4
Revises: e56ba565f414
Create Date: 2023-08-29 19:33:11.831862

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ebe62bce51c4'
down_revision: Union[str, None] = 'e56ba565f414'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userconfigs', sa.Column('dontVoiceSleep', sa.Boolean(), nullable=False, server_default='false'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userconfigs', 'dontVoiceSleep')
    # ### end Alembic commands ###