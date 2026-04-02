"""add_stripe_fields_to_organizations

Revision ID: c5f2d8b1e47a
Revises: af93ceac2f8d
Create Date: 2026-04-02

Adds stripe_customer_id and stripe_subscription_id to the organizations table.
These are populated when an org subscribes to a plan via Stripe.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c5f2d8b1e47a"
down_revision = "af93ceac2f8d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "organizations",
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("organizations", "stripe_subscription_id")
    op.drop_column("organizations", "stripe_customer_id")
