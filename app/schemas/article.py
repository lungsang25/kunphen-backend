from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ArticleBase(BaseModel):
    title: str
    slug: str
    category: str = ""
    author: str = ""
    excerpt: str = ""
    content: str = ""
    image_url: str = ""
    published_at: datetime | None = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    category: str | None = None
    author: str | None = None
    excerpt: str | None = None
    content: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None


class ArticleListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    category: str
    author: str
    excerpt: str
    image_url: str
    published_at: datetime


class ArticleOut(ArticleListOut):
    content: str
    created_at: datetime
    updated_at: datetime
