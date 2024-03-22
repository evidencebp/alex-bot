"""add unMuteAndDeafen Feature to user and guild config

Revision ID: 1b5c4ba46fbe
Revises: ebe62bce51c4
Create Date: 2023-09-12 16:21:19.190512

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1b5c4ba46fbe'
down_revision: Union[str, None] = 'ebe62bce51c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'guildconfigs', sa.Column('allowUnMuteAndDeafenOnJoin', sa.Boolean(), server_default='false', nullable=False)
    )
    op.add_column(
        'userconfigs', sa.Column('unMuteAndDeafenOnJoin', sa.Boolean(), server_default='false', nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userconfigs', 'unMuteAndDeafenOnJoin')
    op.drop_column('guildconfigs', 'allowUnMuteAndDeafenOnJoin')
    # ### end Alembic commands ###
