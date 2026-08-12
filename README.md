# Kunphen Backend

FastAPI backend for the Kunphen website — public APIs for Medicines, Articles, and Gallery, plus JWT-protected CMS endpoints with Google sign-in and S3 presigned image uploads.

## Stack

- FastAPI + SQLAlchemy 2 + Alembic
- PostgreSQL
- AWS S3 (presigned PUT URLs for direct browser uploads)
- Google OAuth (email allowlist) + JWT sessions for CMS

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in values
createdb kunphen       # or create the DB however you manage Postgres
alembic upgrade head
python -m scripts.seed # optional: seed mock data
python -m scripts.seed_hero_slides  # optional: push the website's bundled hero images to S3
```

## Run

```bash
cd /home/lungsang/Project/kunphen/kunphen-backend

source .venv/bin/activate
uvicorn app.main:app --port 8000
```

API docs: http://localhost:8000/docs

## Endpoints

### Public (no auth)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/medicines` | List medicines |
| GET | `/api/medicines/{id}` | Single medicine |
| GET | `/api/articles` | List articles (`?category=`, `?search=`) |
| GET | `/api/articles/{slug}` | Full article by slug |
| GET | `/api/gallery` | List gallery images |
| GET | `/api/hero-slides` | List active homepage hero slides |

### CMS (Bearer JWT required)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/cms/auth/google` | Exchange Google ID token for JWT |
| * | `/api/cms/medicines...` | Full CRUD |
| * | `/api/cms/articles...` | Full CRUD |
| * | `/api/cms/gallery...` | Full CRUD |
| * | `/api/cms/hero-slides...` | Full CRUD |
| PUT | `/api/cms/hero-slides/reorder` | Set slide order from a list of ids |
| POST | `/api/cms/uploads/presign` | Get S3 presigned PUT URL |
