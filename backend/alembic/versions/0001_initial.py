"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2025-12-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)

    op.create_table(
        'skills',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=32), nullable=True),
        sa.Column('type', sa.Enum('hard', 'soft', name='skilltype', create_type=False), nullable=False),
    )
    op.create_index('ix_skills_name', 'skills', ['name'], unique=False)

    op.create_table(
        'organizers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('login', sa.String(length=128), nullable=True),
        sa.Column('password_hash', sa.String(length=64), nullable=True),
    )
    op.create_index('uq_organizers_login', 'organizers', ['login'], unique=True)

    op.create_table(
        'hackathons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('max_teams', sa.Integer(), nullable=True),
        sa.Column('min_team_size', sa.Integer(), nullable=True),
        sa.Column('max_team_size', sa.Integer(), nullable=True),
        sa.Column('organizer_id', sa.Integer(), sa.ForeignKey('organizers.id'), nullable=True),
    )
    op.create_index('ix_hackathons_name', 'hackathons', ['name'], unique=False)
    op.create_index('ix_hackathons_organizer_id', 'hackathons', ['organizer_id'], unique=False)

    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hackathon_id', sa.Integer(), sa.ForeignKey('hackathons.id'), nullable=True),
        sa.Column('name', sa.String(length=32), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
    )
    op.create_index('ix_teams_hackathon_id', 'teams', ['hackathon_id'], unique=False)
    op.create_index('ix_teams_name', 'teams', ['name'], unique=False)

    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('role', sa.Enum('backend', 'frontend', 'mobile', 'ml', 'product', 'designer', name='roletype', create_type=False), nullable=False),
        sa.Column('about', sa.String(length=512), nullable=True),
    )
    op.create_index('ix_profiles_user_id', 'profiles', ['user_id'], unique=False)

    op.create_table(
        'profile_skills',
        sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profiles.id'), primary_key=True, nullable=False),
        sa.Column('skill_id', sa.Integer(), sa.ForeignKey('skills.id'), primary_key=True, nullable=False),
    )

    op.create_table(
        'team_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('teams.id'), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('role', sa.Enum('backend', 'frontend', 'mobile', 'ml', 'product', 'designer', name='roletype', create_type=False), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=True),
    )
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'], unique=False)
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_team_members_user_id', table_name='team_members')
    op.drop_index('ix_team_members_team_id', table_name='team_members')
    op.drop_table('team_members')

    op.drop_table('profile_skills')

    op.drop_index('ix_profiles_user_id', table_name='profiles')
    op.drop_table('profiles')

    op.drop_index('ix_teams_name', table_name='teams')
    op.drop_index('ix_teams_hackathon_id', table_name='teams')
    op.drop_table('teams')

    op.drop_index('ix_hackathons_organizer_id', table_name='hackathons')
    op.drop_index('ix_hackathons_name', table_name='hackathons')
    op.drop_table('hackathons')

    op.drop_index('uq_organizers_login', table_name='organizers')
    op.drop_table('organizers')

    op.drop_index('ix_skills_name', table_name='skills')
    op.drop_table('skills')

    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')

    # Drop enum types
    role_enum = postgresql.ENUM(name='roletype')
    role_enum.drop(op.get_bind())

    skill_enum = postgresql.ENUM(name='skilltype')
    skill_enum.drop(op.get_bind())
