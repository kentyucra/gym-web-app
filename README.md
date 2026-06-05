# Site Fitness Web App

Product plan for a new gym in Juliaca.

For local development startup instructions, see:

```txt
RUNNING_SERVICES.md
```

This should be treated as two products in one:

1. Gym Management System for staff and owners
2. Member Portal / Mobile App for customers

The MVP should solve the gym's daily operational problems first. Fancy AI features can come later.

## MVP Version 1

### 1. Member Management

This is the heart of the system.

#### Member Profile

Store:

- Full name
- DNI
- Date of birth
- Phone
- Email
- Address
- Emergency contact
- Medical notes
- Photo
- Join date
- Membership type
- Current status:
  - Active
  - Suspended
  - Expired
  - Cancelled

#### Benefits

Staff can quickly:

- Search members
- View membership status
- See payment history
- See attendance history

### 2. Membership & Subscription Management

#### Membership Plans

Examples:

| Plan | Price | Duration |
| --- | --- | --- |
| Monthly | S/120 | 30 days |
| Quarterly | S/300 | 90 days |
| Annual | S/1000 | 365 days |

#### Features

- Create plans
- Assign plans
- Renew memberships
- Freeze memberships
- Cancel memberships

#### Notifications

Send WhatsApp or email notifications for:

- Membership expiring in 7 days
- Membership expired
- Payment reminder

### 3. Check-In System

This is extremely valuable.

#### Options

Option A for MVP:

- Member enters DNI
- Member enters phone
- Member enters member ID

Option B:

- QR code
- Member scans QR at reception

Option C for the future:

- Biometric fingerprint check-in

#### Attendance Dashboard

Owner can see:

- Daily attendance
- Weekly attendance
- Monthly attendance
- Peak hours

Example:

| Day | Peak Time |
| --- | --- |
| Monday | 6pm to 9pm |

This is very useful for staffing decisions.

### 4. Member Portal

Members log in and can see:

- Dashboard
- Membership status
- Days remaining
- Next payment date
- Attendance

Example attendance:

| Date | Time |
| --- | --- |
| 01/06 | 07:12 |
| 02/06 | 06:58 |
| 04/06 | 07:05 |

This motivates consistency.

### 5. Exercise Library

This is a very useful differentiator.

#### Exercise Record

Store:

- Name
- Description
- Video
- Image
- Difficulty
- Equipment required
- Muscle groups

Examples:

| Exercise | Muscles |
| --- | --- |
| Bench Press | Chest, Triceps |
| Squat | Quads, Glutes |
| Deadlift | Back, Hamstrings |
| Pull Up | Lats, Biceps |

Members can browse by:

- Chest
- Back
- Legs
- Shoulders
- Arms
- Core

### 6. Group Classes

This should support dance classes and other group sessions.

#### Class Schedule

Example:

| Day | Class | Time |
| --- | --- | --- |
| Monday | Zumba | 7pm |
| Tuesday | Dance Fitness | 7pm |
| Thursday | Salsa | 8pm |

#### Weekly Notification

Every Sunday, send:

> These are this week's classes.

Send through:

- WhatsApp
- Email
- Push notification

## Features To Add Immediately

### Body Measurements

Track:

- Weight
- Body fat percentage
- Waist
- Chest
- Arms
- Legs

Show monthly progress. This creates retention.

### Progress Photos

Members upload:

- Front
- Side
- Back

Photos should be stored in a private gallery. This is a strong motivation tool.

### Trainer Notes

Trainer can record:

- Injuries
- Goals
- Recommendations

Example:

> Improve squat depth.

### Workout Programs

Create templates such as:

- Weight Loss
- Muscle Gain

Example weight loss program:

| Day | Exercises |
| --- | --- |
| Monday | Squat, Lunges, Walking |

Example muscle gain program:

| Day | Exercises |
| --- | --- |
| Monday | Bench Press, Incline Press, Flyes |

Trainers can assign plans to members.

## Version 2 Features

### AI Coach

Use LLMs so members can ask questions like:

> What exercises should I do for chest?

The AI should answer using the gym's exercise library.

### AI Workout Generator

Input:

- Goal: Lose weight
- Experience: Beginner
- Days: 4

Output:

- Custom workout program

## Supporting Services

### OpenWA

OpenWA can be used later for WhatsApp notifications, including member invites, payment reminders, expiration notices, and weekly class schedules.

Setup documentation lives in:

```txt
openWA/README.md
```

## Step-By-Step MVP Build Plan

The recommended build order for the first MVP is:

1. Project setup
2. Authentication and roles
3. Member management
4. Membership plans
5. Subscriptions and payments
6. Check-in system
7. Attendance dashboard
8. Member portal
9. Exercise library
10. Group classes
11. Notifications

