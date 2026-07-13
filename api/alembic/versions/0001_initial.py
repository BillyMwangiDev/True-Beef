"""initial: animals, ledger_events, append-only trigger

Revision ID: 0001
Revises:
Create Date: 2026-07-13
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "animals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_tag", sa.String(), nullable=True),
        sa.Column("breed", sa.String(), nullable=False),
        sa.Column("sex", sa.String(), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("sire_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("dam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("us_born", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("us_raised", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("muzzle_ref", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "ledger_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("animal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("prev_hash", sa.String(), nullable=False),
        sa.Column("hash", sa.String(), nullable=False),
        sa.Column("signature", sa.String(), nullable=True),
        sa.Column("signer_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("animal_id", "seq", name="uq_ledger_animal_seq"),
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ledger_events_no_mutate() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'ledger_events is append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER ledger_events_append_only
        BEFORE UPDATE OR DELETE ON ledger_events
        FOR EACH ROW EXECUTE FUNCTION ledger_events_no_mutate();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS ledger_events_append_only ON ledger_events;")
    op.execute("DROP FUNCTION IF EXISTS ledger_events_no_mutate();")
    op.drop_table("ledger_events")
    op.drop_table("animals")
