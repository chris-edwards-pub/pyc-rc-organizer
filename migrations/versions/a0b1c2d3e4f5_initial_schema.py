"""initial schema

Revision ID: a0b1c2d3e4f5
Revises:
Create Date: 0.1.0

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a0b1c2d3e4f5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("invite_token", sa.String(length=64), nullable=True),
        sa.Column("invited_by", sa.Integer(), nullable=True),
        sa.Column("reset_token", sa.String(length=64), nullable=True),
        sa.Column("reset_token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["invited_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("invite_token"),
        sa.UniqueConstraint("reset_token"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_site_settings_key", "site_settings", ["key"], unique=True)


def downgrade():
    op.drop_index("ix_site_settings_key", table_name="site_settings")
    op.drop_table("site_settings")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
