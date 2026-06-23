# ArchTrack - Architecture Decision Records Management System

> A collaborative platform for managing Architecture Decision Records (ADRs) with multi-tenant support, role-based access control, and structured review workflows.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136.3-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.50-red)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Required-336791?logo=postgresql)](https://www.postgresql.org/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Security & Authentication](#security--authentication)
- [Decision Workflow](#decision-workflow)
- [Role-Based Access Control](#role-based-access-control)
- [Development Guidelines](#development-guidelines)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

ArchTrack is a comprehensive backend system for managing Architecture Decision Records (ADRs) in software development teams. It provides a structured approach to documenting, reviewing, and tracking architectural decisions throughout the software development lifecycle.

### Key Capabilities

- **Multi-Tenant Architecture**: Isolated workspaces for organizations with team-based structures
- **Structured Decision Management**: Create, review, and track architectural decisions with context, consequences, and alternatives
- **Collaborative Review Process**: Assign reviewers, collect verdicts, and maintain decision audit trails
- **Role-Based Permissions**: Fine-grained access control across org admins, team admins, architects, and developers
- **Project Organization**: Group decisions by projects with tagging and filtering capabilities

---

## ✨ Features

### Core Functionality

- **🏢 Organization Management**
  - Multi-tenant isolation with organization-scoped queries
  - Custom organization slugs and branding
  - Organization-level settings and configurations

- **👥 Team Collaboration**
  - Team-based user organization within organizations
  - Email invitation system with secure token-based registration
  - Team admin capabilities for user management

- **📝 Decision Records**
  - Structured ADR format (Context, Decision, Consequences)
  - Multiple decision options with voting capabilities
  - Tag-based categorization and filtering
  - Status-based workflow (Proposed → Under Review → Accepted/Rejected)
  - Full audit trail for all decision changes

- **🔍 Review System**
  - Reviewer assignment by decision authors
  - Structured review comments and verdicts
  - One verdict per reviewer constraint
  - Review status tracking and notifications

- **💬 Collaboration Features**
  - Decision comments and discussions
  - Real-time voting on decision options
  - Project-level organization
  - Advanced filtering (by status, tags, projects)

### Technical Features

- **RESTful API** with FastAPI framework
- **JWT-based authentication** with secure token management
- **PostgreSQL database** with SSL support
- **Multi-tenant data isolation** using organization-scoped queries
- **CORS support** for frontend integration
- **Comprehensive validation** with Pydantic schemas

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.136.3 |
| **Language** | Python | 3.9+ |
| **Database** | PostgreSQL | - |
| **ORM** | SQLAlchemy | 2.0.50 |
| **Authentication** | JWT (python-jose) | 3.5.0 |
| **Password Hashing** | Bcrypt (passlib) | 1.7.4 |
| **Validation** | Pydantic | 2.13.4 |
| **Server** | Uvicorn | 0.49.0 |

### Project Structure

```
Backend/
├── app/
│   ├── db/
│   │   ├── database.py          # Database connection & session management
│   │   └── __init__.py
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── organizations.py     # Organization entity
│   │   ├── teams.py             # Team entity
│   │   ├── users.py             # User entity with roles
│   │   ├── projects.py          # Project entity
│   │   ├── decisions.py         # Decision & reviewer assignment
│   │   ├── options.py           # Decision options
│   │   ├── votes.py             # Voting system
│   │   ├── comments.py          # Decision comments
│   │   ├── reviewcomments.py    # Review verdicts
│   │   ├── tags.py              # Tagging system
│   │   ├── invites.py           # Team invitation system
│   │   └── decisionaudits.py    # Audit trail
│   ├── routers/                 # API route handlers
│   │   ├── auth.py              # Authentication & registration
│   │   ├── admin.py             # Organization admin operations
│   │   ├── Organizations.py     # Organization management
│   │   ├── Teams.py             # Team management
│   │   ├── Invites.py           # Invitation handling
│   │   ├── Projects.py          # Project CRUD
│   │   ├── Decisions.py         # Decision CRUD & workflow
│   │   ├── ReviewerAssignments.py  # Review management
│   │   ├── Options.py           # Decision options
│   │   ├── Votes.py             # Voting endpoints
│   │   ├── Comments.py          # Comment system
│   │   └── Tags.py              # Tag management
│   ├── schemas/                 # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── team.py
│   │   ├── project.py
│   │   ├── decision.py
│   │   ├── invite.py
│   │   └── ...
│   ├── utils/                   # Utility modules
│   │   ├── oauth2.py            # JWT token handling
│   │   ├── hashing.py           # Password hashing
│   │   ├── permissions.py       # Authorization checks
│   │   ├── org_query.py         # Organization-scoped queries
│   │   ├── context.py           # Request context management
│   │   ├── workflow.py          # Decision workflow logic
│   │   └── token_generator.py   # Invitation token generation
│   ├── config.py                # Application configuration
│   └── __init__.py
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
└── CONTRIBUTING.md              # Development guidelines

```

### Multi-Tenant Architecture

The system implements strict multi-tenant isolation using the `OrgScopedQuery` pattern:

```python
# All route handlers must use organization-scoped queries
projects = sq.projects().all()      # ✅ Correct
projects = db.query(Project).all()  # ❌ Forbidden
```

This ensures data isolation between organizations and prevents cross-tenant data leaks.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** installed on your system
- **PostgreSQL** database instance (with SSL support)
- **pip** package manager
- **Git** for version control

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd Backend
```

2. **Create and activate virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Initialize the database**

The application will automatically create all required tables on startup using SQLAlchemy's `Base.metadata.create_all()`.

6. **Run the application**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### First-Time Setup (Bootstrap)

Create your first organization and admin user:

```bash
POST /auth/bootstrap
{
  "org_name": "Your Organization",
  "org_slug": "your-org",
  "admin_email": "admin@example.com",
  "admin_password": "secure-password"
}
```

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints Overview

#### Authentication (`/auth`)
- `POST /auth/login` - User login (returns JWT token)
- `POST /auth/bootstrap` - First-time organization setup
- `POST /auth/register` - Register via team invitation
- `GET /auth/invite-info` - Get invitation details
- `GET /auth/me` - Get current user profile

#### Organizations (`/organizations`)
- `GET /organizations/me` - Get organization details
- `PUT /organizations/me` - Update organization (org admin only)

#### Teams (`/teams`)
- `POST /teams` - Create team (org admin only)
- `GET /teams` - List all teams
- `PUT /teams/{id}` - Update team
- `DELETE /teams/{id}` - Delete team

#### Invitations (`/invites`)
- `POST /invites/team/{team_id}` - Create team invitation
- `GET /invites/team/{team_id}/pending` - List pending invites
- `DELETE /invites/{id}` - Revoke invitation

#### Projects (`/projects`)
- `POST /projects` - Create project
- `GET /projects` - List all projects
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

#### Decisions (`/decisions`)
- `POST /decisions/project/{project_id}` - Create decision
- `GET /decisions/project/{project_id}` - List decisions (with filters)
- `GET /decisions/{id}` - Get decision details
- `PUT /decisions/{id}` - Update decision
- `PUT /decisions/{id}/status` - Update decision status

#### Reviewers (`/reviewers`)
- `POST /reviewers/decision/{id}` - Assign reviewer
- `DELETE /reviewers/decision/{id}/reviewer/{reviewer_id}` - Remove reviewer
- `POST /reviewers/decision/{id}/verdict` - Submit review verdict
- `GET /reviewers/decision/{id}/reviews` - Get all verdicts

#### Options (`/options`)
- `POST /options/decision/{decision_id}` - Add decision option
- `DELETE /options/{id}` - Delete option

#### Votes (`/votes`)
- `POST /votes` - Cast vote on option
- Additional voting endpoints...

#### Comments (`/comments`)
- `POST /comments/decision/{decision_id}` - Add comment
- `DELETE /comments/{id}` - Delete comment

#### Tags (`/tags`)
- `GET /tags` - List all tags

#### Admin (`/admin`)
- `GET /admin/users` - List all users with roles
- `PUT /admin/users/{id}/role` - Change user role
- `DELETE /admin/users/{id}` - Remove user
- `GET /admin/projects` - List all projects
- `PUT /admin/decisions/{id}/status/override` - Override decision status

---

## 🗄️ Database Schema

### Core Entities

#### Organizations
- Multi-tenant root entity
- Unique slug for URL-friendly identification
- Contains teams, users, and projects

#### Teams
- Group users within an organization
- Team-level permissions and invitations
- Many-to-many relationship with users

#### Users
- Email-based authentication
- Role-based access (org_admin, team_admin, architect, developer)
- Belongs to one organization and optionally one team

#### Projects
- Logical grouping of decisions
- Owned by users within an organization
- Can be archived or deleted

#### Decisions
- Core ADR entity with context, decision, and consequences
- Status-based workflow (StatusEnum)
- Many-to-many relationship with reviewers
- Belongs to a project and authored by a user

#### Decision Options
- Alternative solutions for a decision
- Supports voting by team members

#### Votes
- User votes on decision options
- One vote per user per decision

#### Comments
- Discussion threads on decisions
- Authored by users

#### Review Comments
- Formal review verdicts (approve/reject)
- One verdict per assigned reviewer per decision

#### Tags
- Categorization and filtering mechanism
- Many-to-many relationship with decisions

#### Invites
- Secure token-based team invitations
- Email-based with expiration

#### Decision Audits
- Complete audit trail of all decision changes
- Tracks status changes and modifications

### Entity Relationships

```
Organization (1) ──< (N) Teams
Organization (1) ──< (N) Users
Organization (1) ──< (N) Projects

Team (1) ──< (N) Users
Team (1) ──< (N) Invites

Project (1) ──< (N) Decisions

Decision (1) ──< (N) Options
Decision (1) ──< (N) Comments
Decision (1) ──< (N) Review Comments
Decision (1) ──< (N) Decision Audits
Decision (N) ──< (M) Tags
Decision (N) ──< (M) Users (as reviewers)

Option (1) ──< (N) Votes

User (1) ──< (N) Decisions (as author)
User (1) ──< (N) Projects (as owner)
User (1) ──< (N) Votes
User (1) ──< (N) Comments
```

```mermaid
erDiagram
    %% Base Organization and High-Level Scope
    Organization ||--|{ Teams : manages
    Organization ||--|{ Users : employs
    Organization ||--|{ Projects : encompasses

    %% Team Context and Onboarding
    Teams ||--|{ Users : belongs_to
    Teams ||--|{ Invites : sends_to

    %% Project Context
    Projects ||--|{ Decisions : produces

    %% User Roles/Ownership
    Users ||--|{ Projects : owns
    Users ||--|{ Decisions : authors
    Users ||--|{ Votes : casts
    Users ||--|{ Comments : writes
    Users ||--|{ ReviewComments : makes

    %% Decision Details and Lifecycle
    Decisions ||--|{ Options : provides
    Decisions ||--|{ Comments : receives
    Decisions ||--|{ ReviewComments : requires
    Decisions ||--|{ DecisionAudits : tracks

    %% Option/Voting Interaction
    Options ||--|{ Votes : gathers

    %% Many-to-Many Relationships (Implemented with Junction Tables)

    %% Decision <-> Tag (N:M)
    Decisions ||--|{ DecisionTags : has
    Tags ||--|{ DecisionTags : classifies

    %% Decision <-> User (as reviewers) (N:M)
    Decisions ||--|{ Reviewers : is_reviewed_by
    Users ||--|{ Reviewers : acts_as
```

---

### 📈 Load Testing & Performance Metrics

To evaluate API performance and concurrency handling, the backend was load-tested using Locust against a remote Supabase PostgreSQL database.

- Sustained Throughput: ~40 requests/second (RPS)
- Concurrent Load Tested: Up to 100 simulated users
- Observed Failure Rate: 0% at 30 concurrent users; failures at higher loads were caused by Supabase free-tier connection limits rather than application errors.
- Infrastructure Bottleneck: Encountered `EMAXCONNSESSION` when exceeding the database pool limit of 15 active sessions on Supabase.
- Authentication Analysis: Identified that every protected route performs a database lookup through JWT-based user resolution (`get_current_user()`), making database connections the primary scaling constraint under heavy load.

---
## 🔐 Security & Authentication

### JWT Token-Based Authentication

- **Algorithm**: HS256 (configurable)
- **Token Expiration**: 30 minutes (configurable)
- **Password Hashing**: Bcrypt with automatic salt generation

### Authentication Flow

1. User submits credentials via `/auth/login`
2. Server validates credentials and generates JWT token
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token on protected endpoints using `get_current_user` dependency

### Invitation System

- Secure token-based team invitations
- Tokens include org_id, team_id, inviter_id, and email
- Expiration checking on registration
- Prevents token reuse after successful registration

### Data Isolation

- All queries are organization-scoped using `OrgScopedQuery`
- Prevents cross-tenant data access
- Enforced at the database query level

---

## 🔄 Decision Workflow

### Status Flow

```text
Architect
---------
proposed → under_review
rejected → proposed

Reviewer
--------
under_review → accepted
under_review → rejected

Team Admin
----------
Can perform both Architect + Reviewer transitions

Org Admin
---------
Must use override endpoint for any status change
```

### Status Definitions

| Status | Description |
|--------|-------------|
| **proposed** | Initial state when decision is created |
| **under_review** | Decision is being reviewed by assigned reviewers |
| **accepted** | Decision has been approved by reviewers |
| **rejected** | Decision has been rejected by reviewers |
| **deprecated** | Decision is no longer recommended (but was once accepted) |
| **superseded** | Decision has been replaced by a newer decision |

### Review Process

1. **Decision Author** creates a decision (status: `proposed`)
2. **Author** assigns reviewers to the decision
3. **Author** transitions status to `under_review`
4. **Assigned Reviewers** submit their verdicts (approve/reject)
5. Based on verdicts, decision transitions to `accepted` or `rejected`
6. **Only assigned reviewers** can submit verdicts (one per reviewer)

### Workflow Rules

- Decision authors can assign/remove reviewers
- Only assigned reviewers can submit verdicts
- Each reviewer can submit exactly one verdict per decision
- Org admins can override any status using the admin endpoint
- All status changes are logged in the audit trail

---

## 👥 Role-Based Access Control

### User Roles

| Role | Permissions |
|------|-------------|
| **org_admin** | Full control over organization, teams, users, and all resources. Can override decision workflows. |
| **team_admin** | Manage team members, create invitations, manage team projects. Can perform both architect and reviewer transitions. |
| **architect** | Create and manage decisions, assign reviewers, manage decision status (within workflow rules). |
| **developer** | View decisions, vote on options, comment on decisions, participate as assigned reviewer. |

### Permission Contexts

The system uses three main context types for authorization:

1. **OrgContext**: Validates user belongs to the organization
2. **OrgAdminContext**: Requires org_admin role
3. **TeamAdminContext**: Requires team_admin or org_admin role

These are implemented as FastAPI dependencies:

```python
@router.post("/admin-only-endpoint")
def admin_endpoint(ctx: OrgContext = Depends(get_org_admin_context)):
    # Only org admins can access this
    pass
```

---

## 💻 Development Guidelines

### Code Quality Rules

#### ⚠️ CRITICAL: Organization-Scoped Queries

**All data queries in route handlers MUST use `OrgScopedQuery`.**

```python
# ✅ CORRECT
def get_projects(sq: OrgScopedQuery = Depends(get_scoped_query)):
    projects = sq.projects().all()
    return projects

# ❌ INCORRECT - Will be rejected in code review
def get_projects(db: SessionDB):
    projects = db.query(Project).all()  # Bypasses tenant isolation!
    return projects
```

**Allowed exceptions for raw `db.query()`:**
- Inside `get_scoped_query()` implementation
- `/auth/bootstrap` endpoint (first-time setup)
- `OrgScopedQuery` class implementation
- Global resources (e.g., Tag) that aren't tenant-scoped

### Best Practices

1. **Always use Pydantic schemas** for request/response validation
2. **Use dependency injection** for database sessions and authentication
3. **Handle errors gracefully** with appropriate HTTP status codes
4. **Log audit events** for all sensitive operations
5. **Validate permissions** at the route handler level
6. **Use transactions** for multi-step database operations
7. **Write tests** for all new features and bug fixes

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Style

- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep functions **focused and small** (single responsibility)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the development guidelines
4. Ensure all tests pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All route handlers use `OrgScopedQuery` (no raw `db.query()`)
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No breaking changes (or clearly documented)

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/NareshXcodes/ArchTrack/issues)
- **Documentation**: See `/docs` endpoint when running
- **Email**: codes.xdev@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- FastAPI framework for excellent async Python web development
- SQLAlchemy for robust ORM capabilities
- PostgreSQL for reliable multi-tenant data storage
- The open-source community for various dependencies

---

**Built with ❤️ for better architecture decision management**