The first true usable milestone is:

> Staff can register a member, assign a plan, take a payment, and check the member in.

That is the core of the gym business.

## Step 1: Project Setup

### Recommended Stack

Use the following stack for the MVP:

- Frontend: Next.js
- Frontend data fetching: TanStack Query, also known as useQuery
- UI components: shadcn/ui
- Backend: Flask API
- Database: PostgreSQL

This is a solid stack for the gym MVP because the application is very CRUD-heavy. The main workflows are members, plans, payments, subscriptions, attendance, classes, and exercises.

### Architecture

The app should be split into three main parts:

```txt
Next.js frontend
  - shadcn/ui components
  - TanStack Query for API data
  - auth/session handling
  - admin dashboard
  - member portal

Flask API backend
  - REST endpoints
  - auth and role permissions
  - business logic
  - membership status calculations
  - check-in validation

PostgreSQL database
  - members
  - users
  - plans
  - subscriptions
  - payments
  - attendance
  - exercises
  - classes
```

### Backend Responsibility

The Flask API should own the business rules, including:

- Is this membership active?
- How many days remain?
- Can this member check in?
- What is the current subscription?
- Has the membership expired?
- What payments belong to this member?

The Next.js frontend should focus on:

- User interface
- Forms
- Tables
- Dashboards
- Portal pages
- Calling the API through TanStack Query

### REST First

Use REST for the MVP instead of GraphQL.

The MVP endpoints are straightforward and REST will be faster to build, easier to debug, and easier to test.

Example API shape:

```txt
POST   /auth/login

GET    /members
POST   /members
GET    /members/:id
PATCH  /members/:id

GET    /plans
POST   /plans
PATCH  /plans/:id

POST   /members/:id/subscriptions
POST   /members/:id/payments

POST   /check-ins

GET    /dashboard/attendance

GET    /exercises
POST   /exercises

GET    /classes
POST   /classes
```

### Project Structure

Use a monorepo-style structure:

```txt
SiteFitnessWebApp/
  frontend/
  backend/
  README.md
  docker-compose.yml
```

### Frontend Setup

The frontend should include:

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Basic admin layout
- Basic member portal layout
- API client helper

Initial routes:

```txt
/login
/admin
/admin/members
/admin/plans
/admin/check-ins
/admin/attendance
/member
/member/attendance
```

### Backend Setup

The backend should include:

- Flask
- SQLAlchemy
- Flask-Migrate / Alembic
- PostgreSQL database connection
- Flask-CORS
- Environment variable support
- Basic health endpoint

Initial backend structure:

```txt
backend/
  app/
    __init__.py
    config.py
    extensions.py
    models/
    routes/
    services/
  migrations/
  requirements.txt
  run.py
```

### Database Setup

Use PostgreSQL through Docker Compose for local development.

The first database setup should include:

- Local PostgreSQL container
- Database name
- Database user
- Database password
- Persistent database volume
- Backend environment variable for database URL

Example environment variable:

```txt
DATABASE_URL=postgresql://sitefitness:sitefitness@localhost:5432/sitefitness
```

### First Connection Test

The first setup milestone is complete when:

- PostgreSQL runs locally
- Flask connects to PostgreSQL
- Flask exposes a `/health` endpoint
- Next.js runs locally
- Next.js calls the Flask `/health` endpoint
- The frontend displays a successful API connection message

Example response from Flask:

```json
{
  "status": "ok",
  "database": "connected"
}
```

### Definition Of Done For Step 1

Step 1 is finished when the project has:

- `frontend/` Next.js app
- `backend/` Flask API
- `docker-compose.yml` for PostgreSQL
- Working environment variables
- Working backend health route
- Working frontend-to-backend API call
- README instructions for running everything locally

### Local Development Commands

#### 1. Start PostgreSQL

PostgreSQL is configured in `docker-compose.yml`.

```bash
docker compose up -d postgres
```

If Docker is not installed yet, install Docker Desktop first or run PostgreSQL locally with the same credentials:

```txt
Database: sitefitness
User: sitefitness
Password: sitefitness
Port: 5432
```

#### 2. Start The Flask API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

The API runs on:

```txt
http://localhost:5001/api
```

Health check:

```txt
http://localhost:5001/api/health
```

Expected response when PostgreSQL is connected:

```json
{
  "status": "ok",
  "database": "connected"
}
```

#### 3. Start The Next.js Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The frontend runs on:

```txt
http://localhost:3000
```

The home page calls the Flask `/health` endpoint through TanStack Query and displays the API/database connection status.

### Current Step 1 Scaffold

The first phase now includes:

