"""add_unique_constraint_team_member_user_id_team_id

Revision ID: fa220b929b14
Revises: 9ebcf4928f8d
Create Date: 2025-12-08 12:38:54.926605

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fa220b929b14'
down_revision: Union[str, None] = '9ebcf4928f8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_team_member_user_id_team_id',
        'team_member',
        ['user_id', 'team_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_team_member_user_id_team_id',
        'team_member',
        type_='unique'
    )
