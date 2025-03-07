"""Combinando as revisions 87c144a283df e 79a896c147ec

Revision ID: 46b16f55c18d
Revises: 87c144a283df, 79a896c147ec
Create Date: 2025-03-07 19:37:39.199866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46b16f55c18d'
down_revision: Union[str, None] = ('87c144a283df', '79a896c147ec')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