- Root `docker-compose.yml` for PostgreSQL
- `backend/` Flask API
- Backend configuration through `.env`
- SQLAlchemy and Flask-Migrate setup
- `/api/health` backend route
- `frontend/` Next.js app
- shadcn/ui initialization
- TanStack Query provider
- Frontend API helper
- Home page health-check panel
- Placeholder routes for:
  - `/login`
  - `/admin`
  - `/admin/members`
  - `/admin/plans`
  - `/admin/check-ins`
  - `/admin/attendance`
  - `/member`
  - `/member/attendance`

## Step 2: Authentication And Roles

Authentication should be split by user type because staff/admin authentication and member authentication have different risks.

The Step 2 implementation now includes:

- `users` table
- `members` table
- `member_invites` table
- Email/password login
- HttpOnly JWT cookie sessions
- `/api/auth/login`
- `/api/auth/logout`
- `/api/auth/me`
- `/api/auth/member-invites`
- `/api/auth/member-invites/accept`
- Owner seed CLI command
- Protected admin routes
- Protected member routes
- Member invite acceptance page at `/register?token=...`

### Admin And Staff Authentication

For admin and staff users, use email and password.

Do not use one shared admin username and password. Each staff person should have their own account so the system can track who created members, accepted payments, edited plans, or checked members in.

Admin and staff users should have:

- Email
- Password hash
- Role
- Active/inactive status
- Last login date
- Created by owner/admin

Recommended roles:

- `owner`
- `staff`
- `trainer`
- `member`

For the MVP, use this flow:

```txt
Owner creates staff account
Staff receives invite email
Staff sets their password
Staff logs in with email and password
```

Security basics to include from the start:

- Passwords hashed with bcrypt or argon2
- JWT or secure session cookies
- Role-based permissions
- Owner account seeded manually during setup
- Password reset by email
- No public staff registration page

### Member Authentication

Members should not freely create accounts from a public registration page. A member account should start from the gym staff creating the member profile.

Recommended member flow:

```txt
Staff creates member profile
Staff enters member email
System sends invite email
Member clicks invite link
Member creates password
Member can access the member portal
```

This keeps the member portal limited to real gym members.

### Google Login

Do not make Google login the only authentication method for the MVP.

Some members may not use Gmail, may share emails, may forget which Google account they used, or may not want to use Google login.

Recommended approach:

```txt
MVP:
- Admin/staff: email and password
- Members: invite email and create password

Later:
- Add Google login as an optional sign-in method
```

### Suggested Auth Data Model

Use one `users` table for login accounts:

```txt
users
- id
- email
- password_hash
- role
- status
- email_verified_at
- last_login_at
- created_at
- updated_at
```

Then link gym members to users:

```txt
members
- id
- user_id
- full_name
- dni
- phone
- date_of_birth
- address
- emergency_contact
- medical_notes
- photo_url
- join_date
- status
```

A staff member has a `users` record but no `members` profile.

A gym member has both:

```txt
users record = login credentials
members record = gym profile
```

### Recommended Build Order

Build authentication in this order:

1. Admin owner seed account
2. Admin/staff login with email and password
3. Protected admin routes
4. Roles: owner, staff, trainer, member
5. Staff creates member without login credentials
6. Staff sends member invite
7. Member accepts invite and creates password
8. Protected member portal

This gives the system control, security, and a clean member experience without making the MVP too complex.

### Step 2 Local Setup

After PostgreSQL is running, apply the auth migration:

```bash
cd backend
source .venv/bin/activate
flask --app run db upgrade
```

Create the first owner account:

```bash
flask --app run seed-owner --email owner@example.com
```

The command will securely prompt for a password.

Then start the backend:

```bash
python run.py
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Sign in at:

```txt
http://localhost:3000/login
```

Admin routes are protected for:

- `owner`
- `staff`
- `trainer`

Member routes are protected for:

- `member`

### Member Invite Flow

For now, member invites return an invite URL directly from the API. Later, this URL should be sent by email.

The admin members page now supports this flow at:

```txt
http://localhost:3000/admin/members
```

Staff can:

- Register a member profile
- Add DNI, phone, email, dates, address, emergency contact, and medical notes
- Generate a member portal invite when an email is present
- Copy the invite URL
- View recent members

Create an invite as an authenticated owner/staff/trainer:

```txt
POST /api/auth/member-invites
```

Example body:

```json
{
  "email": "member@example.com"
}
```

Example response:

```json
{
  "invite": {
    "id": 1,
    "memberId": null,
    "email": "member@example.com",
    "role": "member",
    "expiresAt": "2026-06-07T00:00:00",
    "acceptedAt": null
  },
  "inviteUrl": "http://localhost:3000/register?token=..."
}
```

The member opens the invite URL, creates a password, and then signs in from `/login`.
