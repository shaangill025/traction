"""v1-pres-req-templates

Revision ID: 135b4f1c8965
Revises: 5f13cfb97471
Create Date: 2022-07-28 11:56:24.859875

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "135b4f1c8965"
down_revision = "5f13cfb97471"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "presentation_request_template",
        sa.Column(
            "presentation_request_template_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "external_reference_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "presentation_request",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("deleted", sa.Boolean(), nullable=False),
        sa.Column("comment", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("error_status_detail", sa.VARCHAR(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
        ),
        sa.PrimaryKeyConstraint("presentation_request_template_id"),
    )
    op.create_index(
        op.f("ix_presentation_request_template_tenant_id"),
        "presentation_request_template",
        ["tenant_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_presentation_request_template_tenant_id"),
        table_name="presentation_request_template",
    )
    op.drop_table("presentation_request_template")
    # ### end Alembic commands ###