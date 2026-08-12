from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.cms import articles as cms_articles
from app.routers.cms import auth as cms_auth
from app.routers.cms import gallery as cms_gallery
from app.routers.cms import hero_slides as cms_hero_slides
from app.routers.cms import medicines as cms_medicines
from app.routers.cms import uploads as cms_uploads
# NB: this package must not be named "public" — Vercel strips directories with that
# name from the function bundle (it treats them as static assets), which makes the
# import fail at runtime in production while working fine locally.
from app.routers.public_api import articles, gallery, hero_slides, medicines

app = FastAPI(title="Kunphen API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(medicines.router, prefix="/api")
app.include_router(articles.router, prefix="/api")
app.include_router(gallery.router, prefix="/api")
app.include_router(hero_slides.router, prefix="/api")

app.include_router(cms_auth.router, prefix="/api/cms")
app.include_router(cms_medicines.router, prefix="/api/cms")
app.include_router(cms_articles.router, prefix="/api/cms")
app.include_router(cms_gallery.router, prefix="/api/cms")
app.include_router(cms_hero_slides.router, prefix="/api/cms")
app.include_router(cms_uploads.router, prefix="/api/cms")


@app.get("/health")
def health():
    return {"status": "ok"}
