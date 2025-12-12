"""add_completed_at_to_task

Revision ID: 549db8bfdcab
Revises: fa220b929b14
Create Date: 2025-12-12 13:51:11.308697

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '549db8bfdcab'
down_revision: str | None = 'fa220b929b14'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("task", sa.Column("completed_at", sa.DateTime(), nullable=True))

    op.execute(
        text(
            """
            UPDATE task
            SET completed_at = updated_at
            WHERE status = 'COMPLETED' AND completed_at IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_column("task", "completed_at")
