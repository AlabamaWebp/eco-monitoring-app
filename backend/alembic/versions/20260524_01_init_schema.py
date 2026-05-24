"""Initial schema for eco monitoring app.

Revision ID: 20260524_01
Revises:
Create Date: 2026-05-24 17:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260524_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_collectors",
        sa.Column("collector_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("middle_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("collector_id"),
    )
    op.create_index("ix_data_collectors_last_name", "data_collectors", ["last_name"], unique=False)

    op.create_table(
        "measurement_units",
        sa.Column("unit_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("unit_id"),
        sa.UniqueConstraint("symbol"),
    )

    op.create_table(
        "polygons",
        sa.Column("polygon_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("polygon_id"),
    )

    op.create_table(
        "sensor_types",
        sa.Column("sensor_type_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("unit_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["unit_id"], ["measurement_units.unit_id"]),
        sa.PrimaryKeyConstraint("sensor_type_id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "import_files",
        sa.Column("import_file_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("polygon_id", sa.BigInteger(), nullable=False),
        sa.Column("collector_id", sa.BigInteger(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("rows_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("measurements_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["collector_id"], ["data_collectors.collector_id"]),
        sa.ForeignKeyConstraint(["polygon_id"], ["polygons.polygon_id"]),
        sa.PrimaryKeyConstraint("import_file_id"),
    )
    op.create_index(
        "idx_import_files_polygon_uploaded",
        "import_files",
        ["polygon_id", "uploaded_at"],
        unique=False,
    )

    op.create_table(
        "measurements",
        sa.Column("measurement_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("polygon_id", sa.BigInteger(), nullable=False),
        sa.Column("sensor_type_id", sa.BigInteger(), nullable=False),
        sa.Column("unit_id", sa.BigInteger(), nullable=False),
        sa.Column("import_file_id", sa.BigInteger(), nullable=True),
        sa.Column("measured_at", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Numeric(precision=16, scale=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["import_file_id"], ["import_files.import_file_id"]),
        sa.ForeignKeyConstraint(["polygon_id"], ["polygons.polygon_id"]),
        sa.ForeignKeyConstraint(["sensor_type_id"], ["sensor_types.sensor_type_id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["measurement_units.unit_id"]),
        sa.PrimaryKeyConstraint("measurement_id"),
    )
    op.create_index(
        "idx_measurements_polygon_sensor_time",
        "measurements",
        ["polygon_id", "sensor_type_id", "measured_at"],
        unique=False,
    )
    op.create_index(
        "idx_measurements_sensor_time_polygon",
        "measurements",
        ["sensor_type_id", "measured_at", "polygon_id"],
        unique=False,
    )
    op.create_index("idx_measurements_time", "measurements", ["measured_at"], unique=False)
    op.create_index("idx_measurements_import_file", "measurements", ["import_file_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_measurements_import_file", table_name="measurements")
    op.drop_index("idx_measurements_time", table_name="measurements")
    op.drop_index("idx_measurements_sensor_time_polygon", table_name="measurements")
    op.drop_index("idx_measurements_polygon_sensor_time", table_name="measurements")
    op.drop_table("measurements")

    op.drop_index("idx_import_files_polygon_uploaded", table_name="import_files")
    op.drop_table("import_files")

    op.drop_table("sensor_types")
    op.drop_table("polygons")
    op.drop_table("measurement_units")
    op.drop_index("ix_data_collectors_last_name", table_name="data_collectors")
    op.drop_table("data_collectors")

