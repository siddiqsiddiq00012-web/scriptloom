"""add production billing schema

Revision ID: a1b2c3d4e5f6
Revises: align_clips_schema
Create Date: 2026-08-08 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'align_clips_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly_cents', sa.Integer(), nullable=False),
        sa.Column('price_annual_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('max_projects', sa.Integer(), nullable=False),
        sa.Column('max_media_uploads', sa.Integer(), nullable=False),
        sa.Column('max_processing_minutes', sa.Integer(), nullable=False),
        sa.Column('max_ai_generations', sa.Integer(), nullable=False),
        sa.Column('max_storage_bytes', sa.BigInteger(), nullable=False),
        sa.Column('priority_processing', sa.Boolean(), nullable=False),
        sa.Column('creator_intelligence_advanced', sa.Boolean(), nullable=False),
        sa.Column('api_access', sa.Boolean(), nullable=False),
        sa.Column('team_workspaces', sa.Boolean(), nullable=False),
        sa.Column('enterprise_support', sa.Boolean(), nullable=False),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_plans_key'), 'plans', ['key'], unique=True)
    op.create_index(op.f('ix_plans_id'), 'plans', ['id'], unique=False)

    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_invoice_id', sa.String(length=255), nullable=False),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('invoice_url', sa.String(length=500), nullable=True),
        sa.Column('invoice_pdf', sa.String(length=500), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_invoices_user_id'), 'invoices', ['user_id'], unique=False)
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_provider_invoice_id'), 'invoices', ['provider_invoice_id'], unique=True)

    op.create_table(
        'payment_methods',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_payment_method_id', sa.String(length=255), nullable=False),
        sa.Column('brand', sa.String(length=50), nullable=True),
        sa.Column('last4', sa.String(length=4), nullable=True),
        sa.Column('exp_month', sa.Integer(), nullable=True),
        sa.Column('exp_year', sa.Integer(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_payment_methods_user_id'), 'payment_methods', ['user_id'], unique=False)
    op.create_index(op.f('ix_payment_methods_id'), 'payment_methods', ['id'], unique=False)
    op.create_index(op.f('ix_payment_methods_provider_payment_method_id'), 'payment_methods', ['provider_payment_method_id'], unique=True)

    op.add_column('user_subscriptions', sa.Column('plan_id', sa.Integer(), nullable=True))
    op.add_column('user_subscriptions', sa.Column('billing_cycle', sa.String(length=20), nullable=False, server_default='monthly'))
    op.add_column('user_subscriptions', sa.Column('provider_customer_id', sa.String(length=255), nullable=True))
    op.add_column('user_subscriptions', sa.Column('provider_subscription_id', sa.String(length=255), nullable=True))
    op.add_column('user_subscriptions', sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user_subscriptions', sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True))
    op.add_column('user_subscriptions', sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user_subscriptions', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_user_subscriptions_plan_id', 'user_subscriptions', 'plans', ['plan_id'], ['id'], ondelete='SET NULL')

    op.add_column('usage_records', sa.Column('media_uploads', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('usage_records', sa.Column('processing_seconds', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('usage_records', sa.Column('ai_generations', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('usage_records', sa.Column('storage_bytes', sa.BigInteger(), nullable=False, server_default='0'))
    op.drop_column('usage_records', 'hours_processed')
    op.drop_column('usage_records', 'campaign_packs_generated')
    op.drop_column('user_subscriptions', 'plan_name')


def downgrade() -> None:
    op.add_column('user_subscriptions', sa.Column('plan_name', sa.String(length=50), nullable=False, server_default='starter'))
    op.add_column('usage_records', sa.Column('campaign_packs_generated', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('usage_records', sa.Column('hours_processed', sa.Float(), nullable=False, server_default='0'))
    op.drop_constraint('fk_user_subscriptions_plan_id', 'user_subscriptions', type_='foreignkey')
    op.drop_column('user_subscriptions', 'cancelled_at')
    op.drop_column('user_subscriptions', 'cancel_at_period_end')
    op.drop_column('user_subscriptions', 'current_period_end')
    op.drop_column('user_subscriptions', 'current_period_start')
    op.drop_column('user_subscriptions', 'provider_subscription_id')
    op.drop_column('user_subscriptions', 'provider_customer_id')
    op.drop_column('user_subscriptions', 'billing_cycle')
    op.drop_column('user_subscriptions', 'plan_id')

    op.drop_column('usage_records', 'storage_bytes')
    op.drop_column('usage_records', 'ai_generations')
    op.drop_column('usage_records', 'processing_seconds')
    op.drop_column('usage_records', 'media_uploads')

    op.drop_index(op.f('ix_payment_methods_provider_payment_method_id'), table_name='payment_methods')
    op.drop_index(op.f('ix_payment_methods_id'), table_name='payment_methods')
    op.drop_index(op.f('ix_payment_methods_user_id'), table_name='payment_methods')
    op.drop_table('payment_methods')

    op.drop_index(op.f('ix_invoices_provider_invoice_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_user_id'), table_name='invoices')
    op.drop_table('invoices')

    op.drop_index(op.f('ix_plans_key'), table_name='plans')
    op.drop_index(op.f('ix_plans_id'), table_name='plans')
    op.drop_table('plans')
