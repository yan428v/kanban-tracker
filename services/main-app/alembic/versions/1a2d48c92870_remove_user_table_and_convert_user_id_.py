"""remove_user_table_and_convert_user_id_fks

Revision ID: 1a2d48c92870
Revises: 9ebcf4928f8d
Create Date: 2025-12-07 12:57:37.500046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2d48c92870'
down_revision: Union[str, None] = '9ebcf4928f8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('board_owner_id_fkey', 'board', type_='foreignkey')
    op.drop_constraint('team_member_user_id_fkey', 'team_member', type_='foreignkey')
    op.drop_constraint('permission_user_id_fkey', 'permission', type_='foreignkey')
    op.drop_constraint('task_user_id_fkey', 'task', type_='foreignkey')
    op.drop_constraint('comment_user_id_fkey', 'comment', type_='foreignkey')
    op.drop_constraint('task_members_user_id_fkey', 'task_members', type_='foreignkey')
    
    op.drop_table('user')


def downgrade() -> None:
    op.create_table('user',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    
    op.create_foreign_key('task_members_user_id_fkey', 'task_members', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('comment_user_id_fkey', 'comment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('task_user_id_fkey', 'task', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('permission_user_id_fkey', 'permission', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('team_member_user_id_fkey', 'team_member', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('board_owner_id_fkey', 'board', 'user', ['owner_id'], ['id'], ondelete='CASCADE')
