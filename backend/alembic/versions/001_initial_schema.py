"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-06-04 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Enable gen_random_uuid extension if not already loaded
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    # 2. Enums
    # Postgres specific types
    user_role_enum = postgresql.ENUM('admin', 'senior_manager', 'hr_recruiter', 'employee', name='user_role')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    employment_type_enum = postgresql.ENUM('full_time', 'part_time', 'contract', 'intern', name='employment_type')
    employment_type_enum.create(op.get_bind(), checkfirst=True)

    employment_status_enum = postgresql.ENUM('active', 'on_leave', 'notice_period', 'terminated', name='employment_status')
    employment_status_enum.create(op.get_bind(), checkfirst=True)

    document_type_enum = postgresql.ENUM('aadhar', 'pan', 'passport', 'offer_letter', 'experience_letter', 'payslip', 'other', name='document_type')
    document_type_enum.create(op.get_bind(), checkfirst=True)

    proficiency_level_enum = postgresql.ENUM('beginner', 'intermediate', 'advanced', 'expert', name='proficiency_level')
    proficiency_level_enum.create(op.get_bind(), checkfirst=True)

    job_status_enum = postgresql.ENUM('draft', 'open', 'paused', 'closed', name='job_status')
    job_status_enum.create(op.get_bind(), checkfirst=True)

    application_stage_enum = postgresql.ENUM('applied', 'ai_screening', 'shortlisted', 'interview', 'technical', 'hr_round', 'offered', 'hired', 'rejected', name='application_stage')
    application_stage_enum.create(op.get_bind(), checkfirst=True)

    offer_status_enum = postgresql.ENUM('pending', 'accepted', 'rejected', 'expired', name='offer_status')
    offer_status_enum.create(op.get_bind(), checkfirst=True)

    attendance_status_enum = postgresql.ENUM('present', 'absent', 'late', 'half_day', 'on_leave', 'holiday', name='attendance_status')
    attendance_status_enum.create(op.get_bind(), checkfirst=True)

    regularization_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', name='regularization_status')
    regularization_status_enum.create(op.get_bind(), checkfirst=True)

    leave_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'cancelled', name='leave_status')
    leave_status_enum.create(op.get_bind(), checkfirst=True)

    payroll_status_enum = postgresql.ENUM('draft', 'computing', 'computed', 'approved', 'paid', name='payroll_status')
    payroll_status_enum.create(op.get_bind(), checkfirst=True)

    cycle_type_enum = postgresql.ENUM('quarterly', 'half_yearly', 'annual', name='cycle_type')
    cycle_type_enum.create(op.get_bind(), checkfirst=True)

    cycle_status_enum = postgresql.ENUM('upcoming', 'active', 'review', 'completed', name='cycle_status')
    cycle_status_enum.create(op.get_bind(), checkfirst=True)

    goal_status_enum = postgresql.ENUM('not_started', 'in_progress', 'completed', 'deferred', name='goal_status')
    goal_status_enum.create(op.get_bind(), checkfirst=True)

    review_type_enum = postgresql.ENUM('self_review', 'manager_review', 'peer_review', name='review_type')
    review_type_enum.create(op.get_bind(), checkfirst=True)

    # 3. Create Tables in dependency order
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('logo_url', sa.String(512), nullable=True),
        sa.Column('timezone', sa.String(64), nullable=False, server_default='UTC'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_companies_slug', 'companies', ['slug'], unique=True)

    op.create_table(
        'departments',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'name', name='uq_department_company_name')
    )
    op.create_index('ix_departments_company_id', 'departments', ['company_id'])

    op.create_table(
        'designations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('department_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'title', name='uq_designation_company_title')
    )
    op.create_index('ix_designations_company_id', 'designations', ['company_id'])

    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'senior_manager', 'hr_recruiter', 'employee', name='user_role', create_type=False), nullable=False, server_default='employee'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_2fa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'email', name='uq_user_company_email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_company_id', 'users', ['company_id'])

    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])

    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index('ix_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
    op.create_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])

    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False, server_default='system'),
        sa.Column('action_url', sa.String(512), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    op.create_table(
        'employees',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('employee_code', sa.String(50), nullable=False),
        sa.Column('first_name', sa.String(128), nullable=False),
        sa.Column('last_name', sa.String(128), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('personal_email', sa.String(255), nullable=True),
        sa.Column('address', postgresql.JSONB(), nullable=True),
        sa.Column('emergency_contact', postgresql.JSONB(), nullable=True),
        sa.Column('date_of_joining', sa.Date(), nullable=False),
        sa.Column('employment_type', postgresql.ENUM('full_time', 'part_time', 'contract', 'intern', name='employment_type', create_type=False), nullable=False),
        sa.Column('employment_status', postgresql.ENUM('active', 'on_leave', 'notice_period', 'terminated', name='employment_status', create_type=False), nullable=False, server_default='active'),
        sa.Column('department_id', sa.UUID(), nullable=True),
        sa.Column('designation_id', sa.UUID(), nullable=True),
        sa.Column('reporting_manager_id', sa.UUID(), nullable=True),
        sa.Column('work_location', sa.String(255), nullable=True),
        sa.Column('profile_photo_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['designation_id'], ['designations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['reporting_manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_code')
    )
    op.create_index('ix_employees_company_id', 'employees', ['company_id'])
    op.create_index('ix_employees_employee_code', 'employees', ['employee_code'])
    op.create_index('ix_employees_department_id', 'employees', ['department_id'])
    op.create_index('ix_employees_user_id', 'employees', ['user_id'])

    op.create_table(
        'skills',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('category', sa.String(128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_skills_name', 'skills', ['name'])

    op.create_table(
        'employee_skills',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('skill_id', sa.UUID(), nullable=False),
        sa.Column('proficiency', postgresql.ENUM('beginner', 'intermediate', 'advanced', 'expert', name='proficiency_level', create_type=False), nullable=False, server_default='beginner'),
        sa.Column('years_experience', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'skill_id', name='uq_employee_skill')
    )
    op.create_index('ix_employee_skills_employee_id', 'employee_skills', ['employee_id'])

    op.create_table(
        'employment_history',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('previous_value', postgresql.JSONB(), nullable=True),
        sa.Column('new_value', postgresql.JSONB(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('recorded_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employment_history_employee_id', 'employment_history', ['employee_id'])

    op.create_table(
        'employee_documents',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('document_type', postgresql.ENUM('aadhar', 'pan', 'passport', 'offer_letter', 'experience_letter', 'payslip', 'other', name='document_type', create_type=False), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_url', sa.String(512), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employee_documents_employee_id', 'employee_documents', ['employee_id'])

    # 4. Recruitment Tables
    op.create_table(
        'job_postings',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('department_id', sa.UUID(), nullable=True),
        sa.Column('employment_type', sa.String(50), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('salary_min', sa.Numeric(12, 2), nullable=True),
        sa.Column('salary_max', sa.Numeric(12, 2), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('experience_min', sa.Integer(), nullable=True),
        sa.Column('experience_max', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'open', 'paused', 'closed', name='job_status', create_type=False), nullable=False, server_default='draft'),
        sa.Column('posted_by', sa.UUID(), nullable=True),
        sa.Column('openings_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('deadline', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_postings_company_id', 'job_postings', ['company_id'])
    op.create_index('ix_job_postings_department_id', 'job_postings', ['department_id'])
    op.create_index('ix_job_postings_status', 'job_postings', ['status'])

    op.create_table(
        'candidates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('first_name', sa.String(128), nullable=False),
        sa.Column('last_name', sa.String(128), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('linkedin_url', sa.String(512), nullable=True),
        sa.Column('resume_url', sa.String(512), nullable=True),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'email', name='uq_candidate_company_email')
    )
    op.create_index('ix_candidates_company_id', 'candidates', ['company_id'])
    op.create_index('ix_candidates_email', 'candidates', ['email'])

    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('job_posting_id', sa.UUID(), nullable=False),
        sa.Column('candidate_id', sa.UUID(), nullable=False),
        sa.Column('stage', postgresql.ENUM('applied', 'ai_screening', 'shortlisted', 'interview', 'technical', 'hr_round', 'offered', 'hired', 'rejected', name='application_stage', create_type=False), nullable=False, server_default='applied'),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('current_ctc', sa.Numeric(12, 2), nullable=True),
        sa.Column('expected_ctc', sa.Numeric(12, 2), nullable=True),
        sa.Column('notice_period_days', sa.Integer(), nullable=True),
        sa.Column('stage_history', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_posting_id', 'candidate_id', name='uq_application_job_candidate')
    )
    op.create_index('ix_applications_job_posting_id', 'applications', ['job_posting_id'])
    op.create_index('ix_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('ix_applications_stage', 'applications', ['stage'])

    op.create_table(
        'ai_evaluations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('fit_score', sa.Float(), nullable=True),
        sa.Column('skill_match_score', sa.Float(), nullable=True),
        sa.Column('experience_score', sa.Float(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('strengths', postgresql.JSONB(), nullable=True),
        sa.Column('weaknesses', postgresql.JSONB(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('human_override', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('override_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )
    op.create_index('ix_ai_evaluations_application_id', 'ai_evaluations', ['application_id'], unique=True)

    op.create_table(
        'voice_screenings',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('audio_url', sa.String(512), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('ai_evaluation', postgresql.JSONB(), nullable=True),
        sa.Column('overall_voice_score', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_voice_screenings_application_id', 'voice_screenings', ['application_id'])

    op.create_table(
        'interview_questions',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('job_posting_id', sa.UUID(), nullable=False),
        sa.Column('questions', postgresql.JSONB(), nullable=True),
        sa.Column('generated_by_ai', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['job_posting_id'], ['job_postings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interview_questions_job_posting_id', 'interview_questions', ['job_posting_id'])

    op.create_table(
        'offers',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('application_id', sa.UUID(), nullable=False),
        sa.Column('offered_salary', sa.Numeric(12, 2), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'accepted', 'rejected', 'expired', name='offer_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('application_id')
    )
    op.create_index('ix_offers_application_id', 'offers', ['application_id'], unique=True)

    # 5. Attendance Tables
    op.create_table(
        'attendance_logs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('clock_in', sa.DateTime(timezone=True), nullable=False),
        sa.Column('clock_out', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_hours', sa.Float(), nullable=True),
        sa.Column('status', postgresql.ENUM('present', 'absent', 'late', 'half_day', 'on_leave', 'holiday', name='attendance_status', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'date', name='uq_attendance_employee_date')
    )
    op.create_index('ix_attendance_logs_employee_id', 'attendance_logs', ['employee_id'])
    op.create_index('ix_attendance_logs_date', 'attendance_logs', ['date'])

    op.create_table(
        'attendance_regularizations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('requested_clock_in', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requested_clock_out', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', name='regularization_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('approved_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attendance_regularizations_employee_id', 'attendance_regularizations', ['employee_id'])

    # 6. Leave Tables
    op.create_table(
        'leave_types',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('annual_quota', sa.Integer(), nullable=False),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('carry_forward', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'code', name='uq_leave_type_company_code')
    )
    op.create_index('ix_leave_types_company_id', 'leave_types', ['company_id'])

    op.create_table(
        'leave_balances',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('leave_type_id', sa.UUID(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('allocated', sa.Float(), nullable=False),
        sa.Column('used', sa.Float(), nullable=False, server_default='0'),
        sa.Column('pending', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'leave_type_id', 'year', name='uq_leave_balance_employee_type_year')
    )
    op.create_index('ix_leave_balances_employee_id', 'leave_balances', ['employee_id'])

    op.create_table(
        'leave_requests',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('leave_type_id', sa.UUID(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('days_count', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'rejected', 'cancelled', name='leave_status', create_type=False), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_requests_employee_id', 'leave_requests', ['employee_id'])
    op.create_index('ix_leave_requests_status', 'leave_requests', ['status'])

    op.create_table(
        'leave_approvals',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('leave_request_id', sa.UUID(), nullable=False),
        sa.Column('approver_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('actioned_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['leave_request_id'], ['leave_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_approvals_leave_request_id', 'leave_approvals', ['leave_request_id'])

    op.create_table(
        'holidays',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('is_optional', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'date', name='uq_holiday_company_date')
    )
    op.create_index('ix_holidays_company_id', 'holidays', ['company_id'])

    # 7. Payroll Tables
    op.create_table(
        'salary_structures',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('components', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_salary_structures_company_id', 'salary_structures', ['company_id'])

    op.create_table(
        'employee_salaries',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('salary_structure_id', sa.UUID(), nullable=True),
        sa.Column('gross_salary', sa.Numeric(14, 2), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['salary_structure_id'], ['salary_structures.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employee_salaries_employee_id', 'employee_salaries', ['employee_id'])

    op.create_table(
        'payroll_runs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'computing', 'computed', 'approved', 'paid', name='payroll_status', create_type=False), nullable=False, server_default='draft'),
        sa.Column('total_gross', sa.Numeric(16, 2), nullable=True),
        sa.Column('total_net', sa.Numeric(16, 2), nullable=True),
        sa.Column('initiated_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'month', 'year', name='uq_payroll_run_company_month_year')
    )
    op.create_index('ix_payroll_runs_company_id', 'payroll_runs', ['company_id'])

    op.create_table(
        'payroll_entries',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('payroll_run_id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('gross_salary', sa.Numeric(14, 2), nullable=False),
        sa.Column('basic', sa.Numeric(14, 2), nullable=False),
        sa.Column('hra', sa.Numeric(14, 2), nullable=False),
        sa.Column('allowances', postgresql.JSONB(), nullable=True),
        sa.Column('pf_deduction', sa.Numeric(14, 2), nullable=False),
        sa.Column('esi_deduction', sa.Numeric(14, 2), nullable=False),
        sa.Column('tds_deduction', sa.Numeric(14, 2), nullable=False),
        sa.Column('lop_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lop_deduction', sa.Numeric(14, 2), nullable=False, server_default='0'),
        sa.Column('net_salary', sa.Numeric(14, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payroll_entries_payroll_run_id', 'payroll_entries', ['payroll_run_id'])
    op.create_index('ix_payroll_entries_employee_id', 'payroll_entries', ['employee_id'])

    # 8. Performance Tables
    op.create_table(
        'performance_cycles',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('cycle_type', postgresql.ENUM('quarterly', 'half_yearly', 'annual', name='cycle_type', create_type=False), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('review_start', sa.Date(), nullable=False),
        sa.Column('review_end', sa.Date(), nullable=False),
        sa.Column('status', postgresql.ENUM('upcoming', 'active', 'review', 'completed', name='cycle_status', create_type=False), nullable=False, server_default='upcoming'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_cycles_company_id', 'performance_cycles', ['company_id'])
    op.create_index('ix_performance_cycles_status', 'performance_cycles', ['status'])

    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('cycle_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('key_results', postgresql.JSONB(), nullable=True),
        sa.Column('weightage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'completed', 'deferred', name='goal_status', create_type=False), nullable=False, server_default='not_started'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cycle_id'], ['performance_cycles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_goals_company_id', 'goals', ['company_id'])
    op.create_index('ix_goals_employee_id', 'goals', ['employee_id'])
    op.create_index('ix_goals_cycle_id', 'goals', ['cycle_id'])

    op.create_table(
        'performance_reviews',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('cycle_id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('reviewer_id', sa.UUID(), nullable=True),
        sa.Column('review_type', postgresql.ENUM('self_review', 'manager_review', 'peer_review', name='review_type', create_type=False), nullable=False),
        sa.Column('ratings', postgresql.JSONB(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['performance_cycles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_reviews_cycle_id', 'performance_reviews', ['cycle_id'])
    op.create_index('ix_performance_reviews_employee_id', 'performance_reviews', ['employee_id'])
    op.create_index('ix_performance_reviews_reviewer_id', 'performance_reviews', ['reviewer_id'])

    op.create_table(
        'performance_scores',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('cycle_id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('goal_score', sa.Float(), nullable=True),
        sa.Column('self_score', sa.Float(), nullable=True),
        sa.Column('manager_score', sa.Float(), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('ai_promotion_score', sa.Float(), nullable=True),
        sa.Column('ai_attrition_risk', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['performance_cycles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cycle_id', 'employee_id', name='uq_performance_score_cycle_employee')
    )
    op.create_index('ix_performance_scores_cycle_id', 'performance_scores', ['cycle_id'])
    op.create_index('ix_performance_scores_employee_id', 'performance_scores', ['employee_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('notifications')
    op.drop_table('performance_scores')
    op.drop_table('performance_reviews')
    op.drop_table('goals')
    op.drop_table('performance_cycles')
    op.drop_table('payroll_entries')
    op.drop_table('payroll_runs')
    op.drop_table('employee_salaries')
    op.drop_table('salary_structures')
    op.drop_table('holidays')
    op.drop_table('leave_approvals')
    op.drop_table('leave_requests')
    op.drop_table('leave_balances')
    op.drop_table('leave_types')
    op.drop_table('attendance_regularizations')
    op.drop_table('attendance_logs')
    op.drop_table('offers')
    op.drop_table('interview_questions')
    op.drop_table('voice_screenings')
    op.drop_table('ai_evaluations')
    op.drop_table('applications')
    op.drop_table('candidates')
    op.drop_table('job_postings')
    op.drop_table('employee_documents')
    op.drop_table('employment_history')
    op.drop_table('employee_skills')
    op.drop_table('skills')
    op.drop_table('employees')
    op.drop_table('password_reset_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    op.drop_table('designations')
    op.drop_table('departments')
    op.drop_table('companies')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS review_type")
    op.execute("DROP TYPE IF EXISTS goal_status")
    op.execute("DROP TYPE IF EXISTS cycle_status")
    op.execute("DROP TYPE IF EXISTS cycle_type")
    op.execute("DROP TYPE IF EXISTS payroll_status")
    op.execute("DROP TYPE IF EXISTS leave_status")
    op.execute("DROP TYPE IF EXISTS regularization_status")
    op.execute("DROP TYPE IF EXISTS attendance_status")
    op.execute("DROP TYPE IF EXISTS offer_status")
    op.execute("DROP TYPE IF EXISTS application_stage")
    op.execute("DROP TYPE IF EXISTS job_status")
    op.execute("DROP TYPE IF EXISTS proficiency_level")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS employment_status")
    op.execute("DROP TYPE IF EXISTS employment_type")
    op.execute("DROP TYPE IF EXISTS user_role")
