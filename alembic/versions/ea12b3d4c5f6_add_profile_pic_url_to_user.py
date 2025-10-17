"""add profile_pic_url to users

Revision ID: ea12b3d4c5f6
Revises: af6ec59bd5fd
Create Date: 2025-10-17
"""

from typing import Sequence, Union

from alembic import op  # type: ignore
import sqlalchemy as sa  # type: ignore


# revision identifiers, used by Alembic.
revision: str = "ea12b3d4c5f6"
down_revision: Union[str, None] = "af6ec59bd5fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("profile_pic_url", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "profile_pic_url")


