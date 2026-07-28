from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article
from app.schemas.article import ArticleCreate, ArticleOut, ArticleUpdate
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/articles",
    tags=["cms-articles"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.scalars(select(Article).order_by(Article.published_at.desc())).all()


@router.post("", response_model=ArticleOut, status_code=201)
def create_article(body: ArticleCreate, db: Session = Depends(get_db)):
    if db.scalars(select(Article).where(Article.slug == body.slug)).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    data = body.model_dump()
    if data.get("published_at") is None:
        data.pop("published_at")
    article = Article(**data)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{article_id}", response_model=ArticleOut)
def update_article(
    article_id: int, body: ArticleUpdate, db: Session = Depends(get_db)
):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    updates = body.model_dump(exclude_unset=True)
    if "slug" in updates and updates["slug"] != article.slug:
        if db.scalars(select(Article).where(Article.slug == updates["slug"])).first():
            raise HTTPException(status_code=409, detail="Slug already exists")
    for field, value in updates.items():
        setattr(article, field, value)
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=204)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
