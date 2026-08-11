from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article
from app.schemas.article import ArticleListOut, ArticleOut

router = APIRouter(prefix="/articles", tags=["public-articles"])


@router.get("", response_model=list[ArticleListOut])
def list_articles(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Article).order_by(Article.published_at.desc())
    if category and category.lower() != "all":
        stmt = stmt.where(Article.category == category)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Article.title.ilike(pattern), Article.excerpt.ilike(pattern))
        )
    return db.scalars(stmt).all()


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    article = db.scalars(select(Article).where(Article.slug == slug)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
