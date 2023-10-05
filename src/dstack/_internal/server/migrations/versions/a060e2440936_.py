"""empty message

Revision ID: a060e2440936
Revises: 
Create Date: 2023-09-20 16:34:34.649303

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "a060e2440936"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("ssh_private_key", sa.Text(), nullable=False),
        sa.Column("ssh_public_key", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("name", name=op.f("uq_projects_name")),
    )
    op.create_table(
        "users",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("token", sa.String(length=200), nullable=False),
        sa.Column("global_role", sa.Enum("ADMIN", "USER", name="globalrole"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("name", name=op.f("uq_users_name")),
        sa.UniqueConstraint("token", name=op.f("uq_users_token")),
    )
    op.create_table(
        "backends",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column(
            "project_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column(
            "type", sa.Enum("AWS", "AZURE", "GCP", "LAMBDA", name="backendtype"), nullable=False
        ),
        sa.Column("config", sa.String(length=2000), nullable=False),
        sa.Column("auth", sa.String(length=2000), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_backends_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_backends")),
    )
    op.create_table(
        "members",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column(
            "project_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("project_role", sa.Enum("ADMIN", "USER", name="projectrole"), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_members_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_members_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_members")),
    )
    op.create_table(
        "repos",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column(
            "project_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.Enum("REMOTE", "LOCAL", name="repotype"), nullable=False),
        sa.Column("info", sa.String(length=2000), nullable=False),
        sa.Column("creds", sa.String(length=2000), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_repos_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repos")),
        sa.UniqueConstraint("project_id", "name", name="uq_repos_project_id_name"),
    )
    op.create_table(
        "runs",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column(
            "project_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("repo_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("user_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("run_name", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "SUBMITTED",
                "PROVISIONING",
                "RUNNING",
                "TERMINATING",
                "TERMINATED",
                "ABORTED",
                "FAILED",
                "DONE",
                name="jobstatus",
            ),
            nullable=False,
        ),
        sa.Column("run_spec", sa.String(length=4000), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_runs_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["repo_id"], ["repos.id"], name=op.f("fk_runs_repo_id_repos"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_runs_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_runs")),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column(
            "project_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False
        ),
        sa.Column("run_id", sqlalchemy_utils.types.uuid.UUIDType(binary=False), nullable=False),
        sa.Column("run_name", sa.String(length=100), nullable=False),
        sa.Column("job_num", sa.Integer(), nullable=False),
        sa.Column("job_name", sa.String(length=100), nullable=False),
        sa.Column("submission_num", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.Column("last_processed_at", sa.DateTime(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "SUBMITTED",
                "PROVISIONING",
                "RUNNING",
                "TERMINATING",
                "TERMINATED",
                "ABORTED",
                "FAILED",
                "DONE",
                name="jobstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "error_code",
            sa.Enum(
                "NO_INSTANCE_MATCHING_REQUIREMENTS",
                "FAILED_TO_START_DUE_TO_NO_CAPACITY",
                "INTERRUPTED_BY_NO_CAPACITY",
                "INSTANCE_TERMINATED",
                "CONTAINER_EXITED_WITH_ERROR",
                "PORTS_BINDING_FAILED",
                name="joberrorcode",
            ),
            nullable=True,
        ),
        sa.Column("job_spec_data", sa.String(length=4000), nullable=False),
        sa.Column("job_provisioning_data", sa.String(length=4000), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_jobs_project_id_projects"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["runs.id"], name=op.f("fk_jobs_run_id_runs"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jobs")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("jobs")
    op.drop_table("runs")
    op.drop_table("repos")
    op.drop_table("members")
    op.drop_table("backends")
    op.drop_table("users")
    op.drop_table("projects")
    # ### end Alembic commands ###
